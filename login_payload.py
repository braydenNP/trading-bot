from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64
import json

def encrypt_password(password: str, key: str) -> str:
    """
    AES encrypts the password using ECB mode with the given key.
    Mimics CryptoJS AES encryption behavior with ECB + PKCS7.
    """
    key_bytes = key.encode('utf-8')
    cipher = AES.new(key_bytes, AES.MODE_ECB)
    padded_password = pad(password.encode('utf-8'), AES.block_size)
    encrypted_bytes = cipher.encrypt(padded_password)
    return base64.b64encode(encrypted_bytes).decode('utf-8')

def build_login_payload(username: str, password: str, session_key: str = None, session_id: str = None) -> dict:
    """
    Constructs the login payload similar to the JavaScript logic.
    """
    payload = {
        "username": username.lower(),
        "password": encrypt_password(password, session_key) if session_key else password,
        "provider": "paritech",
        "storage_token": False
    }

    if session_id:
        payload["session_id"] = session_id

    return payload

# Example usage
if __name__ == "__main__":
    user = input("Username: ").strip()
    pwd = input("Password: ").strip()

    # Replace with your actual session key and ID if needed
    session_key = None  # Must be 16/24/32 bytes for AES
    session_id = "ecddf5fa32774b05a8ecc9206b707404"

    payload = build_login_payload(user, pwd, session_key=session_key, session_id=session_id)
    print("\nPayload to send:")
    print(json.dumps(payload, indent=2))
