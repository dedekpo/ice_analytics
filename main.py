import streamlit as st
import numpy as np
from st_material_table import st_material_table
import base64
from io import BytesIO
#from pyxlsb import open_workbook as open_xlsb
import datetime
import pandas as pd

from Aluno import Alunos
from Escolas import Escolas, get_escola_logged

from PIL import Image
BACKGROUND_IMAGE = "assets/bg_ICEAnalytics.jpg"
logo = Image.open('assets/ice_analytics.png')
favicon = Image.open('assets/favicon.png')

def main():

    st.set_page_config(layout="wide", page_title="ICE Analytics", page_icon=favicon, initial_sidebar_state="collapsed")
    hide_streamlit_style = """
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .css-18e3th9 {
                flex: 1 1 0%;
                width: 100%;
                padding: 0rem 2rem;
                min-width: auto;
                max-width: initial;
            }
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    coluna_imagem, _, coluna_codigo = st.columns([1, 6, 1])
    coluna_imagem.image(logo, width=320)
    codigo_acesso = coluna_codigo.text_input('Código de acesso: 360a1d3e - addba393', type="password")

    logged_user = get_escola_logged(codigo_acesso)

    if logged_user is not None:

        st.write(f'<h1>Bem vindo, {logged_user._nome}!</h1>', unsafe_allow_html=True)

        if logged_user._user_role == 'Admin':

            escolas = Escolas()

            with st.form(key='cadastrar_escola', clear_on_submit=True):
                nome = st.text_input('Nome:')
                nome_wp = st.text_input('Nome Wordpress:')
                user_role = st.selectbox('Acesso', ['Escola', 'Professor'])

                submit = st.form_submit_button('Cadastrar')

                if submit:
                    escolas.insert_escola(nome, nome_wp, user_role)
                    st.experimental_rerun()

            with st.expander("Escolas"):
                st_material_table(escolas.get_escolas_dataframe().fillna(''))
        
        if logged_user._user_role == 'Escola':

            user = Alunos(logged_user)

            email_field, ano_field = st.columns([3, 1])

            pesquisa_aluno = email_field.selectbox('E-mail aluno:', np.append(['Todos alunos'], user.get_users_emails()), key = 2)
            pesquisa_ano = ano_field.selectbox('Ano:', np.append(['Todos anos'], user.get_users_ano()), key = 3)

            alunos_notas = user.get_users_notas(pesquisa_aluno, pesquisa_ano).fillna('')

            with st.expander("Listar"):
                st_material_table(alunos_notas)

            if pesquisa_aluno != 'Todos alunos':
                st.write(user.get_user_progress(pesquisa_aluno))
            
            else:
                #graph, display_info = user.user_line_graph(pesquisa_aluno, pesquisa_ano)
                column1, column2, column3 = st.columns([5, 5, 2])
    
                # if display_info['view'] == 'aluno':
                #     aluno_data_column.metric(label="Cursos matriculados", value = display_info['cursos_matriculados'])
                #     aluno_data_column.metric(label="Progresso semana", value = f"""{round(display_info['progresso_semana'], 2)}%""", delta = f"""{get_change(display_info['progresso_semana'], display_info['progresso_ultima_semana'])}%""")
                #     aluno_data_column.metric(label="Carga horária completa", value = f"""{round(display_info['total_perc_completos'], 2)}%""")
                # else:
                #     aluno_data_column.metric(label="Alunos", value = display_info['numero_alunos'])
                #     aluno_data_column.metric(label="Progresso semana", value = f"""{round(display_info['progresso_semana'], 2)}%""", delta = f"""{get_change(display_info['progresso_semana'], display_info['progresso_ultima_semana'])}%""")
                #     aluno_data_column.metric(label="Cursos completos", value = int(display_info['total_cursos_completos']))
                
                column1.plotly_chart(user.get_class_progress(pesquisa_ano), use_container_width=True, config = {'staticPlot': True})
                column2.plotly_chart(user.get_courses_subscribers(pesquisa_ano), use_container_width=True, config = {'staticPlot': True})
                column3.plotly_chart(user.get_users_last_7days_access(pesquisa_ano), use_container_width=True, config = {'staticPlot': True})
                #graph_3.plotly_chart(graph, use_container_width=True)


            df_xlsx = to_excel(alunos_notas)

            botao1, botao2, _ = st.columns([1, 1, 10])

            #botao1.download_button(label='Exportar Excel', data=df_xlsx, file_name= f"""{ alunos_notas['Nome do Aluno'][0] if display_info['view'] == 'aluno' else 'relatorio_iceplay-'}{datetime.datetime.today().strftime('%d/%m/%Y')}.xlsx""")
            #st.download_button('Exportar PDF', None, 'text/csv')

            
    else:

        st.markdown(
            f"""
            <style>        
                .reportview-container {{
                    background: url('data:image/png;base64,{base64.b64encode(open(BACKGROUND_IMAGE, "rb").read()).decode()}');
                }}
                .sidebar .sidebar-content {{
                    background: url('data:image/png;base64,{base64.b64encode(open(BACKGROUND_IMAGE, "rb").read()).decode()}');
                }}
            </style>
            """, 
            unsafe_allow_html=True
        )

def to_excel(df):

    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data

main()