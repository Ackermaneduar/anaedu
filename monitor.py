import streamlit as st
from streamlit_option_menu import option_menu
import sqlite3
import requests
import time
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Nuestro Espacio Privado ❤️", layout="wide")

# Base de datos compatible con DB Browser
DB_NAME = "datos_pareja.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notas 
                 (autor TEXT, mensaje TEXT, fecha TEXT)''')
    # Tabla de finanzas actualizada con 'nota'
    c.execute('''CREATE TABLE IF NOT EXISTS finanzas 
                 (tipo TEXT, monto REAL, categoria TEXT, fecha TEXT, nota TEXT)''')
    # Tabla para Metas
    c.execute('''CREATE TABLE IF NOT EXISTS metas 
                 (nombre_meta TEXT, objetivo REAL, ahorrado REAL, fecha_limite TEXT)''')
    conn.commit()
    conn.close()


# --- SEGURIDAD ---
USUARIOS = {
    "edu": "edu",    # Cambia esto por tus datos reales
    "nombre_novia": "5678"
}

def login():
    st.markdown("<h1 style='text-align: center;'>❤️ Nuestro Espacio</h1>", unsafe_allow_html=True)
    with st.container():
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            usuario = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            if st.button("Entrar al mundo de nosotros"):
                if usuario in USUARIOS and USUARIOS[usuario] == password:
                    st.session_state["logueado"] = True
                    st.session_state["usuario"] = usuario
                    st.rerun()
                else:
                    st.error("Acceso denegado. Intenta de nuevo.")

# --- FUNCIONES DE SECCIÓN ---

def seccion_status():
    st.header("🌐 Monitor de Páginas")
    url = st.text_input("URL a revisar:", "https://")
    if st.button("Verificar ahora"):
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            inicio = time.time()
            r = requests.get(url, headers=headers, timeout=10)
            latencia = time.time() - inicio
            if r.status_code == 200:
                st.success(f"✅ ONLINE | Tiempo: {latencia:.2f}s | Server: {r.headers.get('Server', 'Desconocido')}")
            else:
                st.warning(f"⚠️ Respondio con error {r.status_code}")
        except:
            st.error("❌ El sitio está caído o la URL es inválida.")

def seccion_finanzas():
    st.header("💰 Centro Financiero de Pareja")
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Resumen", "✍️ Registrar", "📜 Historial Completo", "🎯 Metas"])
    conn = sqlite3.connect(DB_NAME)
    
    # CARGAR DATOS
    df = pd.read_sql_query("SELECT * FROM finanzas", conn)

    with tab1: # RESUMEN
        if not df.empty:
            total_gastado = df[df['tipo'] == 'Gasto']['monto'].sum()
            total_ingreso = df[df['tipo'] == 'Ingreso']['monto'].sum()
            balance = total_ingreso - total_gastado
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Ingresos", f"${total_ingreso:,.2f}")
            c2.metric("Gastos", f"${total_gastado:,.2f}", delta=f"-{total_gastado:,.2f}", delta_color="inverse")
            c3.metric("Balance", f"${balance:,.2f}")
            
            st.write("### Gastos por Categoría")
            df_gastos = df[df['tipo'] == 'Gasto']
            if not df_gastos.empty:
                st.bar_chart(df_gastos.groupby("categoria")["monto"].sum())
        else:
            st.info("No hay datos para mostrar el resumen.")

    with tab2: # REGISTRAR
        st.subheader("Nuevo Registro")
        with st.form("form_finanzas", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            tipo = col_a.radio("Tipo de movimiento", ["Gasto", "Ingreso"], horizontal=True)
            monto = col_b.number_input("Monto ($)", min_value=0.0, step=0.01)
            
            categoria = st.selectbox("Categoría", [
                "Comida 🍕", "Supermercado 🛒", "Citas ❤️", 
                "Viajes ✈️", "Hogar 🏠", "Sueldo 💵", "Otros 📦"
            ])

            # CAMPO DE NOTA ADICIONAL
            nota_adicional = st.text_input("Descripción o Nota (ej: Cena de aniversario)")
            
            fecha_mov = st.date_input("Fecha", datetime.now())
            
            if st.form_submit_button("Guardar en la base de datos"):
                if monto > 0:
                    c = conn.cursor()
                    # AHORA INSERTAMOS 5 VALORES: tipo, monto, categoria, fecha Y nota
                    c.execute("INSERT INTO finanzas (tipo, monto, categoria, fecha, nota) VALUES (?,?,?,?,?)", 
                              (tipo, monto, categoria, fecha_mov.strftime("%Y-%m-%d"), nota_adicional))
                    conn.commit()
                    st.success("¡Movimiento registrado correctamente con nota!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("El monto debe ser mayor a 0")


    with tab3: # HISTORIAL DETALLADO (LO NUEVO)
        st.subheader("📜 Historial de Gastos e Ingresos")
        if not df.empty:
            # Filtros rápidos
            col_f1, col_f2 = st.columns(2)
            filtro_tipo = col_f1.multiselect("Filtrar por tipo:", ["Gasto", "Ingreso"], default=["Gasto", "Ingreso"])
            filtro_cat = col_f2.multiselect("Filtrar por categoría:", df['categoria'].unique(), default=df['categoria'].unique())
            
            # Aplicar filtros al DataFrame
            df_filtrado = df[(df['tipo'].isin(filtro_tipo)) & (df['categoria'].isin(filtro_cat))]
            
            # Mostrar tabla
            st.dataframe(df_filtrado.sort_values(by="fecha", ascending=False), use_container_width=True)
            
            # Opción para exportar
            csv = df_filtrado.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar Historial (CSV)", csv, "finanzas_pareja.csv", "text/csv")
        else:
            st.warning("El historial está vacío.")

   
    conn.close()

def seccion_chat():
    st.header("💬 Notas de Amor")
    
    # ... (El código de guardar nota es el mismo, funciona bien) ...
    with st.container():
        nota = st.text_area("Escribe algo lindo para hoy...")
        if st.button("Dejar Nota"):
            if nota:
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("INSERT INTO notas VALUES (?,?,?)", 
                          (st.session_state["usuario"], nota, datetime.now().strftime("%d/%m/%Y %H:%M")))
                conn.commit()
                conn.close()
                st.success("Tu mensaje ha sido guardado.")

    st.write("---")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM notas ORDER BY fecha DESC")
    mensajes = c.fetchall()
    conn.close()
    
    # --- LA PARTE CORREGIDA ES ESTA: ---
    for m in mensajes:
        autor = m[0]     # Extraemos el autor
        mensaje = m[1]   # Extraemos el mensaje
        fecha = m[2]     # Extraemos la fecha
        
        # Usamos st.chat_message con la lógica de usuario actual
        with st.chat_message("user" if autor == st.session_state["usuario"] else "assistant"):
            # Ahora mostramos el mensaje y la fecha formateados
            st.markdown(f"**{autor}** - *{fecha}*")
            st.write(mensaje)
    # -----------------------------------


def seccion_fotos():
    st.header("📸 Nuestro Álbum")
    foto = st.file_uploader("Sube una foto especial", type=["jpg", "png", "jpeg"])
    if foto:
        st.image(foto, caption="¡Hermoso recuerdo!", use_container_width=True)
    st.info("Nota: Las fotos se muestran al subir, para guardarlas permanentemente se requiere un servidor de archivos.")

# --- LÓGICA PRINCIPAL ---
init_db()

if "logueado" not in st.session_state:
    login()
else:
    with st.sidebar:
        st.title("❤️ Menú")
        selected = option_menu(
            None, ["Status de paginas", "Finanzas", "Chat familiar", "Seccion de fotos"],
            icons=["globe", "cash", "heart", "camera"],
            menu_icon="cast", default_index=0,
        )
        if st.button("Cerrar Sesión"):
            del st.session_state["logueado"]
            st.rerun()

    if selected == "Status de paginas": seccion_status()
    elif selected == "Finanzas": seccion_finanzas()
    elif selected == "Chat familiar": seccion_chat()
    elif selected == "Seccion de fotos": seccion_fotos()
