"""Tool route_advice - Geocode places and output JSON for map visualization."""

from __future__ import annotations

import json
import re

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable


def geocode_places(places: list[str]) -> list[dict]:
    """Chuyển tên địa điểm thành tọa độ (lat, lng)."""
    geolocator = Nominatim(user_agent="trip_guilder_bot")
    geocoded = []

    for i, place in enumerate(places, 1):
        try:
            location = geolocator.geocode(place, timeout=5)
            if location:
                geocoded.append({
                    "name": place,
                    "lat": location.latitude,
                    "lng": location.longitude,
                    "order": i
                })
        except (GeocoderTimedOut, GeocoderUnavailable):
            pass

    return geocoded


def route_advice(user_request: str) -> dict:
    """
    Input: danh sách địa điểm (list hoặc JSON array)
    Output: JSON với tọa độ cho map visualization
    """
    try:
        places = []

        # Parse list format [place1, place2, ...]
        match = re.search(r'\[([^\]]+)\]', user_request)
        if match:
            places = [p.strip() for p in match.group(1).split(',')]
        else:
            # Try JSON array
            try:
                places = json.loads(user_request)
                if isinstance(places, dict):
                    places = places.get('places', [])
            except:
                pass

        if not places:
            return {
                "tool_name": "route_advice",
                "status": "error",
                "summary": "Input không hợp lệ. Cần danh sách địa điểm.",
                "verified": False,
            }

        geocoded = geocode_places(places)

        if not geocoded:
            return {
                "tool_name": "route_advice",
                "status": "error",
                "summary": f"Không tìm tọa độ cho các địa điểm: {places}",
                "verified": False,
            }

        output_json = {"optimized_route": geocoded}

        return {
            "tool_name": "route_advice",
            "status": "success",
            "summary": f"Đã geocode {len(geocoded)}/{len(places)} địa điểm",
            "output": output_json,
            "verified": True,
        }

    except Exception as e:
        return {
            "tool_name": "route_advice",
            "status": "error",
            "summary": f"Lỗi: {str(e)}",
            "verified": False,
        }
