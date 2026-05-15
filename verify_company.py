import logging
from core.database import supabase

def verify_company():
    response = supabase.table("companies").select("id, name, whatsapp_phone_number_id").execute()
    for c in response.data:
        print(c)

if __name__ == "__main__":
    verify_company()
