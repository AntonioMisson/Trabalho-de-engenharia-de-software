from flask import Flask, render_template, request, redirect, url_for, make_response
import os
import json

app = Flask(
    __name__,
    static_url_path='/static',
    static_folder='static'
)

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

        usuarios = []
        if os.path.exists(USUARIOS_PATH):
            with open(USUARIOS_PATH, "r") as f:
                usuarios = json.load(f)

        usuario_encontrado = next(
            (u for u in usuarios if u["email"] == email_ou_usuario or u["usuario"] == email_ou_usuario),
            None
        )

        if usuario_encontrado:
            if usuario_encontrado["senha"] == senha:
                response = make_response(redirect(url_for("home")))
                if lembrar:
                    response.set_cookie("remembered_user", email_ou_usuario, max_age=60*60*24*30)
                return response
            else:
                mensagem = "Senha incorreta."
        else:
            mensagem = (
                'Conta não encontrada. '
                f'<a href="{ url_for("cadastro") }">Cadastrar-se</a>'
            )

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

        usuarios = []
        if os.path.exists(USUARIOS_PATH):
            with open(USUARIOS_PATH, "r") as f:
                usuarios = json.load(f)

        usuarios.append(novo_usuario)
        with open(USUARIOS_PATH, "w") as f:
            json.dump(usuarios, f, indent=2)

        return redirect(url_for("login"))

    return render_template("cadastro.html")

@app.route("/perfil")
def perfil():
    return render_template("perfil.html")

@app.route("/arquivo", methods=["GET", "POST"])
def enviar_atividade():
    if request.method == "POST":
        monitor = request.form.get("monitor")
        descricao = request.form.get("descricao")
        arquivo = request.files.get("arquivo")

        if arquivo:
            uploads_dir = "uploads"
            os.makedirs(uploads_dir, exist_ok=True)
            caminho = os.path.join(uploads_dir, arquivo.filename)
            arquivo.save(caminho)

        return redirect(url_for("home"))

    return render_template("arquivo.html")

@app.route("/horario")
def horario():
    dias      = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
    horarios  = ["07:00","08:00","09:00","10:00","11:00","13:00","14:00","15:00","16:00","17:00"]
    # Exemplo de agendados: {"Segunda-0700": "alice", "Terça-0800": "bob", ...}
    agendados = {...}
    usuario   = "alice"      # ou session["user"], como você estiver fazendo
    return render_template(
      "horario.html",
      dias=dias,
      horarios=horarios,
      agendados=agendados,
      usuario=usuario
    )


if __name__ == "__main__":
    app.run(debug=True)
