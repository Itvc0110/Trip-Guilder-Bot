"""Tool route_advice.

Tối ưu hóa tuyến đi từ danh sách địa điểm:
1. Nhận input: danh sách địa điểm từ place discovery tool
2. Geocoding: chuyển tên địa điểm thành tọa độ (lat/lng)
3. Route Optimization: sắp xếp lại thứ tự để tối thiểu khoảng cách
4. AI Itinerary: dùng LLM để tạo lịch trình chi tiết
5. Output: JSON cho map visualization API
"""

from __future__ import annotations

import json
from math import radians, cos, sin, asin, sqrt
from typing import Any

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Tính khoảng cách giữa hai điểm (km)."""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # km
    return c * r


def geocode_places(places: list[str]) -> list[dict]:
    """Geocoding: chuyển tên địa điểm thành tọa độ."""
    geolocator = Nominatim(user_agent="trip_guilder_bot")
    geocoded = []

    for place in places:
        try:
            location = geolocator.geocode(place, timeout=5)
            if location:
                geocoded.append({
                    "name": place,
                    "lat": location.latitude,
                    "lng": location.longitude,
                })
        except (GeocoderTimedOut, GeocoderUnavailable):
            pass

    return geocoded


def optimize_route(geocoded_places: list[dict]) -> list[dict]:
    """Route Optimization: sắp xếp lại thứ tự bằng nearest-neighbor."""
    if not geocoded_places or len(geocoded_places) < 2:
        return geocoded_places

    # Nearest-neighbor algorithm
    route = []
    remaining = geocoded_places.copy()
    current = remaining.pop(0)
    route.append(current)

    while remaining:
        nearest = min(
            remaining,
            key=lambda p: haversine(
                current["lat"], current["lng"],
                p["lat"], p["lng"]
            )
        )
        remaining.remove(nearest)
        route.append(nearest)
        current = nearest

    # Gán order
    for i, place in enumerate(route, 1):
        place["order"] = i

    return route


def generate_itinerary(
    optimized_route: list[dict],
    openrouter_client: Any = None,
    settings: Any = None
) -> tuple[list[dict], str]:
    """AI Itinerary: tạo lịch trình chi tiết dựa trên tọa độ. Returns (itinerary, status)."""
    if not optimized_route:
        return [], "no_route"

    # Nếu không có LLM, trả về basic itinerary
    if openrouter_client is None or settings is None or not settings.has_api_key:
        return _generate_basic_itinerary(optimized_route), "no_api_key"

    # Dùng LLM
    places_info = "\n".join([
        f"{p['order']}. {p['name']} (lat={p['lat']:.4f}, lng={p['lng']:.4f})"
        for p in optimized_route
    ])

    prompt = f"""Tạo lịch trình chi tiết cho các địa điểm này (đã sắp xếp theo tuyến tối ưu):

{places_info}

Yêu cầu:
- Giờ bắt đầu từ 08:00
- Mỗi địa điểm 60-90 phút
- Thêm ăn trưa nếu cần
- Format: JSON array có trường: time (HH:MM), place, activity, duration_minutes

CHỈ trả JSON array, không giải thích."""

    try:
        response = openrouter_client.chat(
            model=settings.planner_model,
            messages=[
                {
                    "role": "system",
                    "content": "Tạo lịch trình du lịch chi tiết. Trả JSON hợp lệ."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        parsed = json.loads(response)
        # Handle both direct array and wrapped in "itinerary" key
        itinerary = parsed if isinstance(parsed, list) else parsed.get("itinerary", [])
        return (itinerary if itinerary else _generate_basic_itinerary(optimized_route), "llm_success")
    except Exception as e:
        return _generate_basic_itinerary(optimized_route), f"llm_error: {str(e)}"


def _generate_basic_itinerary(optimized_route: list[dict]) -> list[dict]:
    """Basic itinerary nếu không có LLM."""
    itinerary = []
    current_time = 8 * 60  # 08:00 in minutes

    for i, place in enumerate(optimized_route):
        hours = current_time // 60
        minutes = current_time % 60
        time_str = f"{hours:02d}:{minutes:02d}"

        itinerary.append({
            "time": time_str,
            "place": place["name"],
            "activity": "Tham quan",
            "duration_minutes": 90
        })
        current_time += 90

        # Ăn trưa ở điểm 2
        if i == 1 and len(optimized_route) > 2:
            itinerary.append({
                "time": f"{(current_time // 60):02d}:{(current_time % 60):02d}",
                "place": "Nhà hàng địa phương",
                "activity": "Ăn trưa",
                "duration_minutes": 60
            })
            current_time += 60

    return itinerary


def route_advice(user_request: str, openrouter_client: Any = None, settings: Any = None) -> dict:
    """
    Input: danh sách địa điểm (từ place discovery tool)
    Output: JSON optimized route + itinerary cho map visualization
    """
    try:
        # Parse input - có thể là JSON array hoặc string chứa danh sách địa điểm
        import re
        places = []

        # Thử tìm danh sách trong ngoặc vuông [...]
        match = re.search(r'\[([^\]]+)\]', user_request)
        if match:
            # Phân tách theo dấu phẩy
            places = [p.strip() for p in match.group(1).split(',')]
        else:
            # Thử parse JSON
            try:
                places = json.loads(user_request)
            except:
                pass

        if not places:
            return {
                "tool_name": "route_advice",
                "status": "error",
                "summary": "Input không hợp lệ. Cần danh sách địa điểm.",
                "verified": False,
            }

        # Step 1: Geocoding
        geocoded_places = geocode_places(places)

        if not geocoded_places:
            return {
                "tool_name": "route_advice",
                "status": "error",
                "summary": f"Không tìm tọa độ cho các địa điểm: {places}",
                "verified": False,
            }

        # Step 2: Route Optimization
        optimized_route = optimize_route(geocoded_places)

        # Step 3: AI Itinerary
        itinerary, itinerary_status = generate_itinerary(optimized_route, openrouter_client, settings)

        # Build output JSON (specification format)
        output_json = {
            "optimized_route": optimized_route,
            "itinerary": itinerary
        }

        return {
            "tool_name": "route_advice",
            "status": "success",
            "summary": f"Đã tối ưu hóa tuyến cho {len(optimized_route)} địa điểm (itinerary: {itinerary_status})",
            "output": output_json,
            "itinerary_status": itinerary_status,
            "verified": True,
        }

    except Exception as e:
        return {
            "tool_name": "route_advice",
            "status": "error",
            "summary": f"Lỗi: {str(e)}",
            "verified": False,
        }
