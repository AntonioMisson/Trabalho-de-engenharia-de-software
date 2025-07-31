from flask import Flask, render_template, request, redirect, url_for, make_response
import os
import json

app = Flask(__name__, static_url_path='/static', static_folder='static')

app = Flask(__name__)
USUARIOS_PATH = "usuarios.json"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    mensagem = ""
    if request.method == "POST":
        email_ou_usuario = request.form.get("email_ou_usuario")
        senha = request.form.get("senha")
        lembrar = request.form.get("lembrar") == "on"

        if os.path.exists(USUARIOS_PATH):
            with open(USUARIOS_PATH, "r") as f:
                usuarios = json.load(f)
        else:
            usuarios = []

        usuario_encontrado = None
        for usuario in usuarios:
            if usuario["email"] == email_ou_usuario or usuario["usuario"] == email_ou_usuario:
                usuario_encontrado = usuario
                break

        if usuario_encontrado:
            if usuario_encontrado["senha"] == senha:
                response = make_response(redirect(url_for("home")))
                if lembrar:
                    response.set_cookie("remembered_user", email_ou_usuario, max_age=60*60*24*30)
                return response
            else:
                mensagem = "Senha incorreta."
        else:
            mensagem = 'Conta não encontrada. <a href="' + url_for("cadastro") + '">Cadastrar-se</a>'

    return render_template("login.html", mensagem=mensagem)

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

        if os.path.exists(USUARIOS_PATH):
            with open(USUARIOS_PATH, "r") as f:
                usuarios = json.load(f)
        else:
            usuarios = []

        usuarios.append(novo_usuario)

        with open(USUARIOS_PATH, "w") as f:
            json.dump(usuarios, f, indent=2)

        return redirect(url_for("login"))

    return render_template("cadastro.html")

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/perfil")
def perfil():
    return render_template("perfil.html")

@app.route("/arquivo", methods=["GET", "POST"])
def enviar_atividade():
    if request.method == "POST":
        # Aqui você pode salvar arquivos e dados, exemplo:
        monitor = request.form.get("monitor")
        descricao = request.form.get("descricao")
        arquivo = request.files.get("arquivo")

        if arquivo:
            caminho = os.path.join("uploads", arquivo.filename)
            arquivo.save(caminho)

        return redirect(url_for("home"))

    return render_template("arquivo.html")

DATA_FILE = 'agendamentos.json'

# Função utilitária para carregar/agendar
def carregar_agendamentos():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({}, f)
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def salvar_agendamento(horario, dia):
    dados = carregar_agendamentos()
    dados.setdefault(horario, {})[dia] = "ocupado"
    with open(DATA_FILE, 'w') as f:
        json.dump(dados, f)

@app.route('/')
def index():
    agendados = carregar_agendamentos()
    return render_template('index.html', agendados=agendados)

@app.route('/agendar', methods=['POST'])
def agendar():
    data = request.get_json()
    horario = data['horario']
    dia = data['dia']
    salvar_agendamento(horario, dia)
    return jsonify({'status': 'sucesso'})

if __name__ == '__main__':
    app.run(debug=True)