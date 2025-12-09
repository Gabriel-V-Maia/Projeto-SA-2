import sqlite3
import bcrypt
from datetime import datetime, timedelta
import random

print("iniciando init_db.py")

conn = sqlite3.connect('automax.db')
cursor = conn.cursor() 

def init_database():
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.executescript(''' 
    CREATE TABLE IF NOT EXISTS clientes (
        id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_cliente TEXT NOT NULL,
        CPF TEXT UNIQUE NOT NULL,
        celular TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha BLOB NOT NULL
    );

    CREATE TABLE IF NOT EXISTS veiculos (
        id_veiculo INTEGER PRIMARY KEY AUTOINCREMENT,
        marca TEXT NOT NULL,
        cor TEXT NOT NULL,
        ano TEXT NOT NULL,
        modelo TEXT NOT NULL,
        placa TEXT UNIQUE NOT NULL,
        id_cliente INTEGER NOT NULL,
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS produtos (
        id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,  
        preco REAL NOT NULL,
        stock INTEGER,
        imagem TEXT NOT NULL,
        categoria TEXT NOT NULL,
        detalhes TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS funcionarios (
        id_funcionario INTEGER PRIMARY KEY AUTOINCREMENT,
        senha BLOB NOT NULL,
        nome_funcionario TEXT NOT NULL,
        nivel_de_acesso TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS ordem (
        id_ordem INTEGER PRIMARY KEY AUTOINCREMENT,
        id_funcionario INTEGER,
        id_cliente INTEGER NOT NULL,
        id_veiculo INTEGER NOT NULL,
        tipo_ordem TEXT NOT NULL,
        diagnostico TEXT,
        abertura TEXT,
        prazo TEXT,
        fechamento TEXT,
        conclusao_ordem TEXT,
        mao_de_obra REAL,
        orcamento REAL,
        status TEXT DEFAULT 'EM ABERTO',
        FOREIGN KEY (id_funcionario) REFERENCES funcionarios(id_funcionario) ON DELETE SET NULL,
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE CASCADE,
        FOREIGN KEY (id_veiculo) REFERENCES veiculos(id_veiculo) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS logs (
        id_log INTEGER PRIMARY KEY AUTOINCREMENT,
        id_funcionario INTEGER,
        detalhe TEXT,
        momento_acao TEXT,
        FOREIGN KEY (id_funcionario) REFERENCES funcionarios(id_funcionario) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS logs_fun(
        id_logs_fun INTEGER PRIMARY KEY AUTOINCREMENT,
        id_func INTEGER,
        id_log INTEGER,
        FOREIGN KEY (id_func) REFERENCES funcionarios(id_funcionario) ON DELETE SET NULL,
        FOREIGN KEY (id_log) REFERENCES logs(id_log) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS funcionario_ordems (
        id_funcionario_ordem INTEGER PRIMARY KEY AUTOINCREMENT,
        id_ordem INTEGER NOT NULL,
        id_funcionario INTEGER NOT NULL,
        FOREIGN KEY (id_ordem) REFERENCES ordem(id_ordem) ON DELETE CASCADE,
        FOREIGN KEY (id_funcionario) REFERENCES funcionarios(id_funcionario) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS historico_ordems (
        id_historico INTEGER PRIMARY KEY AUTOINCREMENT,
        id_ordem INTEGER NOT NULL,
        id_cliente INTEGER NOT NULL,
        id_veiculo INTEGER NOT NULL,
        abertura TEXT,
        FOREIGN KEY (id_ordem) REFERENCES ordem(id_ordem) ON DELETE CASCADE,
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE CASCADE,
        FOREIGN KEY (id_veiculo) REFERENCES veiculos(id_veiculo) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS fornecedores (
        id_fornecedor INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_fornecedor TEXT NOT NULL,
        cnpj TEXT UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS pecas (
        id_peca INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_peca TEXT NOT NULL,
        quantidade INTEGER NOT NULL,
        tipo TEXT,
        id_fornecedor INTEGER NOT NULL,
        FOREIGN KEY (id_fornecedor) REFERENCES fornecedores(id_fornecedor) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS ordem_pecas (
        id_ordem_peca INTEGER PRIMARY KEY AUTOINCREMENT,
        id_peca INTEGER NOT NULL,
        id_ordem INTEGER NOT NULL,
        quantidade_trocas INTEGER,
        FOREIGN KEY (id_peca) REFERENCES pecas(id_peca) ON DELETE CASCADE,
        FOREIGN KEY (id_ordem) REFERENCES ordem(id_ordem) ON DELETE CASCADE
    );
    ''')

    conn.commit()

def inserir_dados():
    senha_padrao = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
    
    clientes = [
        ('João Silva', '123.456.789-00', '47988887777', 'joao@email.com', senha_padrao),
        ('Maria Oliveira', '987.654.321-00', '47977776666', 'maria@email.com', senha_padrao),
        ('Pedro Santos', '111.222.333-44', '47966665555', 'pedro@email.com', senha_padrao),
        ('Ana Costa', '555.666.777-88', '47955554444', 'ana@email.com', senha_padrao),
        ('Carlos Souza', '999.888.777-66', '47944443333', 'carlos@email.com', senha_padrao),
        ('Juliana Ferreira', '222.333.444-55', '47933332222', 'juliana@email.com', senha_padrao),
        ('Roberto Lima', '444.555.666-77', '47922221111', 'roberto@email.com', senha_padrao),
        ('Fernanda Rocha', '666.777.888-99', '47911110000', 'fernanda@email.com', senha_padrao),
    ]
    
    cursor.executemany(''' 
        INSERT INTO clientes (nome_cliente, CPF, celular, email, senha)
        VALUES (?, ?, ?, ?, ?)
    ''', clientes)

    veiculos = [
        ('Toyota', 'Preto', '2020', 'Corolla', 'ABC-1234', 1),
        ('Honda', 'Branco', '2018', 'Civic', 'ABC-5678', 1),
        ('Nissan', 'Cinza', '2022', 'Kicks', 'ABC-9012', 1),
        
        ('Volkswagen', 'Prata', '2019', 'Gol', 'XYZ-1111', 2),
        ('Fiat', 'Vermelho', '2021', 'Argo', 'XYZ-2222', 2),
        
        ('Hyundai', 'Azul', '2022', 'HB20', 'DEF-3333', 3),
        ('Chevrolet', 'Branco', '2020', 'Onix', 'DEF-4444', 3),
        
        ('Renault', 'Preto', '2023', 'Kwid', 'GHI-5555', 4),
        
        ('Ford', 'Azul', '2021', 'Ka', 'JKL-6666', 5),
        ('Jeep', 'Verde', '2022', 'Renegade', 'JKL-7777', 5),
        ('Mitsubishi', 'Prata', '2019', 'L200', 'JKL-8888', 5),
        
        ('Peugeot', 'Branco', '2020', '208', 'MNO-9999', 6),
        ('Citroën', 'Vermelho', '2021', 'C3', 'MNO-0000', 6),
        
        ('BMW', 'Preto', '2023', 'X1', 'PQR-1234', 7),
        
        ('Audi', 'Cinza', '2022', 'A3', 'STU-5678', 8),
        ('Mercedes', 'Prata', '2023', 'Classe A', 'STU-9012', 8),
    ]
    
    cursor.executemany(''' 
        INSERT INTO veiculos (marca, cor, ano, modelo, placa, id_cliente)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', veiculos)

    produtos = [
        ('Óleo de motor', 50, 100, 'https://www.profiautos.com.br/novosite/wp-content/uploads/2017/05/TROCA-DE-600x400.jpg', 'Pecas', 'Óleo para motores de carros, ideal para troca de óleo.'),
        ('Filtro de ar', 30, 200, 'https://images.cws.digital/produtos/gg/34/51/filtro-de-ar-10075134-1675716012938.jpg', 'Pecas', 'Filtro de ar para manter o motor livre de impurezas.'),
        ('Pastilha de freio', 70, 3, 'https://www.horuspecas.com.br/media/catalog/product/cache/1/image/600x400.8/9df78eab33525d08d6e5fb8d27136e95/1/2/1272.jpg', 'Pecas', 'Pastilhas de freio de alta performance, seguras e duráveis.'),
        ('Pneu 205/55', 350, 120, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQM1y3yHoBYkHV8xShhgFzkGqAvNVpFpIHQdQ&s', 'Pecas', 'Pneu de alta resistência para carros de passeio.'),
        ('Bateria 60Ah', 200, 80, 'https://cdn.awsli.com.br/2500x2500/515/515778/produto/19478716/9aea91eed0.jpg', 'Pecas', 'Bateria automotiva de 60Ah, ideal para carros populares.'),
        ('Amortecedor', 150, 60, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRKySigx4BgpFP6KlqUzyHRuPy0YQDwoMvUGg&s', 'Pecas', 'Amortecedor para melhorar a suspensão do veículo.'),
        ('Vela de ignição', 25, 8, 'https://31b93296e4855c6e.cdn.gocache.net/loja/imagens/full/vela-super-plus-1-eletrodo-bosch02.png', 'Pecas', 'Velas de ignição originais.'),
        ('Lâmpada H4', 15, 5, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRz6vL-zqXtXgMXP-hOgOPYVGRu5cF20uQT5w&s', 'Pecas', 'Lâmpadas para faróis.'),
    ]
    
    cursor.executemany(''' 
        INSERT INTO produtos (nome, preco, stock, imagem, categoria, detalhes)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', produtos)

    funcionarios = [
        (bcrypt.hashpw('gerente123'.encode('utf-8'), bcrypt.gensalt()), 'Carlos Mendes', '3'),
        (bcrypt.hashpw('recepcao123'.encode('utf-8'), bcrypt.gensalt()), 'Roberto Santos', '2'),
        (bcrypt.hashpw('mecanico123'.encode('utf-8'), bcrypt.gensalt()), 'Ana Costa', '1')
    ]
    
    cursor.executemany(''' 
        INSERT INTO funcionarios (senha, nome_funcionario, nivel_de_acesso)
        VALUES (?, ?, ?)
    ''', funcionarios)

    cursor.execute('SELECT id_veiculo, id_cliente FROM veiculos')
    veiculos_clientes = cursor.fetchall()
    
    base_date = datetime.now()
    status_opcoes = ['EM ABERTO', 'EM ANDAMENTO', 'AGUARDANDO PEÇA', 'CONCLUIDO', 'CANCELADO']
    tipos_ordem = ['Revisão', 'Troca de peças', 'Serviço Emergencial', 'Agendamento de Serviço']
    
    ordens = []
    for i in range(40):
        dias_atras = random.randint(0, 180)
        data_abertura = (base_date - timedelta(days=dias_atras)).strftime('%Y-%m-%d %H:%M:%S')
        
        id_veiculo, id_cliente = random.choice(veiculos_clientes)
        
        id_funcionario = random.randint(1, 3)
        tipo_ordem = random.choice(tipos_ordem)
        diagnostico = f'Diagnóstico da ordem {i+1}: {tipo_ordem}'
        status = random.choice(status_opcoes)
        mao_obra = round(random.uniform(100, 500), 2)
        orcamento = round(random.uniform(200, 2000), 2)
        
        ordens.append((
            id_funcionario, id_cliente, id_veiculo, tipo_ordem,
            diagnostico, data_abertura, None, None, None,
            mao_obra, orcamento, status
        ))
    
    cursor.executemany(''' 
        INSERT INTO ordem (id_funcionario, id_cliente, id_veiculo, tipo_ordem, 
                          diagnostico, abertura, prazo, fechamento, conclusao_ordem,
                          mao_de_obra, orcamento, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', ordens)
    
    conn.commit()
    conn.close()
    print("db feita e preenchica!")
    print("- 8 clientes cadastrados")
    print("- 16 veículos cadastrados (múltiplos veículos por cliente)")
    print("- 8 produtos em estoque")
    print("- 3 funcionários")
    print("- 40 ordens de serviço")
    print("- 25 registros de log")

if __name__ == '__main__':
    init_database()
    inserir_dados()