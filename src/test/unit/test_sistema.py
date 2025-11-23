import pytest
import os
import sys
import json

# Corrigir caminho para importar src.app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.app import app, USUARIOS_PATH, PERFIS_PATH, AGENDAMENTOS_PATH, MESSAGES_PATH, FEEDBACKS_PATH


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# ─── Criação de usuário de teste ─────────────────────────────
def criar_usuario_teste():
    usuarios = []
    if os.path.exists(USUARIOS_PATH):
        with open(USUARIOS_PATH, "r", encoding="utf-8") as f:
            usuarios = json.load(f)

    novo = {
        "email": "teste@exemplo.com",
        "senha": "123456",
        "usuario": "testuser",
        "tipo": "aluno"
    }

    if not any(u["email"] == novo["email"] for u in usuarios):
        usuarios.append(novo)
        with open(USUARIOS_PATH, "w", encoding="utf-8") as f:
            json.dump(usuarios, f, indent=2, ensure_ascii=False)

    perfis = {}
    if os.path.exists(PERFIS_PATH):
        with open(PERFIS_PATH, "r", encoding="utf-8") as f:
            perfis = json.load(f)

    perfis[novo["email"]] = {
        "nome": "Aluno Teste",
        "curso": "Engenharia",
        "telefone": "123456789"
    }

    with open(PERFIS_PATH, "w", encoding="utf-8") as f:
        json.dump(perfis, f, indent=2, ensure_ascii=False)

# ─── Autenticação simulada ───────────────────────────────────
def autenticar(client, email="teste@exemplo.com"):
    client.set_cookie("remembered_user", email)


# ─── Testes públicos ─────────────────────────────────────────
def test_home(client):
    response = client.get('/')
    assert response.status_code == 200

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
    criar_usuario_teste()
    dados = {
        "email_ou_usuario": "testuser",
        "senha": "123456",
        "lembrar": "on"
    }
    response = client.post('/login', data=dados, follow_redirects=True)
    assert response.status_code == 200
    assert b'<html' in response.data

# ─── Testes autenticados ─────────────────────────────────────
def test_rota_perfil(client):
    criar_usuario_teste()
    autenticar(client)
    response = client.get('/perfil')
    assert response.status_code == 200
    assert b'nome' in response.data.lower()

def test_arquivo_get(client):
    autenticar(client)
    response = client.get('/arquivo')
    assert response.status_code == 200

def test_feedback_post(client):
    autenticar(client)
    data = {
        "rating": "5",
        "sugestao": "Muito bom",
        "comentario": "Sistema ótimo"
    }
    response = client.post('/feedback', data=data, follow_redirects=True)
    assert response.status_code == 200

def test_mensagens_lista(client):
    autenticar(client)
    response = client.get('/mensagens')
    assert response.status_code == 200

def test_avaliacao_aluno_get(client):
    autenticar(client)
    response = client.get('/avaliação_aluno')  # corrigido: sem acento
    assert response.status_code == 200

def test_horario_get(client):
    autenticar(client)
    response = client.get('/horario')
    assert response.status_code == 200

def test_faqs(client):
    response = client.get('/FAQs')
    assert response.status_code == 200

def test_monitores(client):
    response = client.get('/monitores')
    assert response.status_code == 200

def test_saiba_mais(client):
    response = client.get('/saiba_mais')
    assert response.status_code == 200
    assert b'Sobre o Projeto' in response.data