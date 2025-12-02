from flask import Flask, g
import sqlite3
import click

from utils import Logger

log = Logger("App", enabled=True)

app = Flask(__name__, template_folder="pages")

app.secret_key = "uma_chave_secreta_segura" # aqui será colocado a secret key, essa é só exemplo

DATABASE = 'automax.db'

def get_db():
    db = getattr(g, '_database', None)
    
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  
    
    return db
    
    
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        

# NÃO MOVA AS DUAS LINHAS ABAIXO OU TUDO QUEBRA!
from routes import home 
from routes import produtos


if __name__ == "__main__":
    app.run(debug=True)

