from src.app import app

def test_index_route():
    test_client = app.test_client()
    response = test_client.get('/')
    assert response.status_code == 200
    assert b"Bem-vindo ao Sistema de Monitoria" in response.data