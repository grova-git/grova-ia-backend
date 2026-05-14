import csv
import io
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from core.database import supabase
from core.security import get_current_company
from services.openai_service import get_embedding

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/")
def get_products(company_id: str = Depends(get_current_company)):
    """Obtener todos los productos de la empresa (sin el vector embedding para ahorrar ancho de banda)"""
    # Usamos .select() específico para no traer la columna 'embedding' (vector gigante)
    response = supabase.table("products").select("id, name, description, price, stock").eq("company_id", company_id).execute()
    return response.data

@router.delete("/{product_id}")
def delete_product(product_id: str, company_id: str = Depends(get_current_company)):
    """Eliminar un producto"""
    # Importante: validamos que el company_id coincida para que nadie borre productos de otra empresa
    response = supabase.table("products").delete().eq("id", product_id).eq("company_id", company_id).execute()
    return {"status": "ok", "message": "Producto eliminado"}

@router.post("/bulk")
async def upload_products_csv(file: UploadFile = File(...), company_id: str = Depends(get_current_company)):
    """Carga masiva de productos por CSV y generación automática de Embeddings"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="El archivo debe ser un .csv")
    
    contents = await file.read()
    decoded = contents.decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    
    # Validar columnas mínimas
    expected_cols = {'nombre', 'precio'}
    actual_cols = {col.lower().strip() for col in reader.fieldnames or []}
    if not expected_cols.issubset(actual_cols):
        raise HTTPException(status_code=400, detail=f"El CSV debe contener las columnas: nombre, precio. (Opcional: descripcion, stock)")
    
    inserted_count = 0
    for row in reader:
        # Normalizar claves a minúsculas para robustez
        row_lower = {k.lower().strip(): v for k, v in row.items()}
        
        name = row_lower.get('nombre', '').strip()
        price_str = row_lower.get('precio', '0').replace(',', '.')
        description = row_lower.get('descripcion', '').strip()
        stock_str = row_lower.get('stock', '0')
        
        if not name:
            continue # Saltar filas vacías
            
        try:
            price = float(price_str)
            stock = int(stock_str)
        except ValueError:
            continue # Ignorar si el precio no es un número
        
        # Generar texto para embedding (para el RAG)
        text_for_embedding = f"Producto: {name}\nDescripción: {description}\nPrecio: {price}"
        
        try:
            # Llamar a OpenAI para el embedding vectorial
            embedding_vector = get_embedding(text_for_embedding)
            
            # Insertar en base de datos
            supabase.table("products").insert({
                "company_id": company_id,
                "name": name,
                "description": description,
                "price": price,
                "stock": stock,
                "embedding": embedding_vector
            }).execute()
            inserted_count += 1
        except Exception as e:
            logger.error(f"Error procesando producto {name}: {e}")
            raise HTTPException(status_code=400, detail=f"Error en {name}: {str(e)}")

    return {"status": "ok", "message": f"Se procesaron e insertaron {inserted_count} productos exitosamente"}
