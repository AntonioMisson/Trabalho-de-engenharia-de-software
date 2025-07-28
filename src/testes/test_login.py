import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app
import json
import os

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Bem vindo' in response.data or b'<html' in response.data

def test_login_get(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'login' in response.data.lower()

def test_cadastro_post(client):
    dados = {
        "email": "teste@exemplo.com",
        "senha": "123456",
        "usuario": "testuser",
        "tipo": "aluno"
    }

    response = client.post('/cadastro', data=dados, follow_redirects=True)
    assert response.status_code == 200
    assert b'login' in response.data.lower()

def test_login_post_sucesso(client):
    # Certifique-se de que o usuário acima esteja no usuarios.json
    dados = {
        "email_ou_usuario": "testuser",
        "senha": "123456",
        "lembrar": "on"
    }
    response = client.post('/login', data=dados, follow_redirects=True)
    assert response.status_code == 200
    assert b'Bem vindo' in response.data or b'<html' in response.data

def test_rota_perfil(client):
    response = client.get('/perfil')
    assert response.status_code == 200

def test_rota_enviar(client):
    response = client.get('/arquivo')
    assert response.status_code == 200