import logging
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_config():
    # MOCK the get_current_company dependency
    from core.security import get_current_company
    app.dependency_overrides[get_current_company] = lambda: "99f29425-4de2-4ef9-8fc4-8306c215bc27"

    response = client.post("/api/companies/config", json={
        "name": "Prueba",
        "whatsapp_phone_number_id": "123",
        "whatsapp_access_token": "abc",
        "mercadopago_access_token": "",
        "system_prompt": "Hola"
    })
    
    print(response.status_code)
    print(response.text)

if __name__ == "__main__":
    test_config()
