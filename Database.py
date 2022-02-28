import mysql.connector

# HOST='iceplay.mysql.dbaas.com.br'
# USER='iceplay'
# PASSWORD='P!nkfloyd123'
# DATABASE='iceplay'

HOST='wordpress.c1jo1eunvevo.us-east-1.rds.amazonaws.com'
USER='admin'
PASSWORD='iceplay84017591'
DATABASE='wordpress'


class DB:
    def __init__(self: object) -> None:
        self._database = mysql.connector.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )

        self._cursor = self._database.cursor()

    def return_connection(self: object):
        return self._database

    def return_query(self: object, query: str):
        self._cursor.execute(query)

        return self._cursor.fetchall()

    def close_db(self: object):
        self._cursor.close()
        self._database.close()
        return