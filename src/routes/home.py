from flask import render_template, request
from app import app

import sqlite3

conn = sqlite3.connect('automax.db')
cursor = conn.cursor()

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login', methods =['GET', 'POST'])
def login():
    if request.method == 'POST':
        log_nome = request.form.get("usuario")
        log_senha = request.form.get("senha")
        print(f"nome: {log_nome}\nsenha: {log_senha}")

    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':

        nome = request.form.get("nome")
        cpf = request.form.get("cpf")
        celular = request.form.get("celular")
        email = request.form.get("email")
        senha = request.form.get("senha")

        

        tipo_usuario = request.form.get("tipo_usuario") 

        match tipo_usuario:
            case "cliente":
                placa = request.form.get("placa")
                modelo = request.form.get("modelo")
                marca = request.form.get("marca")
                ano = request.form.get("ano")
                cor = request.form.get("cor")

                cursor.execute("""
                INSERT INTO clientes (nome_cliente, CPF, celular, email, senha)
                VALUES (?, ?, ?, ?, ?)
                """, (nome, cpf, celular, email, senha))

                cursor.execute("""
                INSERT INTO veiculos (marca, cor, ano, modelo, placa)
                VALUES (?, ?, ?, ?, ?)
                """, (marca, cor, ano, modelo, placa))
                
                conn.commit()
                conn.close()

            case "funcionario":
                cargo = request.form.get("cargo")

                cursor.execute("""
                INSERT INTO funcionarios (nome_funcionario, nivel_de_acesso)
                VALUES (?, ?)
                """, (nome, cargo))
                
    return render_template('cadastro.html')


# ← só essa linha abaixo
import routes.produto