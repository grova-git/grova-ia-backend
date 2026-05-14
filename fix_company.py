from core.database import supabase

user_id = "99f29425-4de2-4ef9-8fc4-8306c215bc27"

try:
    response = supabase.table("companies").insert({
        "id": user_id,
        "name": "Empresa de Ezequiel",
        "whatsapp_phone_number_id": "",
        "whatsapp_access_token": "",
        "mercadopago_access_token": None
    }).execute()
    print("Inserted successfully:", response.data)
except Exception as e:
    print("Error inserting:", e)
