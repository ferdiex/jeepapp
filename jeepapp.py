import streamlit as st
import qrcode
import base64
import json
import os
from io import BytesIO
from PIL import Image

# --- CONFIGURACIÓN DE DATOS ---
DATA_FILE = "ruta_pro_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except: pass
    return {
        "titulo": "🏜️ ÚNETE A LA RUTA 4X4",
        "invite_code": st.secrets.get("INVITE_CODE", "0000"),
        "admin_pass": st.secrets.get("ADMIN_PASS", "1234"),
        "fecha": "Domingo, 1 de Agosto 2026",
        "hora": "08:30 AM",
        "punto": "Estacionamiento Costo Xalapa",
        "maps_url": "https://maps.app.goo.gl/dHnpQLPMh7CBDEcG9",
        "qr_app": "https://jeepapp.streamlit.app/",
        "qr_whats": "",
        "requisitos": "🪢 Eslingas (2)\n🧲 Grilletes 3/4\n📻 Radio Baofeng (159.100 MHz) / Talkabout Ch4",
        "full_black": False,
        "fondo_b64": None,
        "participantes": [],
        "fotos": []
    }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def process_image(image_bytes, size=(1280, 720)):
    img = Image.open(BytesIO(image_bytes))
    
    # 1. Forzamos conversión a RGB (quita el peso de transparencias PNG)
    if img.mode != "RGB":
        img = img.convert("RGB")
        
    # 2. Reducimos el tamaño de forma inteligente
    img.thumbnail(size)
    
    # 3. Comprimimos a JPEG (Es mucho más ligero que PNG para fotos)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=50, optimize=True) # Calidad 50% es ideal para fondos
    return base64.b64encode(buf.getvalue()).decode()

# Inicializar
if "db" not in st.session_state:
    st.session_state.db = load_data()

st.set_page_config(
    page_title=st.session_state.db.get("titulo", ""), 
    page_icon="🚜", 
    layout="wide"
)

if "editing_idx" not in st.session_state:
    st.session_state.editing_idx = None # Guardará el número de la fila que estamos editando

# --- CSS TOTAL ---
def apply_css_styles():
    # Revisamos si el admin activó el modo Full Black
    is_full_black = st.session_state.db.get("full_black", False)
    fondo = st.session_state.db.get("fondo_b64")
    
    if is_full_black or not fondo:
        # Modo Full Black o no hay imagen cargada
        bg_style = "none"
        bg_color = "#000000"
    else:
        # Modo con Imagen y Overlay
        overlay = "linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85))"
        bg_style = f'{overlay}, url("data:image/jpeg;base64,{fondo}");'
        bg_color = "#000000"

    st.markdown(f"""
    <style>
    [data-testid="stHeader"] {{ background: rgba(0,0,0,0) !important; }}

    .stApp {{
        background: {bg_style} !important;
        background-color: {bg_color} !important;
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* BOTONES JEEP (Mantenemos el Naranja -> Verde porque el TOML no hace hovers) */
    .stButton > button {{
        background-color: #ff6600 !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        text-transform: uppercase;
        transition: 0.3s all ease;
    }}
    .stButton > button:hover {{
        background-color: #228B22 !important;
        box-shadow: 0 0 15px #228B22;
    }}

    /* ESTILO DE LA GALERÍA Y CARGADORES */
    [data-testid="stFileUploadDropzone"] {{
        border: 2px dashed #ff6600 !important;
        background-color: rgba(26, 26, 26, 0.5) !important;
    }}
    
    /* Forzamos que el botón interno de "Browse files" sea naranja  */
    [data-testid="stFileUploadDropzone"] button {{
        background-color: #ff6600 !important;
        color: white !important;
    }}

    /* TEXTO BLANCO PURO (Para máxima legibilidad) */
    h1, h2, h3, h4, h5, h6, p, label, span, li, div, .stMarkdown {{
        color: #ffffff !important;
    }}

    /* SIDEBAR CON BORDE NARANJA DISCRETO */
    [data-testid="stSidebar"] {{
        border-right: 1px solid #333;
    }}

    /* IMÁGENES REDONDEADAS */
    img {{ border-radius: 12px; }}
    </style>
    """, unsafe_allow_html=True)
    
def apply_login_styles():
    st.markdown("""
    <style>
    /* Estilo para el contenedor del login */
    .login-box {
        text-align: center;
        padding: 20px;
    }
    
    /* Estilizar el input para que parezca 4 cuadros */
    div[data-testid="stTextInput"] input {
        background-color: transparent !important;
        color: #ff6600 !important;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 3rem !important;
        font-weight: bold !important;
        letter-spacing: 35px !important; /* Espacio entre letras para que caigan en su cuadro */
        text-align: center !important;
        border: none !important;
        width: 320px !important;
        margin: 0 auto !important;
        /* Dibujamos los 4 cuadritos con un gradiente de fondo */
        background-image: linear-gradient(to right, #ff6600 2px, transparent 2px), 
                          linear-gradient(to left, #ff6600 2px, transparent 2px), 
                          linear-gradient(to bottom, #ff6600 2px, transparent 2px), 
                          linear-gradient(to top, #ff6600 2px, transparent 2px) !important;
        background-position: 0 0, 100% 0, 0 100%, 0 0 !important;
        background-repeat: no-repeat !important;
        background-size: 25% 100% !important; /* Esto crea el efecto de celdas */
    }

    /* El Halo Naranja alrededor de los 4 cuadros */
    div[data-testid="stTextInput"] > div {
        background-color: transparent !important;
        border: none !important;
        box-shadow: 0 0 20px rgba(255, 102, 0, 0.4) !important;
        width: 320px !important;
        margin: 0 auto !important;
        border-radius: 10px;
    }
    
    div[data-testid="stTextInput"] > div:focus-within {
        box-shadow: 0 0 40px rgba(255, 102, 0, 0.8) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
# --- FLUJO LOGUEO (4 CUADROS + IMAGEN DE FONDO) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # 1. Aplicamos los estilos generales (aquí vive la imagen de fondo)
    apply_css_styles() 
    
    # 2. Aplicamos solo el "Disfraz" de los 4 cuadros (sin tapar el fondo)
    st.markdown("""
    <style>
    /* Estilizamos el input de password para que parezca 4 celdas */
    div[data-testid="stTextInput"] input {
        background-color: rgba(0,0,0,0.5) !important; /* Semitransparente */
        color: #ff6600 !important;
        font-size: 2.5rem !important;
        letter-spacing: 28px !important; 
        text-align: center !important;
        padding-left: 30px !important;
        border: none !important;
        background-image: 
            linear-gradient(to right, #ff6600 2px, transparent 2px),
            linear-gradient(to left, #ff6600 2px, transparent 2px),
            linear-gradient(to bottom, #ff6600 2px, transparent 2px),
            linear-gradient(to top, #ff6600 2px, transparent 2px) !important;
        background-size: 25% 100% !important;
        background-repeat: no-repeat !important;
        width: 280px !important;
        margin: 0 auto !important;
    }

    /* El Halo Naranja Neón */
    div[data-testid="stTextInput"] > div {
        background-color: transparent !important;
        border: none !important;
        box-shadow: 0 0 20px rgba(255, 102, 0, 0.4) !important;
        width: 280px !important;
        margin: 0 auto !important;
        border-radius: 8px;
    }
    
    div[data-testid="stTextInput"] > div:focus-within {
        box-shadow: 0 0 40px rgba(255, 102, 0, 0.9) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    _, col, _ = st.columns([1,2,1])
    with col:
        st.title(st.session_state.db.get("titulo", "🚜 RUTA 4X4"))
        pw = st.text_input("CÓDIGO DE ACCESO", type="password", max_chars=4).upper()
        
        if st.button("ACCEDER A LA RUTA"):
            inv_code = st.session_state.db.get("invite_code", "").upper()
            adm_code = st.session_state.db.get("admin_pass", "").upper()
            
            if pw == inv_code:
                st.session_state.logged_in = True
                st.session_state.is_admin = False
                st.rerun()
            elif pw == adm_code:
                st.session_state.logged_in = True
                st.session_state.is_admin = True
                st.rerun()
            else:
                st.error("CÓDIGO INCORRECTO")
    st.stop()

# --- APP PRINCIPAL ---
apply_css_styles()

with st.sidebar:
    st.image("https://img.icons8.com/ios-filled/100/ff6600/suv.png")
    st.title("4X4 MENU")
    
    # SECCIÓN ADMIN
    if st.session_state.get("is_admin"):
        st.subheader("🛠 Configuración Admin")

        # --- LINK DE WHATSAPP ---
        st.write("---")
        st.subheader("🔗 Links de Invitación")
        st.session_state.db["qr_whats"] = st.text_input("Link Grupo WhatsApp", 
                                                      value=st.session_state.db.get("qr_whats", ""))
        
        if st.button("💾 Guardar Link de QR"):
            save_data(st.session_state.db)
            st.success("¡Link de WhatsApp actualizado!")
            st.rerun()

        st.write("---") 

        st.subheader("🔑 Seguridad y Códigos")
        
        # 1. Capturamos lo que escribes en variables temporales
        nuevo_inv = st.text_input("Código Invitado (4 dígitos)", 
                    value=st.session_state.db.get("invite_code", ""), max_chars=4).upper()
        
        nuevo_adm = st.text_input("Código Admin (4 dígitos)", 
                    value=st.session_state.db.get("admin_pass", ""), max_chars=4).upper()
        
        # 2. El Parche Quirúrgico: Validación de "Diferencial"
        if nuevo_inv == nuevo_adm:
            st.error("⚠️ ¡ALERTA! Los códigos NO pueden ser iguales o perderás el acceso Admin.")
        else:
            # Solo si son diferentes dejamos que aparezca el botón de guardar
            if st.button("💾 Guardar Nueva Seguridad"):
                st.session_state.db["invite_code"] = nuevo_inv
                st.session_state.db["admin_pass"] = nuevo_adm
                save_data(st.session_state.db)
                st.success("¡Códigos actualizados y blindados!")

        st.write("---") 

        # Editar nombre de la ruta
        st.session_state.db["titulo"] = st.text_input("Nombre de la Travesía", value=st.session_state.db.get("titulo", ""))
        
        if st.button("💾 Guardar Nombre y Textos"):
            save_data(st.session_state.db)
            st.success("¡Configuración guardada!")
            # No hace falta rerun, el éxito se muestra y el dato ya está en el JSON
            
        st.write("---")
        
        # Gestión de fondo
        bg = st.file_uploader("Cambiar Imagen de Fondo", type=["jpg", "png", "jpeg"], key="bg_admin")
        if bg:
            # Aquí la procesamos ANTES de guardarla en el JSON
            st.session_state.db["fondo_b64"] = process_image(bg.getvalue())
            save_data(st.session_state.db)
            st.rerun()
            
        if st.session_state.db.get("fondo_b64"):
            if st.button("🗑️ Eliminar Imagen de Fondo"):
                st.session_state.db["fondo_b64"] = None
                save_data(st.session_state.db)
                st.rerun()
                
        st.write("---")        
        # El interruptor para cambiar el modo
        st.session_state.db["full_black"] = st.toggle(
            "🌑 Modo Full Black (Ocultar imagen)", 
            value=st.session_state.db.get("full_black", False)
        )
        
        if st.button("💾 Guardar Estilo"):
            save_data(st.session_state.db)
            st.rerun()
      
        st.write("---")
        if st.button("🚨 RESET TOTAL (LISTA Y FOTOS)"):
            st.session_state.db["participantes"] = []
            st.session_state.db["fotos"] = []
            save_data(st.session_state.db)
            st.rerun()
        st.write("---")
        
        if st.button("🧹 Limpiar Caché (Speed Up)"):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.toast("Caché del servidor purgada")
            st.rerun()

        st.write("---")

        if st.button("🔄 Recarga Forzada (Hard Reload)"):
            # Esto limpia la memoria del navegador y te saca al login
            st.session_state.clear()
            st.rerun()
        st.write("---")
        
    # BOTÓN DE LOGOUT (Siempre visible para todos)
    if st.button("🚪 CERRAR SESIÓN"):
        st.session_state.clear()
        st.rerun()

st.title(st.session_state.db.get("titulo", "🚜 RUTA 4X4"))

col1, col2 = st.columns(2)
with col1:
    st.subheader("📍 Fecha y Punto de Reunión")
    if st.session_state.get("is_admin"):
        st.session_state.db["fecha"] = st.text_input("Fecha", st.session_state.db["fecha"])
        st.session_state.db["hora"] = st.text_input("Hora", st.session_state.db["hora"])
        st.session_state.db["punto"] = st.text_input("Punto", st.session_state.db["punto"])
        st.session_state.db["maps_url"] = st.text_input("URL Maps", st.session_state.db["maps_url"])
    else:
        st.write(f"🗓 {st.session_state.db['fecha']}")
        st.write(f"⏰ {st.session_state.db['hora']}")
        st.write(f"📍 {st.session_state.db['punto']}")
        st.markdown(f"[➡️ Ubicación]({st.session_state.db['maps_url']})")

with col2:
    st.subheader("⚠️ Equipo")
    if st.session_state.get("is_admin"):
        st.session_state.db["requisitos"] = st.text_area("Equipo", st.session_state.db["requisitos"])
    else:
        st.write(st.session_state.db["requisitos"])

if st.session_state.get("is_admin"):
    if st.button("💾 GUARDAR TEXTOS"):
        save_data(st.session_state.db)
        st.toast("Textos guardados")

st.divider()

# --- ASISTENCIA ---
st.subheader("🛞 LISTA DE INVITADOS (POR SEGURIDAD USAR APODOS)")

# Creamos un formulario. 'clear_on_submit=True' hace la magia de limpiar todo al dar click
with st.form("registro_asistencia", clear_on_submit=True):
    c1, c2 = st.columns(2)
    
    with c1:
        nom = st.text_input("Nombre (Apodo)")
    with c2:
        mod = st.text_input("Vehículo 4x4 (Apodo)")
    
    # El botón OK ahora es un 'form_submit_button'
    enviado = st.form_submit_button("ANOTARME EN LA RUTA")

    if enviado:
        if nom and mod:
            # Guardamos en la base de datos
            st.session_state.db["participantes"].append({"nombre": nom, "modelo": mod})
            save_data(st.session_state.db)
            st.success(f"¡Listo {nom}, ya estás en la lista!")
            st.rerun()
        else:
            st.error("Por favor llena ambos campos")

# --- LISTA CON EDICIÓN PARA ADMIN ---
for i, p in enumerate(st.session_state.db["participantes"]):
    # Si el Admin está editando esta fila específica...
    if st.session_state.editing_idx == i and st.session_state.get("is_admin"):
        c_edit = st.columns([0.4, 0.4, 0.2])
        # Cuadros de texto con el valor actual para corregir
        new_n = c_edit[0].text_input("Editar Nombre", value=p['nombre'], key=f"edit_n_{i}")
        new_m = c_edit[1].text_input("Editar Vehículo", value=p['modelo'], key=f"edit_m_{i}")
        
        # Botón para guardar cambios
        if c_edit[2].button("✅", key=f"save_p_{i}"):
            st.session_state.db["participantes"][i] = {"nombre": new_n, "modelo": new_m}
            save_data(st.session_state.db)
            st.session_state.editing_idx = None # Salimos del modo edición
            st.rerun()
            
    else:
        # Modo visualización normal
        row_cols = st.columns([0.1, 0.6, 0.3])
        row_cols[0].markdown(f"`{i+1:02d}`")
        row_cols[1].markdown(f"**{p['nombre']}** — {p['modelo']}")
        
        # Herramientas de Admin: Editar y Borrar
        if st.session_state.get("is_admin"):
            btn_col1, btn_col2 = row_cols[2].columns(2)
            
            # Botón Lápiz para entrar a editar
            if btn_col1.button("📝", key=f"edit_btn_{i}"):
                st.session_state.editing_idx = i
                st.rerun()
                
            # Botón X para borrar (el que ya tenías)
            if btn_col2.button("❌", key=f"del_p_{i}"):
                st.session_state.db["participantes"].pop(i)
                save_data(st.session_state.db)
                st.rerun()

st.divider()

# --- GALERÍA ---
st.subheader("📸 GALERÍA")
foto = st.file_uploader("Subir Experiencia", type=["jpg", "png"], key="user_gal")
if foto:
    if st.button("PUBLICAR FOTO"):
        st.session_state.db["fotos"].append(process_image(foto.getvalue()))
        save_data(st.session_state.db)
        st.rerun()

if st.session_state.db["fotos"]:
    # Mostramos de 3 en 3
    for i in range(0, len(st.session_state.db["fotos"]), 3):
        cols = st.columns(3)
        for j, f_b64 in enumerate(st.session_state.db["fotos"][i:i+3]):
            idx_real = i + j
            with cols[j]:
                st.image(f"data:image/jpeg;base64,{f_b64}")
                if st.session_state.get("is_admin"):
                    if st.button("Eliminar", key=f"del_f_{idx_real}"):
                        st.session_state.db["fotos"].pop(idx_real)
                        save_data(st.session_state.db)
                        st.rerun()

st.divider()
# --- QR APP ---
st.subheader("📲 INVITACIÓN APP")
# Aquí le pasamos la variable real de la base de datos
url_app = st.session_state.db.get("qr_app", "")
if url_app: # Solo genera si hay link
    qr_app_img = qrcode.make(url_app) 
    buf1 = BytesIO()
    qr_app_img.save(buf1, format="PNG")
    st.image(buf1.getvalue(), width=150)
else:
    st.info("Link de App no configurado.")
    
st.divider()
# --- QR WHATSAPP ---
st.subheader("🟢💬 INVITACIÓN GRUPO WHATSAPP")
# Aquí le pasamos la variable real del link de WhatsApp
url_ws = st.session_state.db.get("qr_whats", "")
if url_ws: # Solo genera si hay link
    qr_ws_img = qrcode.make(url_ws)
    buf2 = BytesIO()
    qr_ws_img.save(buf2, format="PNG")
    st.image(buf2.getvalue(), width=150)
else:
    st.info("Link de WhatsApp no configurado.")