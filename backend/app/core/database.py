from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# conexão com o banco de dados SQLite
db = create_engine("sqlite:///valorascan.db", echo=True)


def pegar_session():
    """
    Função para criar e fornecer uma sessão do banco de dados. Ela é usada como uma dependência no FastAPI para garantir que cada solicitação tenha sua própria sessão, que é fechada após o uso.
    """
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    finally:
        session.close() # type: ignore


# cria a base do banco de dados
Base = declarative_base()
