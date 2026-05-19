import httpx
import os
from core.config import settings

def check_users():
    query = """
    SELECT id, email
    FROM auth.users;
    """
    res = supabase.rpc("run_sql", {"query": query}).execute() # if we had run_sql
    pass

if __name__ == "__main__":
    pass
