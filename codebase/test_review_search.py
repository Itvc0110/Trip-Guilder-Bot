"""
Test luồng: search_places → get_place_reviews

Bước 1: search_places lấy danh sách địa điểm + data_id
Bước 2: get_place_reviews dùng data_id để lấy review thực tế
"""

from dotenv import load_dotenv
from tools.place_search import search_places
from tools.review_search import get_place_reviews, get_reviews_for_places
import json

load_dotenv()


def test_single_review():
    """Test lấy review cho 1 địa điểm cụ thể từ kết quả search_places."""
    print("=" * 60)
    print("Bước 1: search_places")
    print("=" * 60)

    search_result = search_places("quán cà phê view đẹp ở Hà Nội")
    print(f"Status: {search_result['status']}")
    print(f"Summary: {search_result['summary']}")

    if search_result["status"] != "success" or not search_result["places"]:
        print("Không có kết quả.")
        return

    # Lấy địa điểm đầu tiên
    first_place = search_result["places"][0]
    print(f"\nĐịa điểm đầu tiên: {first_place['title']}")
    print(f"Địa chỉ: {first_place['address']}")
    print(f"data_id: {first_place['data_id']}")

    print("\n" + "=" * 60)
    print("Bước 2: get_place_reviews")
    print("=" * 60)

    review_result = get_place_reviews(first_place["data_id"], max_best=5)
    print(json.dumps(review_result, indent=2, ensure_ascii=False))


def test_batch_reviews():
    """Test lấy review cho toàn bộ địa điểm từ kết quả search."""
    print("\n" + "=" * 60)
    print("Test batch: get_reviews_for_places")
    print("=" * 60)

    search_result = search_places("nhà hàng hải sản ngon ở Đà Nẵng")
    if search_result["status"] != "success":
        print("Không có kết quả.")
        return

    # Lấy review cho 2 địa điểm đầu tiên, mỗi nơi 3 review
    top_2_places = search_result["places"][:2]
    all_reviews = get_reviews_for_places(top_2_places, max_best_per_place=2, max_worst_per_place=1)

    for r in all_reviews:
        print(f"\n--- {r.get('place_title')} ---")
        print(f"Status: {r['status']}, Summary: {r['summary']}")
        for review in r.get("reviews", []):
            print(f"  ⭐ {review['rating']} | {review['user']} | {review['date']}")
            print(f"     {review['snippet'][:100] if review['snippet'] else 'N/A'}...")


if __name__ == "__main__":
    test_single_review()
    test_batch_reviews()
