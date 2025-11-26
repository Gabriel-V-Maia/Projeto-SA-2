import sqlite3

def init_database():
    conn = sqlite3.connect('automax.db')
    cursor = conn.cursor()
    
    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS veiculos (
        id_veiculo INTEGER PRIMARY KEY AUTOINCREMENT,
        marca TEXT,
        cor TEXT,
        ano TEXT,
        modelo TEXT,
        placa TEXT UNIQUE
    );
    
    CREATE TABLE IF NOT EXISTS produtos (
        id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        preco INTEGER,
        stock INTEGER
    );
    
    CREATE TABLE IF NOT EXISTS clientes (
        id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_cliente TEXT,
        CPF TEXT UNIQUE,
        celular TEXT,
        email TEXT UNIQUE,
        senha TEXT
    );
    
    CREATE TABLE IF NOT EXISTS funcionarios (
        id_funcionario INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_funcionario TEXT,
        nivel_de_acesso INTEGER
    );
    
    CREATE TABLE IF NOT EXISTS ordem (
        id_ordem INTEGER PRIMARY KEY AUTOINCREMENT,
        id_funcionario INTEGER,
        id_cliente INTEGER,
        id_veiculo INTEGER,
        tipo_ordem TEXT,
        diagnostico TEXT,
        abertura TEXT,
        prazo TEXT,
        fechamento TEXT,
        conclusao_ordem TEXT,
        mao_de_obra REAL,
        orcamento REAL,
        FOREIGN KEY (id_funcionario) REFERENCES funcionarios(id_funcionario),
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
        FOREIGN KEY (id_veiculo) REFERENCES veiculos(id_veiculo)
    );
    
    CREATE TABLE IF NOT EXISTS funcionario_ordems (
        id_funcionario_ordem INTEGER PRIMARY KEY AUTOINCREMENT,
        id_ordem INTEGER,
        id_funcionario INTEGER,
        FOREIGN KEY (id_ordem) REFERENCES ordem(id_ordem),
        FOREIGN KEY (id_funcionario) REFERENCES funcionarios(id_funcionario)
    );
    
    CREATE TABLE IF NOT EXISTS historico_ordems (
        id_historico INTEGER PRIMARY KEY AUTOINCREMENT,
        id_ordem INTEGER,
        id_cliente INTEGER,
        id_veiculo INTEGER,
        abertura TEXT,
        FOREIGN KEY (id_ordem) REFERENCES ordem(id_ordem),
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
        FOREIGN KEY (id_veiculo) REFERENCES veiculos(id_veiculo)
    );
    
    CREATE TABLE IF NOT EXISTS fornecedores (
        id_fornecedor INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_fornecedor TEXT,
        cnpj TEXT UNIQUE
    );
    
    CREATE TABLE IF NOT EXISTS pecas (
        id_peca INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_peca TEXT,
        quantidade INTEGER,
        tipo TEXT,
        id_fornecedor INTEGER,
        FOREIGN KEY (id_fornecedor) REFERENCES fornecedores(id_fornecedor)
    );
    
    CREATE TABLE IF NOT EXISTS ordem_pecas (
        id_ordem_peca INTEGER PRIMARY KEY AUTOINCREMENT,
        id_peca INTEGER,
        id_ordem INTEGER,
        quantidade_trocas INTEGER,
        FOREIGN KEY (id_peca) REFERENCES pecas(id_peca),
        FOREIGN KEY (id_ordem) REFERENCES ordem(id_ordem)
    );
    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_database()