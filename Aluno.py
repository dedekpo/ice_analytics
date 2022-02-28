import pandas as pd
from pandas.core.frame import DataFrame
import plotly.express as px
import datetime

from Database import DB
from Escolas import Escola

class Aluno:
    def __init__(self: object, id: int, email: str, nome: str, escola: str, ano: int, matricula: str, learndash_last_login) -> None:
        self._id = id
        self._email = email
        self._nome = nome
        self._escola = escola
        self._ano = ano
        self._matricula = matricula
        self._learndash_last_login = learndash_last_login


class Alunos:
    def __init__(self: object, logged_user: Escola) -> None:
        self._allUsers: Aluno = []
        self._logged_user = logged_user
            
        mydb = DB()

        myresult = mydb.return_query(f""" SELECT * FROM mv_user WHERE escola = '{self._logged_user._nome_wp}' """)
        
        for x in myresult:
            user = Aluno(x[0], x[1], x[2], x[3], x[4], x[5], x[6])
            self._allUsers.append(user)

        mydb.close_db()

    def get_users_emails(self: object) -> list:
        email_list = []
        for x in self._allUsers:
            email_list.append(x._email)
        return email_list

    def get_users_ano(self: object) -> list:
        ano_list = []
        for x in self._allUsers:
            ano_list.append(x._ano)

        return list(set(ano_list))
        
    def get_users_notas(self: object, pesquisa_aluno: str, pesquisa_ano: str) -> DataFrame:

        mydb = DB()

        df = pd.read_sql(f"""
            SELECT 
                u.nome AS 'Nome do Aluno',
                u.email AS 'E-mail',
                u.ano AS 'Ano',
                c.course_name AS 'Nome do Curso',
                CAST(CONCAT(COUNT(CASE WHEN activity_status = 1 THEN 1 END), ' / ', c.course_total_lessons) AS CHAR) AS 'Módulos Completos',
                -- ROUND(4 * (COUNT(0)/(c.course_total_lessons)), 2) AS 'Nota Acumulada',
                DATE_FORMAT(u.learndash_last_login, '%d/%m/%Y') AS 'Último Acesso'
            FROM `wp_learndash_user_activity` a
            JOIN mv_user u ON u.user_id = a.user_id AND u.escola = '{self._logged_user._nome_wp}'
            JOIN (
                SELECT 
                    pm.meta_value as course_id,
                    p2.post_title as course_name,
                    COUNT(CASE WHEN p.post_type = 'sfwd-lessons' THEN p.ID END) as course_total_lessons
                FROM wp_posts p
                JOIN wp_postmeta pm ON pm.post_id = p.ID
                JOIN wp_posts p2 ON p2.ID = pm.meta_value
                WHERE pm.meta_key ='course_id'
                GROUP BY p2.post_title
            ) c ON c.course_id = a.course_id
            WHERE activity_type = 'lesson'
            GROUP BY 
                u.nome,
                u.email,
                u.ano,
                c.course_name
                
            ORDER BY 
                u.nome, 
                c.course_name 
            """, mydb.return_connection())

        if not(pesquisa_aluno == 'Todos alunos'):
            df = df.loc[df['E-mail'] == pesquisa_aluno]
        
        if not(pesquisa_ano == 'Todos anos'):
            df = df.loc[df['Ano'] == pesquisa_ano]

        mydb.close_db()

        return df

    # def user_line_graph(self: object, pesquisa_aluno: str, pesquisa_ano: str):

    #     mydb = DB()

    #     df = pd.read_sql(f"""
    #         SELECT
    #             u.email AS 'E-mail',
    #             u.ano AS 'Ano',
    #             c.course_name AS 'Nome do Curso',
    #             WEEK(FROM_UNIXTIME(activity_completed)) AS 'Semana',
    #             -- CONCAT(WEEK(FROM_UNIXTIME(activity_completed)), '/', YEAR(FROM_UNIXTIME(activity_completed))) AS 'Semana',
    #             COUNT(0) AS 'Tópicos Completos',
    #             c.course_total_topics AS 'Tópicos do Curso',
    #             ROUND((COUNT(0) * 100) / c.course_total_topics, 2) AS '% Completa'
    #         FROM `wp_learndash_user_activity` a
    #         JOIN mv_user u ON u.user_id = a.user_id AND u.escola = '{self._logged_user._nome_wp}'
    #         JOIN (
    #             SELECT 
    #                 pm.meta_value as course_id,
    #                 p2.post_title as course_name,
    #                 COUNT(CASE WHEN p.post_type = 'sfwd-topic' THEN p.ID END) as course_total_topics
    #             FROM wp_posts p
    #             JOIN wp_postmeta pm ON pm.post_id = p.ID
    #             JOIN wp_posts p2 ON p2.ID = pm.meta_value
    #             WHERE pm.meta_key ='course_id'
    #             GROUP BY p2.post_title
    #         ) c ON c.course_id = a.course_id
    #         WHERE a.activity_type = 'topic' 
    #             AND activity_completed IS NOT NULL
    #         GROUP BY u.email, u.ano, c.course_name, 'Semana', c.course_total_topics
    #         ORDER BY u.email, c.course_name, 'Semana'
    #         """, mydb.return_connection())

    #     mydb.close_db()

    #     if not(pesquisa_aluno == 'Todos alunos'):
    #         df = df.loc[df['E-mail'] == pesquisa_aluno]
        
    #     if not(pesquisa_ano == 'Todos anos'):
    #         df = df.loc[df['Ano'] == pesquisa_ano]

    #     if df['E-mail'].nunique() > 1:
    #         fig = px.line(df, x='Semana', y='% Completa', color='E-mail', markers=True)
    #         fig.update_yaxes(tickvals=[0, 25, 50, 75, 100], range = [0, 105])
    #         fig.update_xaxes(range = [0, 53])
    #         display_info = {
    #             'numero_alunos': df['E-mail'].nunique(),
    #             'progresso_ultima_semana': (df.loc[df['Semana'] == datetime.datetime.now().isocalendar()[1] -1]['% Completa'].sum()) ,
    #             'progresso_semana': (df.loc[df['Semana'] == datetime.datetime.now().isocalendar()[1]]['% Completa'].sum()),
    #             'total_cursos_completos': (df['% Completa'].sum() / 100),
    #             'view': 'escola'
    #         }

    #         return fig, display_info

    #     display_info = {
    #         'cursos_matriculados': df['Nome do Curso'].nunique(),
    #         'progresso_ultima_semana': (df.loc[df['Semana'] == datetime.datetime.now().isocalendar()[1] -1]['% Completa'].sum()) ,
    #         'progresso_semana': (df.loc[df['Semana'] == datetime.datetime.now().isocalendar()[1]]['% Completa'].sum()),
    #         'total_perc_completos': (df['% Completa'].sum()),
    #         'view': 'aluno'
    #     }

    #     fig = px.line(df, x='Semana', y='% Completa', color='Nome do Curso', markers=True)
    #     fig.update_yaxes(tickvals=[0, 25, 50, 75, 100], range = [0, 105])
    #     fig.update_xaxes(range = [0, 53])

    #     return fig, display_info
    
    ########################
    ### NEW REQUIREMENTS ###
    ########################

    def get_courses_subscribers(self: object, pesquisa_ano: str):

        mydb = DB()

        df = pd.read_sql(f"""
            SELECT 
                course_name AS 'Curso',
                COUNT(0) AS qtd_matriculados
            FROM wp_learndash_user_activity a
            JOIN (
                SELECT 
                    pm.meta_value as course_id,
                    p2.post_title as course_name,
                    COUNT(CASE WHEN p.post_type = 'sfwd-lessons' THEN p.ID END) as course_total_lessons
                FROM wp_posts p
                JOIN wp_postmeta pm ON pm.post_id = p.ID
                JOIN wp_posts p2 ON p2.ID = pm.meta_value
                WHERE pm.meta_key ='course_id' AND p.post_status = 'publish'
                GROUP BY p2.post_title
            ) c ON c.course_id = a.course_id
            JOIN mv_user mu ON mu.user_id = a.user_id AND mu.escola IS NOT NULL
            WHERE mu.escola = '{self._logged_user._nome_wp}'
            AND activity_type = 'course'
            GROUP BY course_name
            ORDER BY qtd_matriculados DESC
        """, mydb.return_connection())

        mydb.close_db()

        if not(pesquisa_ano == 'Todos anos'):
            df = df.loc[df['Ano'] == pesquisa_ano]

        fig = px.bar(df, y='qtd_matriculados', x='Curso', text='qtd_matriculados', title='Número de alunos matriculados por curso')
        fig.update_traces(texttemplate='%{text:.0s}', textposition='inside')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', margin=dict(l=20, r=20, t=40, b=20), yaxis={'visible': False, 'showticklabels': True})
        fig.update_xaxes(tickangle=5)  

        return fig

    def get_users_last_7days_access(self: object, pesquisa_ano: str):

        mydb = DB()

        df = pd.read_sql(f"""
            SELECT
                logged_last_7days,
                COUNT(0) as qtd
            FROM (
                SELECT 
                    mu.user_id,
                    CASE WHEN DATEDIFF(CURDATE(), mu.learndash_last_login) <= 7 THEN 'Sim' ELSE 'Não' END AS 'logged_last_7days'
                FROM mv_user mu
                WHERE mu.escola = '{self._logged_user._nome_wp}'
                GROUP BY mu.user_id
            ) t
            GROUP BY logged_last_7days
        """, mydb.return_connection())

        mydb.close_db()

        if not(pesquisa_ano == 'Todos anos'):
            df = df.loc[df['Ano'] == pesquisa_ano]

        fig = px.pie(df, values='qtd', names='logged_last_7days', title='Alunos logados últimos 7 dias')
        fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))

        return fig

    def get_class_progress(self: object, pesquisa_ano: str):

        mydb = DB()

        df = pd.read_sql(f"""
            SELECT
                t.current_lesson as 'Módulo atual',
                COUNT(0) as qtd
            FROM (
                SELECT
                    mu.email,
                    course_name AS 'Curso',
                    COUNT(CASE WHEN a.activity_type = 'lesson' AND a.activity_status = 1 THEN mu.user_id END) AS current_lesson
                FROM mv_user mu
                JOIN wp_learndash_user_activity a ON mu.user_id = a.user_id
                JOIN wp_posts wp ON wp.ID = a.post_id 
                JOIN (
                    -- CURSOS
                    SELECT 
                        pm.meta_value as course_id,
                        p2.post_title as course_name,
                        p.post_status
                    FROM wp_posts p
                    JOIN wp_postmeta pm ON pm.post_id = p.ID
                    JOIN wp_posts p2 ON p2.ID = pm.meta_value
                    WHERE pm.meta_key ='course_id' AND p.post_status = 'publish'
                    GROUP BY p2.post_title
                ) c ON c.course_id = a.course_id
                WHERE mu.escola = '{self._logged_user._nome_wp}'
                AND wp.post_status = 'publish'
                GROUP BY mu.email, course_name
            ) t
            GROUP BY t.current_lesson
            ORDER BY t.current_lesson
        """, mydb.return_connection())

        mydb.close_db()

        if not(pesquisa_ano == 'Todos anos'):
            df = df.loc[df['Ano'] == pesquisa_ano]

        fig = px.bar(df, y='qtd', x='Módulo atual', text='qtd', title='Último módulo completo')
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', margin=dict(l=20, r=20, t=40, b=20), yaxis={'visible': False, 'showticklabels': False})

        return fig

    def get_user_progress(self: object, student_email: str):
        mydb = DB()

        df1 = pd.read_sql(f"""
            SELECT 
                mu.nome,
                CASE WHEN DATEDIFF(CURDATE(), mu.learndash_last_login) <= 7 THEN 'acessou' ELSE 'não acessou' END AS acessou_ultimos_7_dias
            FROM mv_user mu
            WHERE mu.email = '{student_email}'
        """, mydb.return_connection())

        # df2 = pd.read_sql(f"""
        #     SELECT
        #         mu.nome,
        #         course_name AS curso,
        #         COUNT(CASE WHEN a.activity_type = 'lesson' AND a.activity_status = 1 THEN mu.user_id END) + 1 AS current_lesson
        #     FROM mv_user mu
        #     JOIN wp_learndash_user_activity a ON mu.user_id = a.user_id
        #     JOIN wp_posts wp ON wp.ID = a.post_id 
        #     JOIN (
        #         -- CURSOS
        #         SELECT 
        #             pm.meta_value as course_id,
        #             p2.post_title as course_name,
        #             p.post_status
        #         FROM wp_posts p
        #         JOIN wp_postmeta pm ON pm.post_id = p.ID
        #         JOIN wp_posts p2 ON p2.ID = pm.meta_value
        #         WHERE pm.meta_key ='course_id' AND p.post_status = 'publish'
        #         GROUP BY p2.post_title
        #     ) c ON c.course_id = a.course_id
        #     WHERE mu.email = '{student_email}'
        #     AND wp.post_status = 'publish'
        #     GROUP BY mu.nome, course_name
        #     ORDER BY mu.nome
        # """, mydb.return_connection())

        mydb.close_db()

        return_message = f"""O aluno(a) {df1['nome'][0]} {df1['acessou_ultimos_7_dias'][0]} a plataforma ICE Play nos últimos 7 dias."""
        
        # for index, row in df2.iterrows():
        #     return_message = return_message + f"Curso: {row['curso']} - Módulo atual: {row['current_lesson']}\n"

        # print(return_message)

        return return_message