import logging
from fastapi import APIRouter, Request, HTTPException, Query, BackgroundTasks
from core.config import settings
from core.database import get_company_by_phone_number_id
from schemas.whatsapp import WhatsAppWebhookPayload

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    """
    Endpoint para verificación inicial de Meta (Webhook Setup).
    """
    if hub_mode == "subscribe" and hub_verify_token == settings.GLOBAL_WHATSAPP_VERIFY_TOKEN:
        logger.info("Webhook verificado exitosamente.")
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Token de verificación inválido")


def process_whatsapp_message(payload: WhatsAppWebhookPayload, company: dict):
    """
    Función que será procesada en background para no bloquear el webhook.
    Aquí entrará la lógica del Orquestador (RAG, Estados, OpenAI).
    """
    try:
        # Extraer el mensaje y el usuario
        entry = payload.entry[0]
        change = entry.changes[0].value
        
        if not change.messages:
            return # Puede ser un status update (entregado, leído)
            
        message = change.messages[0]
        user_phone = message.from_
        
        if message.type == "text":
            text_body = message.text.body
            logger.info(f"[Company: {company['name']}] Mensaje de {user_phone}: {text_body}")
            
            from services.orchestrator_service import OrchestratorService
            from services.whatsapp_service import send_message
            
            orchestrator = OrchestratorService(company)
            response = orchestrator.process_message(user_phone, text_body)
            
            if response:
                send_message(
                    phone_number_id=company["whatsapp_phone_number_id"],
                    to=user_phone,
                    text=response,
                    access_token=company.get("whatsapp_access_token", "")
                )
            
    except Exception as e:
        logger.error(f"Error procesando el mensaje: {e}")


@router.post("/")
async def receive_whatsapp_message(
    payload: WhatsAppWebhookPayload, 
    background_tasks: BackgroundTasks
):
    """
    Recepción de mensajes de WhatsApp.
    Maneja la identificación del tenant (company_id).
    """
    try:
        entry = payload.entry[0]
        change = entry.changes[0].value
        
        # 1. Identificar a la empresa mediante el número receptor
        phone_number_id = change.metadata.phone_number_id
        company = get_company_by_phone_number_id(phone_number_id)
        
        if not company:
            logger.error(f"Tenant no encontrado para phone_number_id: {phone_number_id}")
            return {"status": "error", "message": "Tenant not found"}

        # 2. Enviar el procesamiento a background para responder rápido (200 OK a Meta)
        background_tasks.add_task(process_whatsapp_message, payload, company)
        
        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error parseando el webhook: {e}")
        # Siempre devolver 200 a Meta para que no reintente masivamente si el json es inválido
        return {"status": "ok"}
