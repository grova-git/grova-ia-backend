import logging
from core.database import supabase
from services.orchestrator_service import OrchestratorService

logging.basicConfig(level=logging.ERROR)

def simulate_chat():
    user_id = "99f29425-4de2-4ef9-8fc4-8306c215bc27"
    response = supabase.table("companies").select("*").eq("id", user_id).execute()
    company = response.data[0]
    
    orchestrator = OrchestratorService(company)
    
    # Simulate a user phone
    user_phone = "5491100000000"
    
    # We delete previous history for this phone to start fresh
    supabase.table("conversations").delete().eq("user_phone", user_phone).execute()
    
    print("\n" + "="*50)
    print("IA SIMULADOR DEL ORQUESTADOR DE IA IA")
    print("="*50 + "\n")
    
    messages = [
        "Hola, buenas tardes.",
        "Estoy buscando algún medicamento para el dolor de cabeza, ¿tienen ibuprofeno?",
        "¡Genial! ¿Cuánto cuesta el de Baliarda?",
        "Perfecto, quiero comprar 2 cajas de Ibuprofeno Baliarda por favor."
    ]
    
    for msg in messages:
        print(f"User: {msg}")
        reply = orchestrator.process_message(user_phone, msg)
        # Encode for printing to terminal
        print(f"IA: {reply.encode('ascii', 'ignore').decode()}\n")
        print("-" * 50)

if __name__ == "__main__":
    simulate_chat()
