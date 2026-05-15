import httpx
import os
from core.config import settings

def get_schema():
    url = f"{settings.SUPABASE_URL}/rest/v1/orders"
    headers = {
        "apikey": settings.SUPABASE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_KEY}",
        "Range": "0-0"
    }
    response = httpx.get(url, headers=headers)
    print(response.json())

if __name__ == "__main__":
    get_schema()
