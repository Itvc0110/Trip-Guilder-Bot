from tools.place_search import search_places, search_attractions
from dotenv import load_dotenv
import json

def test():
    load_dotenv()
    print("Testing search_places:")
    result = search_places("quán cafe view đẹp ở quận 1 Hồ Chí Minh")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print("\nTesting search_attractions:")
    result2 = search_places("khách sạn 5 sao có hồ bơi ở Đà Nẵng")
    print(json.dumps(result2, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test()
