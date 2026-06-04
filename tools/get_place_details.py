"""
tools/get_place_details.py
==========================
Tool: get_place_details

Lấy thông tin chi tiết của một địa điểm cụ thể trên Google Maps:
giờ mở cửa từng ngày, số điện thoại, website, mô tả, reviews.

Nguồn dữ liệu : SerpAPI — Google Maps engine (type=place via data_id)
Quota          : 1 SerpAPI call / lần gọi
Điều kiện      : cần data_id từ kết quả search_places trước đó

Workflow điển hình
------------------
1. Gọi search_places → nhận danh sách địa điểm + data_id
2. User chọn 1 địa điểm quan tâm
3. Gọi get_place_details(data_id=...) → nhận thông tin đầy đủ

Tham số tool cho Claude
-----------------------
data_id : str
    ID định danh địa điểm trên Google Maps.
    Lấy từ trường ``data_id`` trong kết quả search_places.

Trả về
------
dict
    Thành công::

        {
            "title":       str,          # tên địa điểm
            "address":     str,          # địa chỉ đầy đủ
            "rating":      float,        # điểm đánh giá (1.0–5.0)
            "reviews":     int,          # số lượng đánh giá
            "phone":       str,          # số điện thoại
            "website":     str,          # URL website
            "description": str,          # mô tả ngắn
            "hours":       list[dict],   # giờ mở cửa từng ngày
            "price":       str,          # mức giá
        }

    Thất bại: ``{"error": str}``

Ví dụ
-----
>>> result = get_place_details(
...     data_id="0x3135ab...:0x4a2b...",
...     api_key="YOUR_KEY",
... )
>>> result["hours"]
[{"monday": "7:00 AM – 10:00 PM"}, ...]
"""

import httpx


TOOL_DEFINITION = {
    "name": "get_place_details",
    "description": (
        "Lấy thông tin chi tiết của một địa điểm: giờ mở cửa từng ngày, "
        "số điện thoại, website, mô tả, reviews. "
        "Chỉ dùng sau khi đã có data_id từ search_places."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "data_id": {
                "type": "string",
                "description": (
                    "data_id của địa điểm, lấy từ kết quả search_places. "
                    "Dạng chuỗi hex, ví dụ: '0x3135ab12:0x4a2bcd'."
                ),
            },
        },
        "required": ["data_id"],
    },
}


def get_place_details(
    data_id: str,
    *,
    api_key: str,
    timeout: float = 15.0,
) -> dict:
    """Lấy thông tin chi tiết một địa điểm từ Google Maps qua SerpAPI.

    Parameters
    ----------
    data_id : str
        Google Maps data_id của địa điểm.
        Lấy từ trường ``data_id`` trong kết quả :func:`search_places`.
    api_key : str
        SerpAPI private key. Truyền qua keyword argument.
    timeout : float, optional
        Timeout HTTP tính bằng giây. Mặc định 15.0.

    Returns
    -------
    dict
        Chi tiết địa điểm nếu thành công,
        ``{"error": str}`` nếu thất bại.

    Raises
    ------
    httpx.TimeoutException
        Nếu SerpAPI không phản hồi trong thời gian timeout.
    httpx.HTTPError
        Nếu có lỗi kết nối mạng.
    """
    with httpx.Client(timeout=timeout) as client:
        response = client.get(
            "https://serpapi.com/search",
            params={
                "engine":  "google_maps",
                "data_id": data_id,
                "hl":      "vi",
                "api_key": api_key,
            },
        )
        response.raise_for_status()

    data = response.json()

    if "error" in data:
        return {"error": data["error"]}

    place = data.get("place_results", {})

    return {
        "title":       place.get("title"),
        "address":     place.get("address"),
        "rating":      place.get("rating"),
        "reviews":     place.get("reviews"),
        "phone":       place.get("phone"),
        "website":     place.get("website"),
        "description": place.get("description"),
        "hours":       place.get("hours"),
        "price":       place.get("price"),
    }