import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from tools.place_search import search_places
from tools.review_search import search_reviews
from tools.filter_review import filter_reviews
from tools.routes import route_advice

def demo():
    print("=" * 60)
    print("DEMO: search_places")
    print("=" * 60)
    places_result = search_places("cafe view đẹp ở Tây Hồ Hà Nội")
    print("Status:", places_result.get("status"))
    print("Summary:", places_result.get("summary"))
    if places_result.get("places"):
        print("First Place found:")
        print(json.dumps(places_result["places"][0], indent=2, ensure_ascii=False))
        
        print("\n" + "=" * 60)
        print("DEMO: search_reviews")
        print("=" * 60)
        first_place = places_result["places"][0]
        # Test with dict input
        reviews_result = search_reviews(first_place)
        print("Status:", reviews_result.get("status"))
        print("Summary:", reviews_result.get("summary"))
        print("Number of reviews fetched:", len(reviews_result.get("reviews", [])))
        if reviews_result.get("reviews"):
            print("First Review sample:")
            print(json.dumps(reviews_result["reviews"][0], indent=2, ensure_ascii=False))
            
        print("\n" + "=" * 60)
        print("DEMO: filter_reviews")
        print("=" * 60)
        # Prepare list for filter_reviews
        places_with_reviews = [{
            "place": first_place,
            "status": reviews_result.get("status"),
            "reviews": reviews_result.get("reviews") or [],
            "review_summary": reviews_result.get("summary")
        }]
        filter_result = filter_reviews("Nhóm bạn muốn đi cafe/chill ở Tây Hồ", places_with_reviews)
        print("Status:", filter_result.get("status"))
        print("Summary:", filter_result.get("summary"))
        if filter_result.get("ranked_places"):
            print("Ranked Place sample:")
            print(json.dumps(filter_result["ranked_places"][0], indent=2, ensure_ascii=False))

    print("\n" + "=" * 60)
    print("DEMO: route_advice")
    print("=" * 60)
    route_result = route_advice("['Xofa Café & Bistro', 'Cộng Cà Phê Tây Hồ']")
    print("Status:", route_result.get("status"))
    print("Summary:", route_result.get("summary"))
    print("Output JSON:")
    print(json.dumps(route_result.get("output"), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    demo()
