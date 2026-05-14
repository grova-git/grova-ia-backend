import logging
from core.database import supabase

def check_orders_schema():
    try:
        response = supabase.table("orders").insert({"status": "test"}).execute()
    except Exception as e:
        print("Insert error:", e)

if __name__ == "__main__":
    check_orders_schema()
