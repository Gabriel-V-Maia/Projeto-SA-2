from flask import render_template, request, redirect, session, flash, jsonify
from app import app, get_db
import bcrypt
import sqlite3
import time
from datetime import datetime, timedelta

def home():
    return redirect('/')

@app.route('/admin')
@app.route('/dashboard')
def dashboard():
    if session.get("tipo") != "funcionario":
        flash('Acesso restrito a funcionários', 'error')
        return redirect('/auth/login')
    
    usuario = session.get("usuario")
    nivel_acesso = session.get("nivel_acesso", "1")
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM ordem WHERE status IN ('EM ANDAMENTO', 'AGUARDANDO PEÇA', 'EM ABERTO')")
        ordens_abertas = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM produtos WHERE stock < 10")
        produtos_baixo_estoque = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM clientes")
        clientes_ativos = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT 
                strftime('%Y-%m', o.abertura) as mes,
                SUM(o.orcamento) as receita
            FROM ordem o
            WHERE o.abertura IS NOT NULL 
            AND o.abertura >= date('now', '-6 months')
            GROUP BY strftime('%Y-%m', o.abertura)
            ORDER BY mes
        """)
        receita_mensal = cursor.fetchall()

        meses = []
        receitas = []
        for row in receita_mensal:
            if row[0]:
                mes_formatado = datetime.strptime(row[0], '%Y-%m').strftime('%b')
                meses.append(mes_formatado)
                receitas.append(float(row[1]) if row[1] else 0)

        while len(meses) < 6:
            meses.insert(0, '')
            receitas.insert(0, 0)

        receita_mes_atual = receitas[-1] if receitas else 0

        cursor.execute("""
            SELECT o.id_ordem, c.nome_cliente, v.modelo, v.placa, o.status 
            FROM ordem o
            LEFT JOIN clientes c ON o.id_cliente = c.id_cliente
            LEFT JOIN veiculos v ON o.id_veiculo = v.id_veiculo
            WHERE o.status != 'CONCLUIDO'
            ORDER BY o.abertura DESC
            LIMIT 4
        """)
        ordens_pendentes = cursor.fetchall()
        
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

        cursor.execute("""
            SELECT o.id_ordem, c.nome_cliente, o.tipo_ordem, o.abertura
            FROM ordem o
            LEFT JOIN clientes c ON o.id_cliente = c.id_cliente
            ORDER BY o.abertura DESC
            LIMIT 5
        """)
        atividades_recentes = cursor.fetchall()
        
    except sqlite3.Error as e:
        print(f"Erro no banco: {e}")
        ordens_abertas = 0
        produtos_baixo_estoque = 0
        clientes_ativos = 0
        meses = ['Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        receitas = [32000, 28500, 35000, 41000, 37200, 45800]
        receita_mes_atual = 45800
        ordens_pendentes = []
        produtos_estoque = []
        atividades_recentes = []
    
    return render_template(
        'admin/admin.html',
        usuario_logado=usuario,
        nivel_acesso=nivel_acesso,
        ordens_abertas=ordens_abertas,
        produtos_baixo_estoque=produtos_baixo_estoque,
        clientes_ativos=clientes_ativos,
        receita_mes_atual=receita_mes_atual,
        meses=meses,
        receitas=receitas,
        ordens_pendentes=ordens_pendentes,
        produtos_estoque=produtos_estoque,
        atividades_recentes=atividades_recentes
    )

def fetch_products():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM produtos ORDER BY preco ASC LIMIT 6")
    results = cursor.fetchall()
    return results

@app.route("/")
@app.route('/index')
@app.route('/home')
def index():
    usuario = session.get("usuario")
    tipo = session.get("tipo")
    produtos = fetch_products()
    return render_template('index.html', usuario_logado=usuario, tipo_usuario=tipo, produtos=produtos)

@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        log_email = request.form.get("email")
        log_senha = request.form.get("senha")

        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id_cliente, senha FROM clientes WHERE email=?", (log_email,))
        row = cursor.fetchone()

        if row and bcrypt.checkpw(log_senha.encode('utf-8'), row[1]):
            cursor.execute("SELECT nome_cliente FROM clientes WHERE email=?", (log_email,))
            session["usuario"] = cursor.fetchone()[0]
            session["tipo"] = "cliente"
            session["id_cliente"] = row[0]
            flash('Login realizado com sucesso!', 'success')
            return redirect('/')

        cursor.execute("SELECT id_funcionario, senha, nivel_de_acesso FROM funcionarios WHERE nome_funcionario=?", (log_email,))
        row = cursor.fetchone()

        if row and bcrypt.checkpw(log_senha.encode('utf-8'), row[1]):
            cursor.execute("SELECT nome_funcionario FROM funcionarios WHERE nome_funcionario=?", (log_email,))
            session["usuario"] = cursor.fetchone()[0]
            session["tipo"] = "funcionario"
            session["id_funcionario"] = row[0]
            session["nivel_acesso"] = row[2]
            flash('Login realizado com sucesso!', 'success')
            return redirect('/admin')

        flash('Usuário ou senha incorretos', 'error')
        return redirect('/auth/login')

    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/auth/login')

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
            
            salt = bcrypt.gensalt()
            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), salt)
            
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
            return redirect('/auth/login')

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

    return render_template('auth/cadastro.html')

@app.route('/pedir', methods=['GET', 'POST'])
def pedir():
    if not session.get("id_cliente"):
        flash('Você precisa estar logado para acessar esta página', 'error')
        return redirect('/auth/login')

    conn = get_db()
    cursor = conn.cursor()
    
    id_cliente = session.get("id_cliente")

    cursor.execute("SELECT * FROM clientes WHERE id_cliente = ?", (id_cliente,))    
    cliente = cursor.fetchone()
    cursor.execute("SELECT id_veiculo, marca, modelo, ano, placa FROM veiculos WHERE id_cliente = ?", (id_cliente,))
    veiculos = cursor.fetchall()
    
    return render_template('servico/pedir.html', cliente=cliente, veiculos=veiculos)

@app.route("/pedir/troca-pecas", methods=["POST"])
def troca_pecas():
    conn = get_db()
    cursor = conn.cursor()
    id_cliente = session.get("id_cliente")
    tipo = "Troca de peças"
    abertura = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    id_veiculo = request.form.get("id_veiculo")
    descricao = request.form.get("descricao")
    observacoes = request.form.get("observacoes")

    diagnostico = descricao
    if observacoes:
        diagnostico += f"\nObservações: {observacoes}"

    cursor.execute("""
        INSERT INTO ordem (id_cliente, id_veiculo, tipo_ordem, diagnostico, abertura, status)
        VALUES (?, ?, ?, ?, ?, 'EM ABERTO')
    """, (id_cliente, id_veiculo, tipo, diagnostico, abertura))
    
    conn.commit()
    return render_template("servico/confirma.html")

@app.route("/pedir/emergencial", methods=["POST"])
def emergencial():
    conn = get_db()
    cursor = conn.cursor()
    id_cliente = session.get("id_cliente")
    tipo = "Serviço Emergencial"
    abertura = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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
        INSERT INTO ordem (id_cliente, id_veiculo, tipo_ordem, diagnostico, abertura, status)
        VALUES (?, ?, ?, ?, ?, 'EM ABERTO')
    """, (id_cliente, id_veiculo, tipo, diagnostico, abertura))
    
    conn.commit()
    return render_template("servico/confirma.html")

@app.route("/pedir/agendamento", methods=["POST"])
def agendamento():
    conn = get_db()
    cursor = conn.cursor()
    id_cliente = session.get("id_cliente")
    tipo = "Agendamento de Serviço"
    abertura = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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
        INSERT INTO ordem (id_cliente, id_veiculo, tipo_ordem, diagnostico, abertura, status)
        VALUES (?, ?, ?, ?, ?, 'EM ABERTO')
    """, (id_cliente, id_veiculo, tipo, diagnostico, abertura))
    
    conn.commit()
    return render_template("servico/confirma.html")


@app.route('/veiculos')
def veiculos():
    if not session.get("id_cliente"):
        flash('Faça login para acessar seus veículos', 'error')
        return redirect('/auth/login')
    
    id_cliente = session.get("id_cliente")
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id_veiculo, marca, modelo, ano, cor, placa 
        FROM veiculos 
        WHERE id_cliente = ?
        ORDER BY marca, modelo
    """, (id_cliente,))
    veiculos = cursor.fetchall()
    
    return render_template('veiculos.html', 
                         veiculos=veiculos,
                         usuario_logado=session.get("usuario"))

@app.route('/veiculos/adicionar', methods=['POST'])
def adicionar_veiculo():
    if not session.get("id_cliente"):
        flash('Faça login para adicionar veículos', 'error')
        return redirect('/auth/login')
    
    id_cliente = session.get("id_cliente")
    marca = request.form.get('marca')
    modelo = request.form.get('modelo')
    ano = request.form.get('ano')
    cor = request.form.get('cor')
    placa = request.form.get('placa').upper()
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id_veiculo FROM veiculos WHERE placa=?", (placa,))
        if cursor.fetchone():
            flash('Esta placa já está cadastrada no sistema!', 'error')
            return redirect('/veiculos')
        
        cursor.execute("""
            INSERT INTO veiculos (marca, modelo, ano, cor, placa, id_cliente)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (marca, modelo, ano, cor, placa, id_cliente))
        
        conn.commit()
        flash('Veículo adicionado com sucesso!', 'success')
        
    except sqlite3.IntegrityError as e:
        conn.rollback()
        if 'placa' in str(e):
            flash('Esta placa já está cadastrada!', 'error')
        else:
            flash('Erro ao adicionar veículo. Verifique os dados.', 'error')
    except Exception as e:
        conn.rollback()
        flash('Erro ao adicionar veículo. Tente novamente.', 'error')
    
    return redirect('/veiculos')

@app.route('/veiculos/editar', methods=['POST'])
def editar_veiculo():
    if not session.get("id_cliente"):
        flash('Faça login para editar veículos', 'error')
        return redirect('/auth/login')
    
    id_cliente = session.get("id_cliente")
    id_veiculo = request.form.get('id_veiculo')
    marca = request.form.get('marca')
    modelo = request.form.get('modelo')
    ano = request.form.get('ano')
    cor = request.form.get('cor')
    placa = request.form.get('placa').upper()
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id_cliente FROM veiculos WHERE id_veiculo=?
        """, (id_veiculo,))
        veiculo = cursor.fetchone()
        
        if not veiculo or veiculo[0] != id_cliente:
            flash('Você não tem permissão para editar este veículo!', 'error')
            return redirect('/veiculos')
        
        cursor.execute("""
            SELECT id_veiculo FROM veiculos 
            WHERE placa=? AND id_veiculo!=?
        """, (placa, id_veiculo))
        
        if cursor.fetchone():
            flash('Esta placa já está cadastrada em outro veículo!', 'error')
            return redirect('/veiculos')
        
        cursor.execute("""
            UPDATE veiculos 
            SET marca=?, modelo=?, ano=?, cor=?, placa=?
            WHERE id_veiculo=? AND id_cliente=?
        """, (marca, modelo, ano, cor, placa, id_veiculo, id_cliente))
        
        conn.commit()
        flash('Veículo atualizado com sucesso!', 'success')
        
    except sqlite3.IntegrityError as e:
        conn.rollback()
        flash('Erro ao atualizar veículo. Placa pode estar duplicada.', 'error')
    except Exception as e:
        conn.rollback()
        flash('Erro ao atualizar veículo. Tente novamente.', 'error')
    
    return redirect('/veiculos')

@app.route('/veiculos/excluir', methods=['POST'])
def excluir_veiculo():
    if not session.get("id_cliente"):
        flash('Faça login para excluir veículos', 'error')
        return redirect('/auth/login')
    
    id_cliente = session.get("id_cliente")
    id_veiculo = request.form.get('id_veiculo')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id_cliente FROM veiculos WHERE id_veiculo=?
        """, (id_veiculo,))
        veiculo = cursor.fetchone()
        
        if not veiculo or veiculo[0] != id_cliente:
            flash('Você não tem permissão para excluir este veículo!', 'error')
            return redirect('/veiculos')
        
        cursor.execute("""
            SELECT COUNT(*) FROM ordem 
            WHERE id_veiculo=? AND status IN ('EM ABERTO', 'EM ANDAMENTO', 'AGUARDANDO PEÇA')
        """, (id_veiculo,))
        ordens_abertas = cursor.fetchone()[0]
        
        if ordens_abertas > 0:
            flash(f'Não é possível excluir este veículo. Existem {ordens_abertas} ordem(ns) de serviço em aberto.', 'error')
            return redirect('/veiculos')
        
        cursor.execute("""
            DELETE FROM veiculos 
            WHERE id_veiculo=? AND id_cliente=?
        """, (id_veiculo, id_cliente))
        
        conn.commit()
        flash('Veículo excluído com sucesso!', 'success')
        
    except Exception as e:
        conn.rollback()
        flash('Erro ao excluir veículo. Tente novamente.', 'error')
    
    return redirect('/veiculos')