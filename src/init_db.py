import sqlite3
'''
AVISO IMPORTANTE
como muitos dados tem UNIQUE, quando você executar o db denovo vai ocorrer um erro de duplicata
então sempre delete o arquivo se for mudar algo
'''
conn = sqlite3.connect('automax.db')
cursor = conn.cursor() 
def init_database():
    
    
    cursor.execute("PRAGMA foreign_keys = ON;") #Boa prática: usar FOREIGN KEY enforcement Por padrão, o SQLite não ativa chaves estrangeiras.

    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS veiculos (
        id_veiculo INTEGER PRIMARY KEY AUTOINCREMENT,
        marca TEXT NOT NULL,
        cor TEXT NOT NULL,
        ano TEXT NOT NULL,
        modelo TEXT NOT NULL,
        placa TEXT UNIQUE NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS produtos (
        id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,  
        preco INTEGER NOT NULL,
        stock INTEGER,
        imagem TEXT NOT NULL,
        categoria TEXT NOT NULL

    );
    
    CREATE TABLE IF NOT EXISTS clientes (
        id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_cliente TEXT NOT NULL,
        CPF TEXT UNIQUE NOT NULL,
        celular TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha BLOB NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS funcionarios (
        id_funcionario INTEGER PRIMARY KEY AUTOINCREMENT,
        senha BLOB NOT NULL,
        nome_funcionario TEXT NOT NULL,
        nivel_de_acesso TEXT NOT NULL -- "gerente", "mecanico" ou "recepcionista"
     );
    
    CREATE TABLE IF NOT EXISTS ordem (
        id_ordem INTEGER PRIMARY KEY AUTOINCREMENT,
        id_funcionario INTEGER NOT NULL,
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
        FOREIGN KEY (id_funcionario) REFERENCES funcionarios(id_funcionario),
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
        FOREIGN KEY (id_veiculo) REFERENCES veiculos(id_veiculo)
    );
    
    CREATE TABLE IF NOT EXISTS funcionario_ordems (
        id_funcionario_ordem INTEGER PRIMARY KEY AUTOINCREMENT,
        id_ordem INTEGER NOT NULL,
        id_funcionario INTEGER NOT NULL,
        FOREIGN KEY (id_ordem) REFERENCES ordem(id_ordem),
        FOREIGN KEY (id_funcionario) REFERENCES funcionarios(id_funcionario)
    );
    
    CREATE TABLE IF NOT EXISTS historico_ordems (
        id_historico INTEGER PRIMARY KEY AUTOINCREMENT,
        id_ordem INTEGER NOT NULL,
        id_cliente INTEGER NOT NULL,
        id_veiculo INTEGER NOT NULL,
        abertura TEXT,
        FOREIGN KEY (id_ordem) REFERENCES ordem(id_ordem),
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
        FOREIGN KEY (id_veiculo) REFERENCES veiculos(id_veiculo)
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
        FOREIGN KEY (id_fornecedor) REFERENCES fornecedores(id_fornecedor)
    );
    
    CREATE TABLE IF NOT EXISTS ordem_pecas (
        id_ordem_peca INTEGER PRIMARY KEY AUTOINCREMENT,
        id_peca INTEGER NOT NULL,
        id_ordem INTEGER NOT NULL,
        quantidade_trocas INTEGER,
        FOREIGN KEY (id_peca) REFERENCES pecas(id_peca),
        FOREIGN KEY (id_ordem) REFERENCES ordem(id_ordem)
    );
    ''')
    
    conn.commit()

def Inserir_dados():
    # Inserindo dados de veiculos
    veiculos = [
        ('Toyota', 'Preto', '2020', 'Corolla', 'ABC-1234'),
        ('Honda', 'Branco', '2021', 'Civic', 'XYZ-5678'),

    ]
    cursor.executemany(''' 
        INSERT INTO veiculos (marca, cor, ano, modelo, placa)
        VALUES (?, ?, ?, ?, ?)
    ''', veiculos)

    # Inserindo dados de produtos
    produtos = [
        ('Óleo de motor', 50, 100, 'óleo_motor.jpg', 'Pecas'),
        ('Filtro de ar', 30, 200, 'filtro_ar.jpg', 'Pecas'),
        ('Pastilha de freio', 70, 150, 'pastilha_freio.jpg', 'Pecas'),
        ('Pneu 205/55', 350, 120, 'pneu_205.jpg', 'Pecas'),
        ('Bateria 60Ah', 200, 80, 'bateria_60Ah.jpg', 'Pecas'),
        ('Amortecedor', 150, 60, 'amortecedor.jpg', 'Pecas'),
        ('Farol de milha', 120, 90, 'farol_milha.jpg', 'Acessorios'),
        ('Lâmpada halógena', 20, 250, 'lampada_halogenas.jpg', 'Acessorios'),
        ('Capa de banco', 50, 300, 'capa_banco.jpg', 'Acessorios'),
        ('Alarme', 100, 80, 'alarme.jpg', 'Acessorios'),
        ('Cinto de segurança', 40, 120, 'cinto_segurança.jpg', 'Acessorios'),
        ('Mola de suspensão', 100, 75, 'mola_suspensao.jpg', 'Pecas'),
        ('Catalisador', 300, 50, 'catalisador.jpg', 'Pecas'),
        ('Sensor de estacionamento', 150, 100, 'sensor_estacionamento.jpg', 'Acessorios'),
        ('Radiador', 250, 60, 'radiador.jpg', 'Pecas'),
        ('Ventoinha', 90, 200, 'ventoinha.jpg', 'Pecas'),
        ('Cárter', 180, 70, 'carter.jpg', 'Pecas'),
        ('Difusor', 60, 110, 'difusor.jpg', 'Acessorios'),
        ('Tampa de válvula', 50, 150, 'tampa_valvula.jpg', 'Pecas'),
        ('Coxim de motor', 120, 80, 'coxim_motor.jpg', 'Pecas')
    ]
    cursor.executemany('''
        INSERT INTO produtos (nome, preco, stock, imagem, categoria)
        VALUES (?, ?, ?, ?, ?)
    ''', produtos)

    # Inserindo dados de clientes (sem duplicatas de CPF)
    clientes = [
        ('João Silva', '123.456.789-00', '123456789', 'joao@email.com', 'senha123'),
        ('Maria Oliveira', '987.654.321-00', '987654321', 'maria@email.com', 'senha456'),
    ]

    # Inserindo clientes sem duplicatas
    cursor.executemany('''
        INSERT INTO clientes (nome_cliente, CPF, celular, email, senha)
        VALUES (?, ?, ?, ?, ?)
    ''', clientes)

    # Inserindo funcionários com diferentes níveis de acesso
    funcionarios = [
        ('gerente123', 'Carlos Mendes', '3'),      # Gerente - Nível 3
        ('mecanico456', 'Roberto Santos', '2'),    # Mecânico - Nível 2
        ('recep789', 'Ana Costa', '1')             # Recepcionista - Nível 1
    ]
    
    cursor.executemany('''
        INSERT INTO funcionarios (senha, nome_funcionario, nivel_de_acesso)
        VALUES (?, ?, ?)
    ''', funcionarios)

    # Commit e fechamento da conexão
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_database()
    Inserir_dados()