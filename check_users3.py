import httpx
import os
from core.config import settings

def find_real_user():
    url = f"{settings.SUPABASE_URL}/rest/v1/rpc/run_sql"
    headers = {
        "apikey": settings.SUPABASE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    # This might not work if run_sql doesn't exist
    pass

def check_with_supabase():
    from core.database import supabase
    res = supabase.auth.admin.list_users() # Not available
    pass

def check_companies_names():
    from core.database import supabase
    res = supabase.table("companies").select("*").execute()
    for c in res.data:
        print(c)

if __name__ == "__main__":
    check_companies_names()
