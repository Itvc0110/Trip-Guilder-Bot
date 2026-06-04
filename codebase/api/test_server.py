import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_spots():
    print("Testing GET /api/spots...")
    response = requests.get(f"{BASE_URL}/api/spots")
    if response.status_code == 200:
        spots = response.json()
        print(f"Success! Retrieved {len(spots)} spots.")
        print(f"Sample spot: {spots[0]['name']} - Vibe: {spots[0]['vibe']}")
    else:
        print(f"Failed to fetch spots: {response.status_code} - {response.text}")

def test_chat():
    print("\nTesting POST /api/chat...")
    payload = {
        "query": "lên lịch trình đi chơi Tây Hồ lãng mạn chiều tối thứ Bảy",
        "vibe": "romantic",
        "num_people": 2,
        "chat_history": []
    }
    response = requests.post(f"{BASE_URL}/api/chat", json=payload)
    if response.status_code == 200:
        result = response.json()
        print("Success! Agent response received:")
        print(f"Bot Message: {result['final_response']}")
        print(f"Itinerary length: {len(result['itinerary'])}")
        if len(result['itinerary']) > 0:
            print("First event:")
            print(json.dumps(result['itinerary'][0], indent=2, ensure_ascii=False))
    else:
        print(f"Failed to call chat: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_spots()
    test_chat()
