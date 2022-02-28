import pandas as pd
from pandas.core.frame import DataFrame
import uuid

from Database import DB

class Escola:
    def __init__(self: object, id: int, nome: str, nome_wp: str, signin_code: str, user_role: str, status: str) -> None:
        self._id = id
        self._nome = nome
        self._nome_wp = nome_wp
        self._signin_code = signin_code
        self._user_role = user_role
        self._status = status


class Escolas:
    def __init__(self: object) -> None:
        self._allEscolas: Escola = []

        mydb = DB()
        query = "SELECT * FROM escolas"
        myresult = mydb.return_query(query)
        
        for x in myresult:
            user = Escola(x[0], x[1], x[2], x[3], x[4], x[5])
            self._allEscolas.append(user)
        
        mydb.close_db()
    
    def get_escolas_dataframe(self: object) -> DataFrame:
        
        list_dict = []
        
        for x in self._allEscolas:
            list_dict.append(x.__dict__)

        dataframe = pd.DataFrame(list_dict)

        dataframe = dataframe.rename(columns={'_id': 'ID', '_nome': 'Nome', '_nome_wp': 'Nome Wordpress', '_signin_code': 'Código de acesso', '_user_role': 'Perfil', '_status': 'Status'})
            
        return dataframe

    def insert_escola(self: object, nome: str, nome_wp: str, user_role: str) -> None:

        mydb = DB()

        signin_code = str(uuid.uuid4())[0:8]

        try:
            mydb._cursor.execute(""" INSERT INTO escolas (nome, nome_escola_wp, signin_code, user_role, status) VALUES (%s, %s, %s, %s, 'Ativo'); """, (nome, nome_wp, signin_code, user_role))

        except:
            print('Erro ao inserir escola')
            mydb._database.rollback()
        else:
            mydb._database.commit()

        mydb.close_db()
        return

def get_escola_logged(codigo_acesso: str):
        mydb = DB()
        query = f"""SELECT * FROM escolas WHERE signin_code = '{codigo_acesso}'; """
        user_query_result = mydb.return_query(query)
        if len(user_query_result) > 0:
            return Escola(user_query_result[0][0], user_query_result[0][1], user_query_result[0][2], user_query_result[0][3], user_query_result[0][4], user_query_result[0][5])