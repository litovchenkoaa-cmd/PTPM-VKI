import bcrypt
import hashlib

def mask_password(password: str):
    hash_password = hashlib.sha256(password.encode('utf-8'))
    return f"hash{hash_password.hexdigest()[:12]}"

if __name__ == "__main__":
    f = mask_password("Hello")
    s = mask_password("Hello")
    if f == s:
        print(f)