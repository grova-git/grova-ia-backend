from supabase import create_client, Client
from core.config import settings

# Inicializamos el cliente global de Supabase
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def get_company_by_phone_number_id(phone_number_id: str):
    """
    Busca la configuración del tenant basándose en el ID del número 
    receptor de WhatsApp.
    """
    response = supabase.table("companies") \
        .select("*") \
        .eq("whatsapp_phone_number_id", phone_number_id) \
        .execute()
        
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None
