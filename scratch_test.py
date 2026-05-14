from core.database import supabase
from services.openai_service import get_embedding
import logging

logging.basicConfig(level=logging.INFO)

company_id = supabase.table("companies").select("id").limit(1).execute().data[0]['id']

name = "Test Product"
description = "Test Desc"
price = 10.0
stock = 5

try:
    print("Getting embedding...")
    embedding_vector = get_embedding(f"Producto: {name}\nDescripción: {description}\nPrecio: {price}")
    print("Got embedding! Length:", len(embedding_vector))
    
    print("Inserting to supabase...")
    res = supabase.table("products").insert({
        "company_id": company_id,
        "name": name,
        "description": description,
        "price": price,
        "stock": stock,
        "embedding": embedding_vector
    }).execute()
    print("Success!", res.data)
except Exception as e:
    print("Exception occurred:", type(e).__name__, str(e))
