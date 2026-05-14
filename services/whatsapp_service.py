import httpx
import logging

logger = logging.getLogger(__name__)

def send_message(phone_number_id: str, to: str, text: str, access_token: str):
    """
    Envía un mensaje usando WhatsApp Cloud API.
    """
    if not access_token:
        logger.warning("No se proporcionó access_token. Simulando envío en consola.")
        logger.info(f"-> [WhatsApp a {to}]: {text}")
        return {"status": "simulated"}

    url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    # Fix especial para números de Argentina (Test Number bug)
    # Meta registra los números sin el '9', pero los lee con el '9'.
    if to.startswith("549") and len(to) == 13:
        to = "54" + to[3:]

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    
    try:
        with httpx.Client() as client:
            response = client.post(url, headers=headers, json=payload)
            if response.status_code != 200:
                logger.error(f"Meta Error: {response.text}")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error enviando WhatsApp: {e}")
        return None
