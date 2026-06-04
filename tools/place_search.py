"""
tools/search_places.py
======================
Tool: search_places

Tìm kiếm địa điểm (nhà hàng, cafe, khách sạn, điểm tham quan, ...)
trên Google Maps thông qua SerpAPI.

Nguồn dữ liệu : SerpAPI — Google Maps engine (type=search)
Quota          : 1 SerpAPI call / lần gọi
Giới hạn kết quả : tối đa 6 địa điểm mỗi lần tìm kiếm

Tham số tool cho Claude
-----------------------
query : str
    Từ khóa tìm kiếm. Nên bao gồm loại hình và khu vực,
    ví dụ: "phở bò Hoàn Kiếm", "cafe view đẹp Tây Hồ".
lat   : float
    Vĩ độ trung tâm vùng tìm kiếm.
lng   : float
    Kinh độ trung tâm vùng tìm kiếm.
zoom  : int, optional
    Mức zoom bản đồ (12–16). Zoom thấp = vùng rộng hơn.
    Mặc định: 14.

Trả về
------
dict
    {"places": List[PlaceItem]} nếu thành công.
    {"error": str}              nếu thất bại.

    PlaceItem gồm:
        title      : tên địa điểm
        address    : địa chỉ đầy đủ
        rating     : điểm đánh giá (float, 1.0–5.0)
        reviews    : số lượng đánh giá (int)
        price      : mức giá ("$", "$$", "$$$", "$$$$")
        type       : loại hình (str)
        open_state : trạng thái mở cửa ("Open", "Closed", ...)
        phone      : số điện thoại
        data_id    : ID dùng cho get_place_details
        gps        : {"latitude": float, "longitude": float}

Ví dụ
-----
>>> result = search_places(
...     query="phở bò Hoàn Kiếm",
...     lat=21.0285,
...     lng=105.8542,
... )
>>> result["places"][0]["title"]
'Phở Thìn'
"""

import httpx


# Schema định nghĩa tool cho Anthropic API
TOOL_DEFINITION = {
    "name": "search_places",
    "description": (
        "Tìm nhà hàng, cafe, điểm tham quan, khách sạn hoặc bất kỳ địa điểm nào "
        "trên Google Maps. Trả về danh sách địa điểm với tên, địa chỉ, rating, "
        "giờ mở cửa và data_id để tra chi tiết."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "Từ khóa tìm kiếm, nên kèm khu vực. "
                    "Ví dụ: 'phở bò Hoàn Kiếm', 'cafe Tây Hồ', 'bảo tàng Hà Nội'."
                ),
            },
            "lat": {
                "type": "number",
                "description": "Vĩ độ trung tâm vùng tìm kiếm.",
            },
            "lng": {
                "type": "number",
                "description": "Kinh độ trung tâm vùng tìm kiếm.",
            },
            "zoom": {
                "type": "number",
                "description": "Mức zoom bản đồ (12–16). Mặc định 14.",
            },
        },
        "required": ["query", "lat", "lng"],
    },
}


def search_places(
    query: str,
    lat: float,
    lng: float,
    zoom: int = 14,
    *,
    api_key: str,
    max_results: int = 6,
    timeout: float = 15.0,
) -> dict:
    """Tìm kiếm địa điểm trên Google Maps qua SerpAPI.

    Parameters
    ----------
    query : str
        Từ khóa tìm kiếm (tên loại hình + khu vực).
    lat : float
        Vĩ độ trung tâm vùng tìm kiếm.
    lng : float
        Kinh độ trung tâm vùng tìm kiếm.
    zoom : int, optional
        Mức zoom bản đồ (12–16). Mặc định 14.
    api_key : str
        SerpAPI private key. Truyền qua keyword argument.
    max_results : int, optional
        Số kết quả tối đa trả về. Mặc định 6.
    timeout : float, optional
        Timeout HTTP tính bằng giây. Mặc định 15.0.

    Returns
    -------
    dict
        {"places": list[dict]} nếu thành công,
        {"error": str} nếu thất bại.

    Raises
    ------
    httpx.TimeoutException
        Nếu SerpAPI không phản hồi trong thời gian timeout.
    httpx.HTTPError
        Nếu có lỗi kết nối mạng.
    """
    ll = f"@{lat},{lng},{zoom}z"

    with httpx.Client(timeout=timeout) as client:
        response = client.get(
            "https://serpapi.com/search",
            params={
                "engine":  "google_maps",
                "q":       query,
                "ll":      ll,
                "type":    "search",
                "hl":      "vi",
                "api_key": api_key,
            },
        )
        response.raise_for_status()

    data = response.json()

    if "error" in data:
        return {"error": data["error"]}

    raw_places = data.get("local_results") or []
    places = [
        {
            "title":      place.get("title"),
            "address":    place.get("address"),
            "rating":     place.get("rating"),
            "reviews":    place.get("reviews"),
            "price":      place.get("price"),
            "type":       place.get("type"),
            "open_state": place.get("open_state"),
            "phone":      place.get("phone"),
            "data_id":    place.get("data_id"),
            "gps":        place.get("gps_coordinates"),
        }
        for place in raw_places[:max_results]
    ]

    return {"places": places}