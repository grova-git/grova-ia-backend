import logging
from core.database import supabase

def fix_duplicate():
    target_id = "1158744353980655"
    print(f"Buscando empresa con whatsapp_phone_number_id = {target_id}")
    
    response = supabase.table("companies").select("*").eq("whatsapp_phone_number_id", target_id).execute()
    
    if not response.data:
        print("No se encontró ninguna empresa con este número.")
        return
        
    for company in response.data:
        print(f"Empresa encontrada: {company['id']} - {company['name']}")
        
        # If it's not the user's current company (which we know is 99f29425-4de2-4ef9-8fc4-8306c215bc27)
        if company['id'] != "99f29425-4de2-4ef9-8fc4-8306c215bc27":
            print("Limpiando el número de esta cuenta antigua...")
            # We can't set it to "" if it's unique and another one might have "", let's append the ID to make it unique or set to null
            # Wait, in the schema, is it nullable?
            # Let's set it to something like 'old_' + company['id']
            supabase.table("companies").update({"whatsapp_phone_number_id": f"old_{company['id']}"}).eq("id", company['id']).execute()
            print("Listo. Se ha liberado el número.")

if __name__ == "__main__":
    fix_duplicate()
