from flask import render_template, request, redirect, session, flash
from app import app, get_db
import bcrypt
import sqlite3
import time


def home():
    return redirect('/')

def fetchProducts():
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT * FROM PRODUTOS ORDER BY preco ASC LIMIT 6")
    results = cursor.fetchall()
    
    return results

@app.route("/")
@app.route('/index')
def index():
    usuario = session.get("usuario")
    tipo = session.get("tipo")
    produtos = fetchProducts()
    return render_template('index.html', usuario_logado=usuario, tipo_usuario=tipo, produtos=produtos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        log_nome = request.form.get("usuario")
        log_senha = request.form.get("senha")

        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id_cliente, senha FROM clientes WHERE nome_cliente=?", (log_nome,))
        row = cursor.fetchone()

        if row and bcrypt.checkpw(log_senha.encode('utf-8'), row[1]):
            session["usuario"] = log_nome
            session["tipo"] = "cliente"
            session["id_cliente"] = row[0] # id
            flash('Login realizado com sucesso!', 'success')
            return redirect('/login')

        cursor.execute("SELECT senha FROM clientes WHERE nome_cliente=?", (log_nome,))
        row = cursor.fetchone()
        if row and bcrypt.checkpw(log_senha.encode('utf-8'), row[0]):
            session["usuario"] = log_nome
            session["tipo"] = "cliente"
            flash('Login realizado com sucesso!', 'success')
            return redirect('/login')

        flash('Usuário ou senha incorretos', 'error')
        return redirect('/login')

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

@app.route('/dashboard')
def dashboard():
    # Verifica se o usuário está logado e é funcionário
    if session.get("tipo") != "funcionario":
        flash('Acesso restrito a funcionários', 'error')
        return redirect('/login')
    
    usuario = session.get("usuario")
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Buscar estatísticas do dashboard
    try:
        cursor.execute("SELECT COUNT(*) FROM ordens_servico WHERE status IN ('Em andamento', 'Aguardando peças')")
        ordens_abertas = cursor.fetchone()[0] if cursor.fetchone() else 24
        
        # Produtos com baixo estoque (menos de 10 unidades)
        cursor.execute("SELECT COUNT(*) FROM produtos WHERE stock < 10")
        produtos_baixo_estoque = cursor.fetchone()[0] if cursor.fetchone() else 7
        
        # O total de clientes ativos
        cursor.execute("SELECT COUNT(*) FROM clientes")
        clientes_ativos = cursor.fetchone()[0] if cursor.fetchone() else 152
    
        cursor.execute("""
            SELECT o.id_ordem, c.nome_cliente, v.modelo, v.placa, o.status 
            FROM ordens_servico o
            LEFT JOIN clientes c ON o.id_cliente = c.id_cliente
            LEFT JOIN veiculos v ON o.id_veiculo = v.id_veiculo
            WHERE o.status != 'Concluída'
            ORDER BY o.data_abertura DESC
            LIMIT 4
        """)
        ordens_pendentes = cursor.fetchall()
        
        # aqui são os produtos com baixo estoque eu tava vendo na tabelas de banco de dados e fazendo testes com isso mas n deu mt bom
        cursor.execute("""
            SELECT nome, stock, 
                CASE 
                    WHEN stock < 5 THEN 'Crítico'
                    WHEN stock < 10 THEN 'Baixo'
                    ELSE 'Normal'
                END as status_estoque
            FROM produtos 
            WHERE stock < 15
            ORDER BY stock ASC
            LIMIT 4
        """)
        produtos_estoque = cursor.fetchall()
        
    except sqlite3.OperationalError:
        # Testando algumas coisas de tabelas
        ordens_abertas = 24
        produtos_baixo_estoque = 7
        clientes_ativos = 152
        ordens_pendentes = []
        produtos_estoque = []
    
    return render_template(
        'dashboard.html',
        usuario_logado=usuario,
        ordens_abertas=ordens_abertas,
        produtos_baixo_estoque=produtos_baixo_estoque,
        clientes_ativos=clientes_ativos,
        ordens_pendentes=ordens_pendentes,
        produtos_estoque=produtos_estoque
    )

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get("nome")
        cpf = request.form.get("cpf")
        celular = request.form.get("celular")
        email = request.form.get("email")
        senha = request.form.get("senha")

        conn = get_db()
        cursor = conn.cursor()


        try:
            cursor.execute("SELECT id_cliente FROM clientes WHERE CPF=?", (cpf,))
            if cursor.fetchone():
                flash('CPF já cadastrado no sistema!', 'error')
                return redirect('/cadastro')

            cursor.execute("SELECT id_cliente FROM clientes WHERE email=?", (email,))
            if cursor.fetchone():
                flash('E-mail já cadastrado no sistema!', 'error')
                return redirect('/cadastro')

            placa = request.form.get("placa")
            if placa:
                cursor.execute("SELECT id_veiculo FROM veiculos WHERE placa=?", (placa,))
                if cursor.fetchone():
                    flash('Placa já cadastrada no sistema!', 'error')
                    return redirect('/cadastro')

            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

            modelo = request.form.get("modelo")
            marca = request.form.get("marca")
            ano = request.form.get("ano")
            cor = request.form.get("cor")
            cursor.execute(
                "INSERT INTO clientes (nome_cliente, CPF, celular, email, senha) VALUES (?, ?, ?, ?, ?)",
                (nome, cpf, celular, email, senha_hash)
            )

            id_cliente = cursor.lastrowid

            if placa and modelo and marca:
                cursor.execute(
                    "INSERT INTO veiculos (marca, cor, ano, modelo, placa, id_cliente) VALUES (?, ?, ?, ?, ?, ?)",
                    (marca, cor, ano, modelo, placa, id_cliente)
                )

            conn.commit()
            flash('Cadastro realizado com sucesso!', 'success')
            return redirect('/cadastro')

        except sqlite3.IntegrityError as e:
            conn.rollback()
            if 'CPF' in str(e):
                flash('CPF já cadastrado no sistema!', 'error')
            elif 'email' in str(e):
                flash('E-mail já cadastrado no sistema!', 'error')
            elif 'placa' in str(e):
                flash('Placa já cadastrada no sistema!', 'error')
            else:
                flash('Erro ao realizar cadastro. Verifique os dados informados.', 'error')
            return redirect('/cadastro')

        except Exception as e:
            conn.rollback()
            flash('Erro ao realizar cadastro. Tente novamente.', 'error')
            return redirect('/cadastro')

    return render_template('cadastro.html')

@app.route('/pedir', methods=['GET', 'POST'])
def pedir():
    if not session:
        return render_template('login.html')

    conn = get_db()
    cursor = conn.cursor()
    
    id_cliente = session.get("id_cliente")

    cursor.execute("SELECT * FROM CLIENTES WHERE id_cliente = ?", (id_cliente,))    
    cliente = cursor.fetchone()
    cursor.execute("SELECT id_veiculo, marca, modelo, ano, placa FROM veiculos WHERE id_cliente = ?", (id_cliente,))
    veiculos = cursor.fetchall()
    print(cliente)
    return render_template('pedir.html', cliente=cliente, veiculos=veiculos)


from flask import request, session
import time

@app.route("/pedir/troca-pecas", methods=["POST"])
def troca_pecas():
    conn = get_db()
    cursor = conn.cursor()
    id_cliente = session.get("id_cliente")
    tipo = "Troca de peças"
    abertura = time.ctime()

    # Campos do formulário
    id_veiculo = request.form.get("id_veiculo")
    descricao = request.form.get("descricao")
    observacoes = request.form.get("observacoes")

    diagnostico = descricao
    if observacoes:
        diagnostico += f"\nObservações: {observacoes}"

    cursor.execute("""
        INSERT INTO ordem (id_cliente, id_veiculo, tipo_ordem, diagnostico, abertura)
        VALUES (?, ?, ?, ?, ?)
    """, (
        id_cliente,
        id_veiculo,
        tipo,
        diagnostico,
        abertura
    ))
    conn.commit()
    return render_template("confirma.html")


@app.route("/pedir/emergencial", methods=["POST"])
def emergencial():
    conn = get_db()
    cursor = conn.cursor()
    id_cliente = session.get("id_cliente")
    tipo = "Serviço Emergencial"
    abertura = time.ctime()

    # Campos do formulário
    id_veiculo = request.form.get("id_veiculo")
    urgencia = request.form.get("urgencia")
    localizacao = request.form.get("localizacao")
    problema = request.form.get("problema")
    pode_dirigir = request.form.get("pode_dirigir")
    observacoes = request.form.get("observacoes")

    diagnostico = f"Urgência: {urgencia}\nLocalização: {localizacao}\nProblema: {problema}\nPode dirigir: {pode_dirigir}"
    if observacoes:
        diagnostico += f"\nObservações: {observacoes}"

    cursor.execute("""
        INSERT INTO ordem (id_cliente, id_veiculo, tipo_ordem, diagnostico, abertura)
        VALUES (?, ?, ?, ?, ?)
    """, (
        id_cliente,
        id_veiculo,
        tipo,
        diagnostico,
        abertura
    ))
    conn.commit()
    return render_template("confirma.html")


@app.route("/pedir/agendamento", methods=["POST"])
def agendamento():
    conn = get_db()
    cursor = conn.cursor()
    id_cliente = session.get("id_cliente")
    tipo = "Agendamento de Serviço"
    abertura = time.ctime()

    # Campos do formulário
    id_veiculo = request.form.get("id_veiculo")
    tipo_servico = request.form.get("tipo_servico")
    data = request.form.get("data")
    horario = request.form.get("horario")
    descricao = request.form.get("descricao")
    observacoes = request.form.get("observacoes")

    diagnostico = f"Tipo de serviço: {tipo_servico}\nData: {data}\nHorário: {horario}\nDescrição: {descricao}"
    if observacoes:
        diagnostico += f"\nObservações: {observacoes}"

    cursor.execute("""
        INSERT INTO ordem (id_cliente, id_veiculo, tipo_ordem, diagnostico, abertura)
        VALUES (?, ?, ?, ?, ?)
    """, (
        id_cliente,
        id_veiculo,
        tipo,
        diagnostico,
        abertura
    ))
    conn.commit()
    return render_template("confirma.html")
