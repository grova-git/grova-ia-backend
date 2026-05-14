import csv
import io
from core.database import supabase
from services.openai_service import get_embedding
import logging

logging.basicConfig(level=logging.INFO)

company_id = supabase.table("companies").select("id").limit(1).execute().data[0]['id']

with open("C:/Users/ezequ/Desktop/productos_farmacia.csv", "rb") as f:
    contents = f.read()

decoded = contents.decode('utf-8')
reader = csv.DictReader(io.StringIO(decoded))

inserted_count = 0
for row in reader:
    row_lower = {k.lower().strip(): v for k, v in row.items() if k is not None}
    
    name = row_lower.get('nombre', '').strip()
    price_str = row_lower.get('precio', '0').replace(',', '.')
    description = row_lower.get('descripcion', '').strip()
    stock_str = row_lower.get('stock', '0')
    
    if not name:
        print("Skipped due to no name")
        continue 
        
    try:
        price = float(price_str)
        stock = int(stock_str)
    except ValueError:
        print("Skipped due to value error")
        continue 
    
    text_for_embedding = f"Producto: {name}\nDescripción: {description}\nPrecio: {price}"
    
    try:
        embedding_vector = get_embedding(text_for_embedding)
        supabase.table("products").insert({
            "company_id": company_id,
            "name": name,
            "description": description,
            "price": price,
            "stock": stock,
            "embedding": embedding_vector
        }).execute()
        inserted_count += 1
        print("Inserted:", name)
        break # Only do one
    except Exception as e:
        print(f"Error procesando producto {name}: {e}")
        continue

print("Total inserted:", inserted_count)
