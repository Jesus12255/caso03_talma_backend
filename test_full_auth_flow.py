import requests
import json
import time

BASE_URL = "http://localhost:8080" # main.py says 8080 or config says 8000? Let's check main.py
# main.py line 36: uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

def test_flow():
    email = "pruebastivit@gmail.com" # From .env
    password = "TivitAlmaviva2025." # From .env
    
    print(f"1. Attempting login for {email}...")
    try:
        login_res = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })
        login_res.raise_for_status()
        tokens = login_res.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        print("Login SUCCESSFUL.")
        # print(f"Access Token: {access_token[:20]}...")
    except Exception as e:
        print(f"Login FAILED: {e}")
        if hasattr(e, 'response') and e.response is not None:
             print(f"Response: {e.response.text}")
        return

    headers = {"Authorization": f"Bearer {access_token}"}
    
    print("2. Calling /auth/me with valid token...")
    me_res = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Response code: {me_res.status_code}")
    if me_res.status_code == 200:
        print("Access SUCCESSFUL.")
    else:
        print(f"Access FAILED: {me_res.text}")
        return

    print("3. Calling /auth/logout...")
    logout_res = requests.post(f"{BASE_URL}/auth/logout", headers=headers, json={
        "refresh_token": refresh_token
    })
    print(f"Logout response code: {logout_res.status_code}")
    print(f"Logout message: {logout_res.text}")

    print("4. Calling /auth/me AGAIN (should fail with 401)...")
    me_res_again = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Response code after logout: {me_res_again.status_code}")
    
    if me_res_again.status_code == 401:
        print("SUCCESS: Token Revocation is working!")
    else:
        print(f"FAILURE: Token still valid! Status: {me_res_again.status_code}")
        print(f"Response: {me_res_again.text}")

if __name__ == "__main__":
    test_flow()
