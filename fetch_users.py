import httpx
import os
from core.config import settings

def fetch_users():
    url = f"{settings.SUPABASE_URL}/auth/v1/admin/users"
    headers = {
        "apikey": settings.SUPABASE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_KEY}"
    }
    res = httpx.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        users = data.get("users", [])
        for u in users:
            print(u["id"], u["email"])
    else:
        print("Failed:", res.status_code, res.text)

if __name__ == "__main__":
    fetch_users()
