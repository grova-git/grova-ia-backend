import logging
from fastapi import FastAPI
from api.webhooks import whatsapp, payments

from fastapi.middleware.cors import CORSMiddleware

# Configuración básica de logs
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="AI Orchestrator SaaS",
    description="Multi-tenant WhatsApp AI Assistant for Sales & Orders",
    version="1.0.0"
)

# Configurar CORS para permitir que Next.js llame a nuestra API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción cambiar por la URL de Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar enrutadores (Webhooks)
from api.endpoints import products, companies

app.include_router(
    products.router,
    prefix="/api/products",
    tags=["Catalog API"]
)

app.include_router(
    companies.router,
    prefix="/api/companies",
    tags=["Company Config API"]
)

app.include_router(
    whatsapp.router, 
    prefix="/api/webhooks/whatsapp", 
    tags=["WhatsApp Webhooks"]
)

app.include_router(
    payments.router,
    prefix="/api/webhooks/payments",
    tags=["Payment Webhooks"]
)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "AI Orchestrator SaaS"}
