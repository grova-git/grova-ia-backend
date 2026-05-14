from fastapi import Request, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.database import supabase
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()

def get_current_company(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Dependency para FastAPI que extrae el token JWT, lo valida contra Supabase,
    y devuelve el ID de la empresa (que es el mismo ID del usuario).
    """
    token = credentials.credentials
    try:
        # get_user verifica el JWT con Supabase directamente
        response = supabase.auth.get_user(token)
        if not response or not response.user:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")
        
        # El ID del usuario en auth.users es el mismo que el ID de la empresa en la tabla companies
        return response.user.id
    except Exception as e:
        logger.error(f"Error de autenticación: {e}")
        raise HTTPException(status_code=401, detail="No autenticado")
