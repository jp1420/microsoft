import streamlit as st
import pandas as pd
import datetime
import sqlite3
import re

st.set_page_config(page_title='Formulario de Registro Seguro')

# Cargar estilos personalizados
with open("style.css") as archivo_css:
    st.markdown(f"<style>{archivo_css.read()}</style>", unsafe_allow_html=True)

# Inicialización de base de datos
def inicializar_base_datos():
    conexion_bd = sqlite3.connect('Usuarios_Microsoft.db')
    cursor_bd = conexion_bd.cursor()
    cursor_bd.execute('''
        CREATE TABLE IF NOT EXISTS REGISTRO_USUARIOS(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            password TEXT,
            fecha_creacion TEXT
        )
    ''')
    conexion_bd.commit()
    conexion_bd.close()

def inicializar_tabla_historial():
    conexion_bd = sqlite3.connect('Usuarios_Microsoft.db')
    cursor_bd = conexion_bd.cursor()
    cursor_bd.execute('''
        CREATE TABLE IF NOT EXISTS REGISTRO_HISTORIAL(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_usuario TEXT,
            tipo_accion TEXT,
            marca_tiempo TEXT
        )
    ''')
    conexion_bd.commit()
    conexion_bd.close()

# Validar contraseña segura
def validar_password_segura(password_usuario):
    criterios = {
        "Al menos 8 caracteres": len(password_usuario) >= 8,
        "Al menos una MAYUSCULA": re.search(r"[A-Z]", password_usuario) is not None,
        "Al menos una minuscula": re.search(r"[a-z]", password_usuario) is not None,
        "Al menos un numero": re.search(r"\d", password_usuario) is not None,
        "Al menos un caracter especial": re.search(r"[!@#$%&*(),.]", password_usuario) is not None
    }
    return criterios

# Registro y verificación
def guardar_usuario(usuario_nuevo, password_segura):
    conexion_bd = sqlite3.connect('Usuarios_Microsoft.db')
    cursor_bd = conexion_bd.cursor()
    fecha_actual = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    cursor_bd.execute("SELECT id FROM REGISTRO_USUARIOS WHERE usuario = ?", (usuario_nuevo,))
    if cursor_bd.fetchone():
        conexion_bd.close()
        return False

    cursor_bd.execute("INSERT INTO REGISTRO_USUARIOS (usuario, password, fecha_creacion) VALUES (?, ?, ?)", 
                      (usuario_nuevo, password_segura, fecha_actual))
    conexion_bd.commit()
    conexion_bd.close()
    return True

def verificar_usuario(usuario_login, password_login):
    conexion_bd = sqlite3.connect('Usuarios_Microsoft.db')
    cursor_bd = conexion_bd.cursor()
    cursor_bd.execute("SELECT password FROM REGISTRO_USUARIOS WHERE usuario = ?", (usuario_login,))
    resultado = cursor_bd.fetchone()
    conexion_bd.close()
    return resultado and resultado[0] == password_login

def registrar_historial(usuario_historial, tipo_movimiento):
    conexion_bd = sqlite3.connect('Usuarios_Microsoft.db')
    cursor_bd = conexion_bd.cursor()
    fecha_actual = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    cursor_bd.execute("INSERT INTO REGISTRO_HISTORIAL (nombre_usuario, tipo_accion, marca_tiempo) VALUES (?, ?, ?)",
                      (usuario_historial, tipo_movimiento, fecha_actual))
    conexion_bd.commit()
    conexion_bd.close()

# Inicializar
inicializar_base_datos()
inicializar_tabla_historial()

# Menú
menu_principal = ['Inicio', 'Ingreso y Registro', 'Base de Datos', 'Historial']
opcion_menu = st.sidebar.selectbox('Seleccione una opción', menu_principal)

if opcion_menu == 'Inicio':
    st.title('Microsoft')
    st.markdown('''
        - Registra usuarios de manera segura.
        - Consulta y descarga los datos.
        - Revisa historial de acciones.
    ''')

elif opcion_menu == 'Ingreso y Registro':
    if "mostrar_formulario_registro" not in st.session_state:
        st.session_state.mostrar_formulario_registro = False

    if not st.session_state.mostrar_formulario_registro:
        st.title('Ingreso de Usuario')
        with st.form(key='formulario_ingreso'):
            ingreso_usuario = st.text_input('Usuario')
            ingreso_password = st.text_input('Contraseña', type='password')
            boton_ingresar = st.form_submit_button('Ingresar')

        if boton_ingresar:
            if ingreso_usuario.strip() == '' or ingreso_password.strip() == '':
                st.warning("⚠️ Por favor complete todos los campos.")
                registrar_historial(ingreso_usuario, 'Ingreso fallido por campos vacíos')
            elif verificar_usuario(ingreso_usuario, ingreso_password):
                st.success(f'✅ Bienvenido {ingreso_usuario}')
                registrar_historial(ingreso_usuario, 'Ingreso exitoso')
            else:
                st.error('❌ Usuario o contraseña incorrectos')
                registrar_historial(ingreso_usuario, 'Ingreso fallido por credenciales')

        if st.button('¿No tienes cuenta? Regístrate'):
            st.session_state.mostrar_formulario_registro = True
            st.rerun()
    else:
        st.title('Registro de Usuario')
        with st.form(key='formulario_registro'):
            nuevo_nombre_usuario = st.text_input('Elige un nombre de usuario')
            password_nueva = st.text_input('Crea una contraseña segura', type='password')
            boton_registro = st.form_submit_button('Registrarse')

        if boton_registro:
            validaciones = validar_password_segura(password_nueva)
            for criterio, cumplido in validaciones.items():
                icono = '✔️' if cumplido else '❌'
                st.markdown(f'{icono} {criterio}')

            if all(validaciones.values()):
                if guardar_usuario(nuevo_nombre_usuario, password_nueva):
                    st.success(f'✅ Usuario {nuevo_nombre_usuario} creado exitosamente')
                    st.session_state.mostrar_formulario_registro = False
                    registrar_historial(nuevo_nombre_usuario, 'Registro exitoso')
                else:
                    st.error('⚠️ El usuario ya está registrado')
            else:
                st.warning('⚠️ La contraseña no cumple con los requisitos mínimos')

        if st.button('¿Ya tienes cuenta? Inicia sesión'):
            st.session_state.mostrar_formulario_registro = False
            st.rerun()

elif opcion_menu == 'Base de Datos':
    st.title('🔐 Acceso a la Base de Datos')
    clave_ingresada = st.text_input('Introduce la clave de acceso', type='password')
    archivo_base_datos = st.file_uploader('Sube tu archivo de base de datos', type=['db'])

    clave_correcta_bd = 'didieresgay'
    if archivo_base_datos and clave_ingresada:
        if clave_ingresada == clave_correcta_bd:
            nombre_archivo_temporal = 'base_datos_temp.db'
            with open(nombre_archivo_temporal, 'wb') as archivo:
                archivo.write(archivo_base_datos.read())

            conexion_temp = sqlite3.connect(nombre_archivo_temporal)
            cursor_temp = conexion_temp.cursor()
            cursor_temp.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tablas_disponibles = cursor_temp.fetchall()

            for tabla_info in tablas_disponibles:
                nombre_tabla = tabla_info[0]
                st.subheader(f"Tabla: {nombre_tabla}")
                dataframe = pd.read_sql(f"SELECT * FROM {nombre_tabla}", conexion_temp)
                st.dataframe(dataframe)
            conexion_temp.close()
        else:
            st.error('❌ Clave incorrecta')

elif opcion_menu == 'Historial':
    st.title('📋 Historial de Acciones')
    clave_historial = st.text_input('Introduce la clave para acceder al historial', type='password')
    clave_correcta_historial = 'didieresgay'  # Usa la misma o cambia si deseas

    if clave_historial:
        if clave_historial == clave_correcta_historial:
            conexion_historial = sqlite3.connect('Usuarios_Microsoft.db')
            df_movimientos = pd.read_sql("SELECT * FROM REGISTRO_HISTORIAL ORDER BY marca_tiempo DESC", conexion_historial)
            conexion_historial.close()

            if not df_movimientos.empty:
                st.dataframe(df_movimientos)
            else:
                st.info('🕓 No se han registrado movimientos aún.')
        else:
            st.error('❌ Clave incorrecta')

