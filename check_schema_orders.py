import httpx
import os
from core.config import settings

def test():
    # Use the rest/v1/?apikey= endpoint to query OpenAPI definitions if available
    url = f"{settings.SUPABASE_URL}/rest/v1/?apikey={settings.SUPABASE_KEY}"
    res = httpx.get(url)
    data = res.json()
    if 'definitions' in data and 'orders' in data['definitions']:
        print(data['definitions']['orders']['properties'].keys())
    else:
        print("Not found in openapi")

if __name__ == "__main__":
    test()
