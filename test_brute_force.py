import requests
import time

BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "nonexistent@example.com"
PASSWORD = "wrongpassword"

def test_brute_force():
    print(f"Testing brute force protection for {EMAIL}...")
    
    for i in range(1, 8):
        start_time = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"email": EMAIL, "password": PASSWORD}
            )
            duration = time.time() - start_time
            print(f"Attempt {i}: Status {response.status_code}, Detail: {response.json().get('detail')}, Duration: {duration:.2f}s")
            
            if response.status_code == 429:
                print("SUCCESS: Lockout triggered!")
                return
        except Exception as e:
            print(f"Attempt {i} failed: {e}")
            
    print("FAILURE: Lockout was NOT triggered after 7 attempts.")

if __name__ == "__main__":
    test_brute_force()
