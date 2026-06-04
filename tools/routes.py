"""
tools/get_route.py
==================
Tool: get_route

Tính đường đi từ điểm A đến điểm B: khoảng cách, thời gian di chuyển
và các bước chỉ đường chi tiết.

Nguồn dữ liệu : OSRM public server (router.project-osrm.org)
Quota          : Không giới hạn — hoàn toàn miễn phí, không cần API key
Rate limit     : Không gọi quá 1 request/giây với public server
Dữ liệu bản đồ : OpenStreetMap

Phương tiện hỗ trợ
------------------
- ``driving``  : xe máy / ô tô
- ``walking``  : đi bộ
- ``cycling``  : xe đạp

Lưu ý tọa độ
-------------
OSRM dùng định dạng ``lng,lat`` (kinh độ trước, vĩ độ sau) —
ngược với Google Maps. Hàm này xử lý đúng thứ tự tự động.

Tham số tool cho Claude
-----------------------
origin_lat : float  — vĩ độ điểm xuất phát
origin_lng : float  — kinh độ điểm xuất phát
dest_lat   : float  — vĩ độ điểm đến
dest_lng   : float  — kinh độ điểm đến
mode       : str    — phương tiện ("driving" | "walking" | "cycling")

Trả về
------
dict
    Thành công::

        {
            "distance_km":  float,        # khoảng cách (km)
            "duration_min": int,          # thời gian (phút)
            "mode":         str,          # phương tiện đã dùng
            "steps": [
                {
                    "instruction": str,   # tên đường hoặc hành động
                    "distance_m":  int,   # khoảng cách bước này (m)
                },
                ...                       # tối đa 8 bước
            ],
        }

    Thất bại: ``{"error": str}``

Ví dụ
-----
>>> result = get_route(
...     origin_lat=21.0267, origin_lng=105.8357,   # Văn Miếu
...     dest_lat=21.0285,   dest_lng=105.8542,      # Hồ Hoàn Kiếm
...     mode="walking",
... )
>>> print(result["duration_min"])
25
"""

import httpx

OSRM_BASE_URL = "https://router.project-osrm.org/route/v1"

TOOL_DEFINITION = {
    "name": "get_route",
    "description": (
        "Tính đường đi từ điểm A đến điểm B. "
        "Trả về khoảng cách (km), thời gian (phút) và các bước chỉ đường. "
        "Dùng tọa độ GPS — lấy từ trường gps trong kết quả search_places "
        "hoặc dùng tọa độ mặc định đã biết."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "origin_lat": {
                "type": "number",
                "description": "Vĩ độ điểm xuất phát.",
            },
            "origin_lng": {
                "type": "number",
                "description": "Kinh độ điểm xuất phát.",
            },
            "dest_lat": {
                "type": "number",
                "description": "Vĩ độ điểm đến.",
            },
            "dest_lng": {
                "type": "number",
                "description": "Kinh độ điểm đến.",
            },
            "mode": {
                "type": "string",
                "enum": ["driving", "walking", "cycling"],
                "description": (
                    "Phương tiện di chuyển. "
                    "driving = xe máy/ô tô, walking = đi bộ, cycling = xe đạp. "
                    "Mặc định: walking."
                ),
            },
        },
        "required": ["origin_lat", "origin_lng", "dest_lat", "dest_lng"],
    },
}

_MANEUVER_VI = {
    "turn":           "Rẽ",
    "new name":       "Tiếp tục",
    "depart":         "Xuất phát",
    "arrive":         "Đã đến nơi",
    "merge":          "Nhập làn",
    "on ramp":        "Lên đường nhánh",
    "off ramp":       "Xuống đường nhánh",
    "fork":           "Đi theo nhánh",
    "end of road":    "Cuối đường",
    "continue":       "Đi thẳng",
    "roundabout":     "Vòng xuyến",
    "rotary":         "Vòng xuyến lớn",
    "roundabout turn":"Rẽ tại vòng xuyến",
    "notification":   "Lưu ý",
    "use lane":       "Giữ làn",
}


def _maneuver_to_vi(maneuver_type: str) -> str:
    """Chuyển maneuver type tiếng Anh sang tiếng Việt."""
    return _MANEUVER_VI.get(maneuver_type, maneuver_type.capitalize())


def get_route(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    mode: str = "walking",
    *,
    max_steps: int = 8,
    timeout: float = 15.0,
) -> dict:
    """Tính đường đi giữa hai tọa độ GPS qua OSRM.

    Parameters
    ----------
    origin_lat : float
        Vĩ độ điểm xuất phát.
    origin_lng : float
        Kinh độ điểm xuất phát.
    dest_lat : float
        Vĩ độ điểm đến.
    dest_lng : float
        Kinh độ điểm đến.
    mode : str, optional
        Phương tiện di chuyển: ``"driving"``, ``"walking"``, ``"cycling"``.
        Mặc định ``"walking"``.
    max_steps : int, optional
        Số bước chỉ đường tối đa trả về. Mặc định 8.
    timeout : float, optional
        Timeout HTTP tính bằng giây. Mặc định 15.0.

    Returns
    -------
    dict
        Kết quả route nếu thành công,
        ``{"error": str}`` nếu thất bại.

    Raises
    ------
    ValueError
        Nếu ``mode`` không hợp lệ.
    httpx.TimeoutException
        Nếu OSRM không phản hồi trong thời gian timeout.
    httpx.HTTPError
        Nếu có lỗi kết nối mạng.
    """
    valid_modes = {"driving", "walking", "cycling"}
    if mode not in valid_modes:
        raise ValueError(f"mode phải là một trong {valid_modes}, nhận được: {mode!r}")

    # OSRM dùng định dạng lng,lat (kinh độ trước)
    coords = f"{origin_lng},{origin_lat};{dest_lng},{dest_lat}"
    url = f"{OSRM_BASE_URL}/{mode}/{coords}"

    with httpx.Client(timeout=timeout) as client:
        response = client.get(url, params={"steps": "true", "overview": "false"})
        response.raise_for_status()

    data = response.json()

    if data.get("code") != "Ok":
        return {"error": f"OSRM lỗi: {data.get('code', 'Unknown')} — {data.get('message', '')}"}

    route = data["routes"][0]
    raw_steps = route["legs"][0]["steps"]

    steps = [
        {
            "instruction": step.get("name") or _maneuver_to_vi(step["maneuver"]["type"]),
            "distance_m":  round(step["distance"]),
        }
        for step in raw_steps
        if step.get("name") or step["maneuver"]["type"] not in ("depart",)
    ][:max_steps]

    return {
        "distance_km":  round(route["distance"] / 1000, 1),
        "duration_min": round(route["duration"] / 60),
        "mode":         mode,
        "steps":        steps,
    }