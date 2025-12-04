import sqlite3
from flask import render_template, jsonify
from app import app
from app import get_db

DATABASE = 'automax.db'

@app.route('/produto/<int:id>')
def get_product(id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        SELECT id_produto, nome, preco, stock, detalhes, categoria, imagem
        FROM produtos
        WHERE id_produto = ?
    ''', (id,))  

    produto = cursor.fetchone()
    

    if produto is None:
        return render_template('notfound.html')

    produto_dict = {
        "id": produto[0],
        "nome": produto[1],
        "preco": produto[2],
        "stock": produto[3],
        "detalhes": produto[4],
        "categoria": produto[5],
        "imagem": produto[6]
    }

    return render_template('produto_detalhe.html', produto=produto_dict)