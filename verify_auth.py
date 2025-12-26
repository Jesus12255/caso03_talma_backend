
from fastapi.testclient import TestClient
from app.auth.repository.user_repository import fake_users_db
from app.auth.service.impl.auth_service_impl import fake_verification_codes
from utl.security_util import SecurityUtil
from main import app

client = TestClient(app)

def test_auth_flow():
    # 1. Setup Test User
    email = "test_auth@example.com"
    password = "password123"
    hashed_pwd = SecurityUtil.get_password_hash(password)
    
    fake_users_db[email] = {
        "id": 999,
        "email": email,
        "full_name": "Test Auth User",
        "is_active": True,
        "hashed_password": hashed_pwd
    }
    
    print(f"[-] Created test user: {email} / {password}")

    # 2. Test Login (Success)
    print("[-] Testing Login...")
    res = client.post("/auth/login", json={"email": email, "password": password})
    if res.status_code == 200:
        print("[+] Login Successful. Token received.")
    else:
        print(f"[!] Login Failed: {res.text}")
        return

    # 3. Test Forgot Password
    print("[-] Testing Forgot Password...")
    res = client.post("/auth/forgot-password", json={"email": email})
    if res.status_code == 200:
        print("[+] Forgot Password Request Successful.")
    else:
        print(f"[!] Forgot Password Request Failed: {res.text}")
        return

    # 4. Get the code (Cheat by reading memory)
    code = fake_verification_codes.get(email)
    if code:
        print(f"[+] Retrieved verification code from memory: {code}")
    else:
        print("[!] Failed to retrieve verification code from memory.")
        return

    # 5. Test Verify Code
    print("[-] Testing Verify Code...")
    res = client.post("/auth/verify-code", json={"email": email, "code": code})
    if res.status_code == 200:
        print("[+] Code Verified Successfully.")
    else:
        print(f"[!] Code Verification Failed: {res.text}")
        return

    # 6. Test Reset Password
    new_password = "newpassword456"
    print("[-] Testing Reset Password...")
    res = client.post("/auth/reset-password", json={
        "email": email, 
        "code": code, 
        "new_password": new_password
    })
    if res.status_code == 200:
        print("[+] Password Reset Successful.")
    else:
        print(f"[!] Password Reset Failed: {res.text}")
        return

    # 7. Test Login with NEW PASSWORD
    print("[-] Testing Login with New Password...")
    res = client.post("/auth/login", json={"email": email, "password": new_password})
    if res.status_code == 200:
        print("[+] Login with New Password Successful.")
    else:
        print(f"[!] Login with New Password Failed: {res.text}")
        return
        
    # 8. Test Login with OLD PASSWORD (should fail)
    print("[-] Testing Login with Old Password (should fail)...")
    res = client.post("/auth/login", json={"email": email, "password": password})
    if res.status_code == 400:
        print("[+] Login with Old Password Failed as expected.")
    else:
        print(f"[!] Login with Old Password unexpected result: {res.status_code}")

if __name__ == "__main__":
    test_auth_flow()
