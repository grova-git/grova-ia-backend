import logging
from core.database import supabase

def check_conversations():
    res = supabase.table("conversations").select("*").execute()
    for c in res.data:
        print(c["user_phone"], c["state"])

if __name__ == "__main__":
    check_conversations()
