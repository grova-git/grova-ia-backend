from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from core.database import supabase
from core.security import get_current_company

router = APIRouter()

class ConfigUpdate(BaseModel):
    name: str | None = None
    whatsapp_phone_number_id: str | None = None
    whatsapp_access_token: str | None = None
    mercadopago_access_token: str | None = None
    system_prompt: str | None = None

@router.get("/config")
def get_company_config(company_id: str = Depends(get_current_company)):
    """Obtiene la configuración actual de la empresa"""
    response = supabase.table("companies").select("name, whatsapp_phone_number_id, whatsapp_access_token, mercadopago_access_token, system_prompt").eq("id", company_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return response.data[0]

@router.post("/config")
def update_company_config(config: ConfigUpdate, company_id: str = Depends(get_current_company)):
    """Actualiza la configuración de la empresa"""
    update_data = {k: v for k, v in config.model_dump().items() if v is not None}
    if not update_data:
        return {"status": "ok"}
    
    try:
        response = supabase.table("companies").update(update_data).eq("id", company_id).execute()
        return {"status": "ok", "message": "Configuración guardada exitosamente"}
    except Exception as e:
        import logging
        logging.error(f"Error updating config: {e}")
        raise HTTPException(status_code=400, detail=str(e))
