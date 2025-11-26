# src/routes/produto.py
from flask import render_template
from app import app

@app.route('/produto/<int:id>')
def produto_detalhe(id):
    # Por enquanto só mostra a mesma página para qualquer ID
    # Depois você troca por banco de dados
    return render_template('produto_detalhe.html')