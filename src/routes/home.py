from flask import render_template, request, redirect, session
from app import app, get_db
import bcrypt

def home():
    usuario = session.get("usuario")
    if not usuario:
        return redirect('/login')

    conn = get_db()
    produtos = conn.execute(
        "SELECT id_produto, nome, preco, stock FROM produtos WHERE stock > 0 ORDER BY nome LIMIT 6"
    ).fetchall()

    return render_template('index.html', produtos=produtos, usuario_logado=usuario)


@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        log_nome = request.form.get("usuario")
        log_senha = request.form.get("senha")

        conn = get_db()
        cursor = conn.cursor()
        # funcionario
        cursor.execute("SELECT senha, nivel_de_acesso FROM funcionarios WHERE nome_funcionario=?", (log_nome,))
        row = cursor.fetchone()
        print(log_senha)
        
        if row and bcrypt.checkpw(log_senha.encode('utf-8'), row[0]):
            session["usuario"] = log_nome
            session["tipo"] = "funcionario"
            session["cargo"] = row[1] #nivel de acesso
            print("SESSION ATUAL:", session)
            return redirect('/home')

        # ---- Cliente ----
        cursor.execute("SELECT senha FROM clientes WHERE nome_cliente=?", (log_nome,))
        row = cursor.fetchone()
        if row and bcrypt.checkpw(log_senha.encode('utf-8'), row[0]):
            session["usuario"] = log_nome
            session["tipo"] = "cliente"
            return redirect('/home')

        return "Usuário ou senha incorretos"

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/admin')
def admin():
    if session.get("tipo") != "funcionario":
        return redirect('/login')

    usuario = session.get("usuario")

    conn = get_db()
    produtos = conn.execute(
        "SELECT id_produto, nome, preco, stock FROM produtos ORDER BY nome"
    ).fetchall()

    clientes = conn.execute(
        "SELECT id_cliente, nome_cliente, email, CPF FROM clientes ORDER BY nome_cliente"
    ).fetchall()

    return render_template(
        'admin.html',
        usuario_logado=usuario,
        produtos=produtos,
        clientes=clientes
    )


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get("nome")
        cpf = request.form.get("cpf")
        celular = request.form.get("celular")
        email = request.form.get("email")
        senha = request.form.get("senha")

        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

        conn = get_db()
        cursor = conn.cursor()

        tipo_usuario = request.form.get("tipo_usuario")

        if tipo_usuario == "cliente":
            placa = request.form.get("placa")
            modelo = request.form.get("modelo")
            marca = request.form.get("marca")
            ano = request.form.get("ano")
            cor = request.form.get("cor")

            cursor.execute(
                "INSERT INTO clientes (nome_cliente, CPF, celular, email, senha) VALUES (?, ?, ?, ?, ?)",
                (nome, cpf, celular, email, senha_hash)
            )

            cursor.execute(
                "INSERT INTO veiculos (marca, cor, ano, modelo, placa) VALUES (?, ?, ?, ?, ?)",
                (marca, cor, ano, modelo, placa)
            )

            conn.commit()
            return "Cadastro do cliente feito com sucesso"

        
        if tipo_usuario == "funcionario":
            cargo = request.form.get("cargo")

            cursor.execute(
                "INSERT INTO funcionarios (nome_funcionario, nivel_de_acesso, senha) VALUES (?, ?, ?)",
                (nome, cargo, senha_hash)
            )

            conn.commit()
            return "Cadastro do funcionário feito com sucesso"

    return render_template('cadastro.html')

