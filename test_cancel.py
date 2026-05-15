import logging
from core.database import supabase

def test_cancel():
    try:
        # Simulate the query
        res = supabase.table("orders").select("id").eq("status", "pendiente").order("created_at", desc=True).limit(1).execute()
        print(res.data)
    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    test_cancel()
