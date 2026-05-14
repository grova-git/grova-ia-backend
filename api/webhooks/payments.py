import logging
from fastapi import APIRouter, Request, HTTPException
from core.database import supabase
from services.whatsapp_service import send_message

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/stripe")
async def stripe_webhook(request: Request):
    """
    Webhook para recibir notificaciones de Stripe.
    Se asume que al crear el PaymentIntent se le pasó el 'order_id' en metadata.
    """
    payload = await request.json()
    
    # Manejo de eventos de Stripe
    if payload.get("type") == "payment_intent.succeeded":
        payment_intent = payload["data"]["object"]
        order_id = payment_intent.get("metadata", {}).get("order_id")
        
        if not order_id:
            logger.warning("Pago exitoso pero no contiene order_id en la metadata.")
            return {"status": "ignored"}
            
        return await process_successful_payment(order_id, payment_intent["id"])

    return {"status": "ok"}


@router.post("/mercadopago")
async def mercadopago_webhook(request: Request):
    """
    Webhook para recibir notificaciones de Mercado Pago.
    """
    payload = await request.json()
    
    # MP envía topic="payment" o type="payment"
    if payload.get("type") == "payment" and payload.get("action") == "payment.created":
        # En una integración real habría que hacer un GET a la API de MP 
        # para verificar el estado usando el ID de payload["data"]["id"]
        # Aquí simplificamos asumiendo que validamos la metadata:
        payment_id = payload["data"]["id"]
        # Obtenemos metadata simulada (en MP se manda en preference_id o external_reference)
        order_id = request.query_params.get("order_id") 
        
        if order_id:
            return await process_successful_payment(order_id, str(payment_id))

    return {"status": "ok"}


async def process_successful_payment(order_id: str, payment_id: str):
    """
    Lógica de cierre de ciclo (Multi-tenant): 
    Actualiza la BD, libera la IA y notifica por WhatsApp.
    """
    try:
        # 1. Obtener la orden de la base de datos
        res_order = supabase.table("orders").select("*").eq("id", order_id).execute()
        if not res_order.data:
            logger.error(f"Orden {order_id} no encontrada al procesar pago.")
            raise HTTPException(status_code=404, detail="Order not found")
            
        order = res_order.data[0]
        
        if order["status"] == "pagado":
            return {"status": "already_paid"}

        company_id = order["company_id"]
        user_phone = order["user_phone"]
        conversation_id = order["conversation_id"]

        # 2. Actualizar la orden a estado pagado
        supabase.table("orders").update({
            "status": "pagado", 
            "payment_id": payment_id
        }).eq("id", order_id).execute()
        
        # 3. Liberar el estado de la conversación (de 'pago_pendiente' a 'atencion')
        if conversation_id:
            supabase.table("conversations").update({"state": "atencion"}).eq("id", conversation_id).execute()
        
        # 4. Obtener datos del Tenant (Empresa) para enviar el WhatsApp
        res_company = supabase.table("companies").select("*").eq("id", company_id).execute()
        if not res_company.data:
            logger.error(f"Tenant {company_id} no encontrado para la orden {order_id}.")
            return {"status": "error"}
            
        company = res_company.data[0]

        # 5. Enviar mensaje de confirmación al cliente por WhatsApp
        success_message = "🎉 *¡Pago recibido exitosamente!* 🎉\n\nHemos procesado tu pago y tu pedido ya está en preparación. ¡Muchas gracias por tu compra!"
        
        send_message(
            phone_number_id=company["whatsapp_phone_number_id"],
            to=user_phone,
            text=success_message,
            access_token=company.get("whatsapp_access_token", "")
        )

        logger.info(f"✅ Pedido {order_id} pagado. WhatsApp de éxito enviado a {user_phone}.")
        return {"status": "success", "order_id": order_id}

    except Exception as e:
        logger.error(f"Error cerrando ciclo de pago para orden {order_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal error")
