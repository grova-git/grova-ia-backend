import mercadopago
import logging
from fastapi import HTTPException
from core.database import supabase
from core.config import settings

logger = logging.getLogger(__name__)

class MercadoPagoService:
    def __init__(self, access_token: str):
        if not access_token:
            logger.error("MercadoPago access token is empty")
            raise ValueError("MercadoPago access token is required")
        self.sdk = mercadopago.SDK(access_token)

    def create_preference(self, order_id: str, items: list, company_name: str) -> str:
        """
        Crea una preferencia de pago en Mercado Pago y retorna el init_point (URL de pago).
        """
        try:
            mp_items = []
            total_amount = 0.0

            for item in items:
                price = float(item["unit_price"])
                qty = int(item["quantity"])
                total_amount += price * qty
                
                mp_items.append({
                    "id": str(item.get("product_id", "")),
                    "title": item["name"],
                    "quantity": qty,
                    "unit_price": price,
                    "currency_id": "ARS"
                })

            preference_data = {
                "items": mp_items,
                "statement_descriptor": company_name,
                "external_reference": str(order_id),
                "auto_return": "approved",
                # Opcional: urls de retorno si el usuario está en web. 
                # Como es WhatsApp, generalmente vuelven al chat manual, pero está bien definirlas:
                "back_urls": {
                    "success": "https://wa.me/", # Se podría armar el link del bot aquí
                    "failure": "",
                    "pending": ""
                },
                # En Render tu webhook:
                "notification_url": f"https://grova-ia-backend.onrender.com/api/webhooks/payments/mercadopago?order_id={order_id}"
            }

            preference_response = self.sdk.preference().create(preference_data)
            preference = preference_response["response"]
            
            # Retorna el link para pagar
            return preference["init_point"]
            
        except Exception as e:
            logger.error(f"Error creating MP preference: {e}")
            raise

