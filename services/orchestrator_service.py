import json
import logging
from core.database import supabase
from services.openai_service import get_embedding, get_chat_completion

logger = logging.getLogger(__name__)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_catalog",
            "description": "Busca productos en el catálogo de la empresa. Úsalo siempre que el usuario pregunte por precios o productos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Término de búsqueda (ej: 'zapatillas rojas' o 'pizza margarita')"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_order_summary",
            "description": "Genera un resumen de pedido cuando el usuario decide comprar uno o más productos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "product_id": {"type": "string"},
                                "name": {"type": "string"},
                                "quantity": {"type": "integer"},
                                "unit_price": {"type": "number"}
                            }
                        }
                    }
                },
                "required": ["items"]
            }
        }
    }
]

class OrchestratorService:
    def __init__(self, company: dict):
        self.company = company
        self.company_id = company["id"]
        base_prompt = company.get("system_prompt") or "Eres un asistente de ventas profesional."
        
        # Inyección de las directrices estrictas
        self.system_prompt = f"""{base_prompt}

REGLA DE ORO ANTI-ALUCINACIÓN: Tienes ESTRICTAMENTE PROHIBIDO mencionar o inventar precios que no existan en el catálogo proporcionado por la herramienta 'search_catalog'. 
Si el usuario pregunta por un producto o precio no disponible, usa la herramienta de búsqueda. Si no se encuentra, indica claramente que no está disponible o dirígelo a un asesor humano.
No asumas precios genéricos.

ESTÉTICA: Utiliza un tono profesional, limpio y editorial. Usa *negritas* para destacar puntos clave y listas para enumerar. Sé muy conciso y evita bloques de texto largos.
"""

    def process_message(self, user_phone: str, message: str) -> str:
        conv = self._get_or_create_conversation(user_phone)
        state = conv["state"]
        history = conv["history"]
        
        # 1. Módulo Human-in-the-loop (Detección de frustración)
        frustration_keywords = ["humano", "persona", "asesor", "queja", "enojado", "ayuda", "malo", "operador"]
        if any(word in message.lower() for word in frustration_keywords) and state != "humano_requerido":
            self._update_conversation_state(conv["id"], "humano_requerido")
            self._notify_human(user_phone, message)
            return "Entiendo. He transferido esta conversación a un *asesor humano* 👤. En breve se comunicarán contigo para ayudarte de forma personalizada."
            
        if state == "humano_requerido":
            return None # El bot guarda silencio
            
        if state == "pago_pendiente":
            if "cancelar" in message.lower() or "anular" in message.lower() or "no" in message.lower().split():
                self._update_conversation_state(conv["id"], "atencion")
                # Intentar cancelar la orden pendiente si existe
                res = supabase.table("orders").select("id").eq("conversation_id", conv["id"]).eq("status", "pendiente").order("created_at", desc=True).limit(1).execute()
                if res.data:
                    supabase.table("orders").update({"status": "cancelada"}).eq("id", res.data[0]["id"]).execute()
                return "❌ Pedido cancelado exitosamente. Tu carrito ha sido vaciado. ¿En qué más te puedo ayudar hoy?"
                
            return "⏳ *Tu pago está pendiente.* Por favor, completa el pago en el enlace de Mercado Pago que te enviamos para procesar tu orden.\n\n_(Si deseas anular este pedido y empezar de nuevo, escribe *Cancelar*)_"

        # 2. Validación Transaccional (Confirmación del Pedido)
        if state == "confirmacion_pedido":
            if message.lower().strip() in ["si", "sí", "yes", "confirmar", "ok", "dale", "perfecto"]:
                self._update_conversation_state(conv["id"], "pago_pendiente")
                
                # Buscar la orden pendiente
                res = supabase.table("orders").select("*").eq("conversation_id", conv["id"]).eq("status", "pendiente").order("created_at", desc=True).limit(1).execute()
                if not res.data:
                    self._update_conversation_state(conv["id"], "atencion")
                    return "No encontré tu pedido pendiente. ¿Podemos empezar de nuevo?"
                
                order = res.data[0]
                mp_token = self.company.get("mercadopago_access_token")
                
                if not mp_token:
                    # Fallback si no hay Mercado Pago configurado
                    return "✅ *¡Pedido confirmado!* Sin embargo, el comercio no tiene configurado el pago electrónico. Te contactarán en breve para coordinar el pago manual."
                
                try:
                    from services.payment_service import MercadoPagoService
                    mp_service = MercadoPagoService(mp_token)
                    pay_link = mp_service.create_preference(order["id"], order["items"], self.company["name"])
                    
                    return f"✅ *¡Pedido confirmado!*\n\nPor favor, realiza el pago de *${order['subtotal']}* ingresando a este enlace seguro de Mercado Pago:\n🔗 {pay_link}"
                except Exception as e:
                    logger.error(f"Error al generar link MP: {e}")
                    return "❌ Hubo un error al generar el link de pago. Por favor, intenta de nuevo más tarde o contacta a un asesor."
                
            elif message.lower().strip() in ["no", "cancelar"]:
                self._update_conversation_state(conv["id"], "atencion")
                # Marcar orden como cancelada
                res = supabase.table("orders").select("id").eq("conversation_id", conv["id"]).eq("status", "pendiente").order("created_at", desc=True).limit(1).execute()
                if res.data:
                    supabase.table("orders").update({"status": "cancelada"}).eq("id", res.data[0]["id"]).execute()
                
                return "❌ Pedido cancelado. ¿Hay algún otro producto en el que te pueda ayudar?"
            else:
                return "Por favor, responde *Sí* para confirmar tu pedido o *No* para cancelar."

        # 3. Flujo Base (Ventas y RAG)
        history.append({"role": "user", "content": message})
        
        # Llamada inicial al LLM
        ai_message = get_chat_completion(history, self.system_prompt, TOOLS)
        
        # Ejecución de Herramientas (Tool Calling)
        if ai_message.tool_calls:
            history.append(ai_message.model_dump(exclude_none=True))
            
            for tool_call in ai_message.tool_calls:
                args = json.loads(tool_call.function.arguments)
                
                if tool_call.function.name == "search_catalog":
                    results = self._search_catalog(args["query"])
                    history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": json.dumps(results)
                    })
                    
                elif tool_call.function.name == "generate_order_summary":
                    response_text = self._build_order_summary(args["items"])
                    self._update_conversation_state(conv["id"], "confirmacion_pedido")
                    
                    # Guardar orden en BD como pendiente
                    total = sum(item["quantity"] * item["unit_price"] for item in args["items"])
                    supabase.table("orders").insert({
                        "company_id": self.company_id,
                        "user_phone": user_phone,
                        "conversation_id": conv["id"],
                        "subtotal": total,
                        "items": args["items"],
                        "status": "pendiente"
                    }).execute()
                    
                    history.append({"role": "tool", "tool_call_id": tool_call.id, "name": tool_call.function.name, "content": "Resumen generado y enviado."})
                    history.append({"role": "assistant", "content": response_text})
                    self._update_conversation_history(conv["id"], history)
                    return response_text

            # Segunda llamada al LLM con los resultados del RAG
            ai_message = get_chat_completion(history, self.system_prompt, TOOLS)

        # Respuesta estándar
        response_text = ai_message.content
        history.append({"role": "assistant", "content": response_text})
        self._update_conversation_history(conv["id"], history)
        
        return response_text

    def _build_order_summary(self, items):
        """Genera el resumen del pedido con estética y emojis."""
        total = sum(item["quantity"] * item["unit_price"] for item in items)
        
        summary = "📦 *RESUMEN DE TU PEDIDO* 📦\n\n"
        for item in items:
            subtotal_item = item['unit_price'] * item['quantity']
            summary += f"🔹 *{item['quantity']}x* {item['name']} - ${subtotal_item:.2f}\n"
        
        summary += f"\n✅ *Total a Pagar:* ${total:.2f}\n\n"
        summary += "¿Confirmas este pedido para proceder al pago? *(Responde Sí o No)*"
        return summary

    def _search_catalog(self, query: str):
        """Ejecuta búsqueda vectorial (RAG) en Supabase."""
        try:
            embedding = get_embedding(query)
            response = supabase.rpc("match_products", {
                "query_embedding": embedding,
                "match_threshold": 0.4, # Similitud mínima
                "match_count": 5,
                "p_company_id": self.company_id
            }).execute()
            
            if not response.data:
                return {"message": "No hay productos que coincidan. OFRECE HABLAR CON UN ASESOR."}
            
            return [{"id": p["id"], "name": p["name"], "price": p["price"], "stock": p["stock"]} for p in response.data]
        except Exception as e:
            logger.error(f"Error en RAG vectorial: {e}")
            return {"error": "El catálogo no está disponible en este momento."}

    def _get_or_create_conversation(self, user_phone: str):
        res = supabase.table("conversations").select("*").eq("company_id", self.company_id).eq("user_phone", user_phone).execute()
        if res.data:
            return res.data[0]
            
        new_conv = {"company_id": self.company_id, "user_phone": user_phone, "state": "atencion", "history": []}
        res_insert = supabase.table("conversations").insert(new_conv).execute()
        return res_insert.data[0]
        
    def _update_conversation_state(self, conv_id: str, state: str):
        supabase.table("conversations").update({"state": state}).eq("id", conv_id).execute()
        
    def _update_conversation_history(self, conv_id: str, history: list):
        pruned_history = history[-15:] if len(history) > 15 else history
        supabase.table("conversations").update({"history": pruned_history}).eq("id", conv_id).execute()

    def _notify_human(self, user_phone: str, message: str):
        logger.warning(f"🚨 HUMAN IN THE LOOP REQUIRED 🚨 Tenant: {self.company_id} | User: {user_phone} | Msg: {message}")
