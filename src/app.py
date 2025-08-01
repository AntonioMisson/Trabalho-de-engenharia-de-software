from flask import Flask, render_template, request, redirect, url_for, make_response
import os
import json
from flask import Response
import datetime


app = Flask(
    __name__,
    static_url_path='/static',
    static_folder='static'
)

USUARIOS_PATH = "usuarios.json"

def aplicar_charset_utf8(response):
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    mensagem = ""
    sucesso = False

    if request.method == "POST":
        print("POST recebido")
        email_ou_usuario = request.form.get("email_ou_usuario")
        senha = request.form.get("senha")
        lembrar = request.form.get("lembrar") == "on"

        # Lê arquivo de usuários
        if os.path.exists(USUARIOS_PATH):
            with open(USUARIOS_PATH, "r") as f:
                usuarios = json.load(f)
        else:
            usuarios = []

        usuario_encontrado = next(
            (u for u in usuarios if u.get("email") == email_ou_usuario or u.get("usuario") == email_ou_usuario),
            None
        )

        if usuario_encontrado:
            if usuario_encontrado["senha"] == senha:
                response = make_response(redirect(url_for("main")))
                if lembrar:
                    response.set_cookie("remembered_user", email_ou_usuario, max_age=60*60*24*30)
                return response
            else:
                mensagem = "Senha incorreta."
        else:
            mensagem = "Usuário não encontrado. <a href='{}'>Cadastrar-se</a>".format(url_for("cadastro"))

    return render_template("login.html", mensagem=mensagem, sucesso=sucesso)

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")
        usuario = request.form.get("usuario")
        tipo = request.form.get("tipo")

        novo_usuario = {
            "email": email,
            "senha": senha,
            "usuario": usuario,
            "tipo": tipo
        }

        usuarios = []
        if os.path.exists(USUARIOS_PATH):
            with open(USUARIOS_PATH, "r") as f:
                usuarios = json.load(f)

        usuarios.append(novo_usuario)
        with open(USUARIOS_PATH, "w") as f:
            json.dump(usuarios, f, indent=2)

        return redirect(url_for("login"))

    return render_template("cadastro.html")


@app.route("/arquivo", methods=["GET", "POST"])
def arquivo():
    monitores = []

    # Carregar usuários e perfis
    if os.path.exists(USUARIOS_PATH):
        with open(USUARIOS_PATH, "r", encoding="utf-8") as f:
            usuarios = json.load(f)
    else:
        usuarios = []

    if os.path.exists(PERFIS_PATH):
        with open(PERFIS_PATH, "r", encoding="utf-8") as f:
            perfis = json.load(f)
    else:
        perfis = {}

    # Construir lista de monitores
    for usuario in usuarios:
        if usuario.get("tipo") == "monitor":
            email = usuario.get("email")
            perfil = perfis.get(email, {})
            nome = perfil.get("nome", email)
            curso = perfil.get("curso", "Curso não informado")
            disciplina = perfil.get("disciplina", "Disciplina não informada")
            monitores.append({
                "email": email,
                "nome": nome,
                "curso": curso,
                "disciplina": disciplina
            })

    if request.method == "POST":
        monitor = request.form.get("monitor")
        descricao = request.form.get("descricao")
        arquivo = request.files.get("arquivo")

        if arquivo:
            uploads_dir = "uploads"
            os.makedirs(uploads_dir, exist_ok=True)
            caminho = os.path.join(uploads_dir, arquivo.filename)
            arquivo.save(caminho)

        return redirect(url_for("main"))

    return render_template("arquivo.html", monitores=monitores)

@app.route("/main")
def main():
    usuario = request.cookies.get("remembered_user")
    if not usuario:
        return redirect(url_for("login"))
    return render_template("main.html", usuario=usuario)

PERFIS_PATH = "perfis.json"

def carregar_perfis():
    if os.path.exists(PERFIS_PATH):
        with open(PERFIS_PATH, "r") as f:
            return json.load(f)
    return {}

def salvar_perfis(perfis):
    with open(PERFIS_PATH, "w") as f:
        json.dump(perfis, f, indent=2)

@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    email = request.cookies.get("remembered_user")
    if not email:
        return redirect(url_for("login"))

    perfis = carregar_perfis()
    dados = perfis.get(email, {})

    if request.method == "POST":
        dados["nome"] = request.form.get("nome")
        dados["telefone"] = request.form.get("telefone")
        dados["curso"] = request.form.get("curso")
        dados["email"] = request.form.get("email")
        perfis[email] = dados
        salvar_perfis(perfis)
        return redirect(url_for("main"))

    return render_template("perfil.html", dados=dados, usuario=email)

@app.route("/monitores")
def monitores():
    USUARIOS_PATH = "usuarios.json"
    PERFIS_PATH = "perfis.json"

    # Carrega arquivos JSON com codificação correta
    with open(USUARIOS_PATH, "r", encoding="utf-8") as f:
        usuarios = json.load(f)

    with open(PERFIS_PATH, "r", encoding="utf-8") as f:
        perfis = json.load(f)

    # Filtra os usuários do tipo "monitor" e junta os dados do perfil
    monitores = []
    for usuario in usuarios:
        if usuario.get("tipo") == "monitor":
            email = usuario.get("email")
            dados_perfil = perfis.get(email, {})

            monitores.append({
                "nome": dados_perfil.get("nome", usuario.get("usuario", "")),
                "email": email,
                "disciplina": dados_perfil.get("disciplina", "N/A"),
                "curso": dados_perfil.get("curso", "N/A"),
                "disponibilidade": dados_perfil.get("disponibilidade", "N/A")
            })

    return render_template("monitores.html", monitores=monitores)

@app.route("/FAQs")
def FAQs():
    return render_template("FAQs.html")

@app.route("/avaliação_aluno", methods=["GET", "POST"])
def avaliação_aluno():
    # Carrega usuários e perfis
    with open("usuarios.json", "r", encoding="utf-8") as f:
        usuarios = json.load(f)

    with open("perfis.json", "r", encoding="utf-8") as f:
        perfis = json.load(f)

    alunos = []
    for usuario in usuarios:
        if usuario.get("tipo") == "aluno":
            email = usuario["email"]
            nome = perfis.get(email, {}).get("nome", email)
            alunos.append({"email": email, "nome": nome})

    if request.method == "POST":
        nome = request.form.get("studentName")
        classificacao = request.form.get("classification")

        nova_avaliacao = {"nome": nome, "classificacao": classificacao}

        avaliacoes_path = "avaliacoes.json"
        if os.path.exists(avaliacoes_path):
            with open(avaliacoes_path, "r", encoding="utf-8") as f:
                avaliacoes = json.load(f)
        else:
            avaliacoes = []

        avaliacoes.append(nova_avaliacao)

        with open(avaliacoes_path, "w", encoding="utf-8") as f:
            json.dump(avaliacoes, f, indent=2, ensure_ascii=False)

        return redirect(url_for("main"))

    return render_template("avaliação_aluno.html", alunos=alunos)

FEEDBACKS_PATH = "feedbacks.json"

@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    email = request.cookies.get("remembered_user") or "anônimo"

    if request.method == "POST":
        rating     = request.form.get("rating")
        sugestao   = request.form.get("sugestao")
        comentario = request.form.get("comentario")

        novo_feedback = {
            "usuario": email,
            "rating": rating,
            "sugestao": sugestao,
            "comentario": comentario
        }

        feedbacks = []
        if os.path.exists(FEEDBACKS_PATH):
            with open(FEEDBACKS_PATH, "r", encoding="utf-8") as f:
                feedbacks = json.load(f)

        feedbacks.append(novo_feedback)

        with open(FEEDBACKS_PATH, "w", encoding="utf-8") as f:
            json.dump(feedbacks, f, indent=2, ensure_ascii=False)

        return redirect(url_for("main"))

    return render_template("feedback.html") 
# ─── Helpers para ler e gravar JSON ────────────────────────────────────
def carregar_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

# Variáveis de rota de mensagens
MESSAGES_PATH   = "mensagens.json"
UPLOADS_FOLDER  = "uploads"
import datetime
os.makedirs(UPLOADS_FOLDER, exist_ok=True)


# ─── Nova rota de Mensagens ───────────────────────────────────────────
@app.route("/mensagens")
def lista_conversas():
    usuario = request.cookies.get("remembered_user")
    if not usuario:
        return redirect(url_for("login"))

    usuarios = carregar_json(USUARIOS_PATH)
    perfis   = carregar_perfis()

    # se for aluno, mostrar monitores; se for monitor, mostrar alunos
    tipo = next((u["tipo"] for u in usuarios if u["email"]==usuario), None)
    if tipo=="aluno":
        alvos = [u for u in usuarios if u["tipo"]=="monitor"]
    else:
        alvos = [u for u in usuarios if u["tipo"]=="aluno"]

    threads = [{
        "email": u["email"],
        "nome": perfis.get(u["email"],{}).get("nome",u["email"])
    } for u in alvos]

    return render_template("lista_conversas.html", threads=threads)


# ─── 2) Chat com um contato específico ──────────────────────────────
@app.route("/mensagens/<contato_email>", methods=["GET","POST"])
def mensagens(contato_email):
    usuario = request.cookies.get("remembered_user")
    if not usuario:
        return redirect(url_for("login"))

    todas = carregar_json(MESSAGES_PATH)
    conversa = [
      m for m in todas
      if {m["from"],m["to"]} == {usuario, contato_email}
    ]

    if request.method=="POST":
        texto   = request.form.get("comentario","").strip()
        arquivo = request.files.get("arquivo")
        foto    = request.files.get("foto")

        anexo = None
        for up in (arquivo,foto):
            if up and up.filename:
                fn  = f"{int(datetime.datetime.now().timestamp())}_{up.filename}"
                dst = os.path.join(UPLOADS_FOLDER, fn)
                up.save(dst)
                anexo = url_for("static", filename=f"../{dst}")
                break

        nova = {
            "from": usuario,
            "to":   contato_email,
            "when": datetime.datetime.now().isoformat(),
            "text": texto,
            "anexo": anexo
        }
        todas.append(nova)
        salvar_json(MESSAGES_PATH, todas)
        return redirect(url_for("mensagens", contato_email=contato_email))

    perfis   = carregar_perfis()
    nome_out = perfis.get(contato_email,{}).get("nome", contato_email)
    return render_template("mensagens.html",
                           conversa=conversa,
                           aluno=usuario,
                           monitor=contato_email,
                           nome_mon=nome_out)

AGENDAMENTOS_PATH = "agendamentos.json"

def carregar_agendamentos():
    if os.path.exists(AGENDAMENTOS_PATH):
        with open(AGENDAMENTOS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_agendamentos(agendamentos):
    with open(AGENDAMENTOS_PATH, "w", encoding="utf-8") as f:
        json.dump(agendamentos, f, indent=2, ensure_ascii=False)

@app.route("/horario", methods=["GET", "POST"])
def horario():
    usuario = request.cookies.get("remembered_user")
    if not usuario:
        return redirect(url_for("login"))

    agendados = carregar_agendamentos()

    if request.method == "POST":
        dia = request.form.get("dia")
        hora = request.form.get("hora")
        chave = f"{dia}-{hora.replace(':', '')}"

        # Se ainda não estiver agendado, salva
        if chave not in agendados:
            agendados[chave] = usuario
            salvar_agendamentos(agendados)

        return redirect(url_for("horario"))  # Redireciona após o post

    dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
    horarios = ["07:00","08:00","09:00","10:00","11:00","13:00","14:00","15:00","16:00","17:00"]

    return render_template("horario.html",
                           dias=dias,
                           horarios=horarios,
                           agendados=agendados,
                           usuario=usuario)


if __name__ == "__main__":
    app.run(debug=True)
