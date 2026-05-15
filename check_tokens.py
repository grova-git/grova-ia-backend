import logging
from core.database import supabase

def verify_tokens():
    response = supabase.table("companies").select("id, name, whatsapp_phone_number_id, whatsapp_access_token, mercadopago_access_token").execute()
    for c in response.data:
        print(c)

if __name__ == "__main__":
    verify_tokens()
