import logging
from core.database import supabase

def check_orders():
    res = supabase.table("orders").select("*").execute()
    for o in res.data:
        print(o)

if __name__ == "__main__":
    check_orders()
