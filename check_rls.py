import httpx
import os
from core.config import settings

def check_rls():
    url = f"{settings.SUPABASE_URL}/rest/v1/orders"
    headers = {
        "apikey": settings.SUPABASE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_KEY}",
    }
    # Wait, using service_role key bypasses RLS.
    # We need to query Postgres to see if RLS is enabled on 'orders'.
    query = """
    SELECT relname, relrowsecurity
    FROM pg_class
    WHERE relname = 'orders';
    """
    res = supabase.rpc("run_sql", {"query": query}).execute() # if we had run_sql
    pass

if __name__ == "__main__":
    check_rls()
