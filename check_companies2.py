import logging
from core.database import supabase

def check_companies():
    res = supabase.table("companies").select("*").execute()
    for c in res.data:
        print(c["id"], c["name"])

if __name__ == "__main__":
    check_companies()
