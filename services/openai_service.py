from openai import OpenAI
from core.config import settings

# Cliente global
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_embedding(text: str) -> list[float]:
    """Genera vector de embeddings usando el modelo optimizado de OpenAI."""
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def get_chat_completion(messages: list[dict], system_prompt: str, tools=None) -> dict:
    """Llamada a gpt-4o-mini con bajo temperature para evitar alucinaciones."""
    msgs = [{"role": "system", "content": system_prompt}] + messages
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=msgs,
        tools=tools,
        temperature=0.1 # Temperatura muy baja = máxima rigurosidad
    )
    return response.choices[0].message
