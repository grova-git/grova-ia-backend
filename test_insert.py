import logging
from core.database import supabase

def test_insert():
    try:
        res = supabase.table("orders").insert({
            "company_id": "99f29425-4de2-4ef9-8fc4-8306c215bc27",
            "user_phone": "123456789",
            "status": "pendiente"
        }).execute()
        print("Insert OK", res)
    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    test_insert()
