import asyncio
from core.database import supabase
from services.openai_service import get_embedding

dummy_products = [
    {"name": "Pizza Margarita", "description": "Pizza clásica con salsa de tomate, mozzarella fresca y albahaca.", "price": 12.50, "stock": 50},
    {"name": "Pizza Pepperoni", "description": "Pizza con doble porción de pepperoni crujiente y extra queso.", "price": 14.00, "stock": 40},
    {"name": "Empanada de Carne", "description": "Empanada frita rellena de carne cortada a cuchillo, huevo y aceitunas.", "price": 2.50, "stock": 100},
    {"name": "Coca Cola 1.5L", "description": "Gaseosa Coca Cola tamaño familiar, bien fría.", "price": 3.00, "stock": 200},
    {"name": "Cerveza Artesanal IPA", "description": "Cerveza rubia artesanal, amarga e intensa. Lata 473ml.", "price": 4.50, "stock": 30}
]

async def seed():
    print("Buscando tu empresa de prueba en Supabase...")
    # 1. Obtenemos el ID de la primera empresa que creaste
    res = supabase.table("companies").select("id").limit(1).execute()
    if not res.data:
        print("❌ Error: No encontré ninguna empresa en la tabla 'companies'. Por favor créala manualmente en Supabase primero.")
        return
        
    company_id = res.data[0]["id"]
    print(f"✅ Empresa encontrada con ID: {company_id}\n")
    
    # 2. Insertamos cada producto y generamos su Vector IA
    for prod in dummy_products:
        print(f"🧠 Generando embedding de IA para: {prod['name']}...")
        
        # El texto que la IA "leerá" para buscar
        text_to_embed = f"{prod['name']}. {prod['description']}"
        embedding_vector = get_embedding(text_to_embed)
        
        product_data = {
            "company_id": company_id,
            "name": prod["name"],
            "description": prod["description"],
            "price": prod["price"],
            "stock": prod["stock"],
            "embedding": embedding_vector
        }
        
        supabase.table("products").insert(product_data).execute()
        print(f"✅ Insertado en Supabase: {prod['name']}")
        
    print("\n🎉 ¡Misión cumplida! Tienes 5 productos inyectados con Inteligencia Artificial. Ya puedes hablarle al bot.")

if __name__ == "__main__":
    asyncio.run(seed())
