from spreadsheet import SpreadSheet
from query import Query
import streamlit as st
#import st_state_patch

import numpy as np
from PIL import Image
from pathlib import Path

#DIRECTORIES
BASE_DIR = Path.cwd()
IMAGES_DIR = BASE_DIR / 'images'

#CREDENTIALS
SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive',
         'https://www.googleapis.com/auth/drive.file']

linterna_logo =  Image.open(IMAGES_DIR/'linterna_logo.jpg')

#sections
header = st.container()
body = st.container()

with header:

    st.image(linterna_logo)
    st.write('\n'*2)
    col1, col2, col3 = st.columns([0.5,3,0.5])
    col2.title('GENERADOR DE QUERIES')
    st.write('\n'*2)
    st.write('**NOTA:** para que funcione la aplicación debe compartirse el documento de Drive en donde está el diccionario con el siguiente correo: <ins>scrapper@prueba-scapper.iam.gserviceaccount.com </ins>',unsafe_allow_html=True)

with body:
    # GET DATA
    st.write('## Cargar el diccionario')

    url = 'https://docs.google.com/spreadsheets/d/1UcGt8Cyr93fVJOMFGe2WWjyoNlanbm9SLUghxK8yBjE/edit#gid=0'
    url = st.text_input('Ingrese URL del diccionario:')
    sheet_name = st.text_input('Ingrese el nombre de la hoja que contiene el diccionario:', 'Diccionario')

    if 'pressed_1st_button' not in st.session_state:
        st.session_state.pressed_1st_button = False

    if st.button("Confirmar", key= 'confirmar1')  or st.session_state.pressed_1st_button:
        st.session_state.pressed_1st_button = True #guardar sesion

        #LOAD DATA
        try:
            spreadsheet = SpreadSheet(SCOPES, st.secrets["gcp_service_account"], url)
            df = spreadsheet.dict_to_df(name= sheet_name)
            cols = list(df.columns.values)
        except:
            st.error('Ingrese una URL válida.')

        #SELECT DATA
        st.write('## Seleccionar columnas')
        usr_cols = st.multiselect('Columnas' ,cols, default=cols, key='General')

        st.write(df[usr_cols])

        if 'pressed_2nd_button' not in st.session_state:
            st.session_state.pressed_2nd_button = False

        if st.button("Confirmar", key= 'confirmar2')  or st.session_state.pressed_2nd_button:
            st.session_state.pressed_2nd_button = True #guardar sesion

            #GROUP BY COLUMN
            st.write('## Agrupar columnas')
            col1, col2 = st.columns(2)
            group1 = col1.multiselect('Grupo 1', usr_cols, default=None, key='group1')
            group2 = col2.multiselect('Grupo 2', list(set(usr_cols).difference(group1)), default=None, key='group2')

            query = Query(df[usr_cols])
            query.preprocess_dictionary()

            for g in [group1,group2]:
                if len(g) != 0:
                    query.combine_columns(g)

            # PRINT LOGICAL EXPRESION
            st.write('## Estructura lógica ')
            st.write(query.get_logic_expression())

            if 'pressed_3rd_button' not in st.session_state:
                st.session_state.pressed_3rd_button = False

            if st.button('Generar query') or st.session_state.pressed_3rd_button:
                st.session_state.pressed_3rd_button = True #guardar sesion
                #PRINT & APPEND QUERY
                st.write('## Query ' + ':snake:')

                #incluir o no el filtro de twitter
                twitter_filter = st.checkbox('Twitter only', value=True)

                query_text = query.get_query(twitter_filter)
                query_text2 = query_text.replace("*", "\*") #cambio para que imprima bien los asteríscos

                st.write(query_text2)

                st.write('## Agregar al documento de Drive')

                query_name = st.text_input('Ingrese nombre de la query:',  'Query', key='query_name')

                if st.button('Confirmar'):
                    spreadsheet.append_query_to_spreadsheet(query_text, query_name)
                    st.write('## ¡Listo! :crocodile:')
