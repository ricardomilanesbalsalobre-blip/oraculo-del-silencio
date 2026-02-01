import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
import base64
import warnings

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="El Oráculo del Silencio",
    page_icon="🧘",
    layout="wide"
)
warnings.filterwarnings("ignore")

# --- GESTIÓN DE ESTADO ---
if 'page' not in st.session_state:
    st.session_state.page = 'landing'
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- ESTILOS CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Lato:wght@300;400&display=swap');
    
    .stApp { 
        background-color: #000000; 
        font-family: 'Lato', sans-serif; 
    }
    
    h1, h2, h3 { 
        font-family: 'Cinzel', serif !important; 
        color: #D4AF37 !important; 
        text-align: center; 
        text-shadow: 0px 0px 10px rgba(212, 175, 55, 0.2); 
    }
    
    .landing-title { 
        font-size: 3.5rem !important; 
        font-weight: 700 !important; 
        letter-spacing: 4px; 
        margin-top: 100px; 
        text-transform: uppercase; 
    }
    
    .landing-subtitle { 
        font-size: 1.2rem; 
        color: #bbbbbb !important; 
        text-align: center; 
        max-width: 600px; 
        margin: 0 auto 50px auto; 
    }
    
    div.stButton > button { 
        background-color: transparent !important; 
        color: #D4AF37 !important; 
        border: 1px solid #D4AF37 !important; 
        padding: 15px 40px !important; 
        font-family: 'Cinzel', serif !important; 
        font-size: 1.2rem !important; 
        display: block; 
        margin: 0 auto; 
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: rgba(212, 175, 55, 0.1) !important;
        box-shadow: 0px 0px 15px rgba(212, 175, 55, 0.3) !important;
    }

    /* Ajustes Chat */
    .stChatMessage {
        background-color: rgba(0, 0, 0, 0.7) !important;
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNCIÓN BACKGROUND ---
def set_chat_bg():
    try:
        if os.path.exists('fondo.jpg'):
            with open('fondo.jpg', "rb") as f:
                data = f.read()
            bin_str = base64.b64encode(data).decode()
            st.markdown(f"""
            <style>
            .stApp {{ 
                background-image: url("data:image/png;base64,{bin_str}"); 
                background-size: cover; 
                background-position: center;
                background-attachment: fixed;
            }}
            </style>
            """, unsafe_allow_html=True)
    except: 
        pass

# --- CARGAR LIBROS ---
@st.cache_data
def load_knowledge():
    try:
        with open("knowledge_base.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

def show_landing():
    col1, col2, col3 = st.columns([1, 8, 1])
    with col2:
        st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
        st.markdown('<h1 class="landing-title">BIENVENIDO AL SILENCIO</h1>', unsafe_allow_html=True)
        st.markdown('<div class="landing-subtitle">Deja atrás el ruido del mundo.</div>', unsafe_allow_html=True)
        if st.button("ENTRAR AL SANTUARIO"):
            st.session_state.page = 'chat'
            st.rerun()

def show_chat():
    # 1. AUTENTICACIÓN
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

    if not api_key:
        st.error("⚠️ ERROR: No se encontró la API Key.")
        st.stop()

    genai.configure(api_key=api_key)
    set_chat_bg()

    # 2. CARGAR CEREBRO (Solo una vez)
    book_content = load_knowledge()
    SYSTEM_INSTRUCTION = f"""
Eres el Maestro Pedro. Tu conocimiento proviene única y exclusivamente de estos libros:
{book_content}

"Prestando atención con mi conciencia al silencio, puedo transformar mi alma en vida."
    """
    
    # 3. INICIALIZAR CHAT (Solo si no existe)
    if "chat_session" not in st.session_state:
        # Usamos gemini-1.5-flash que soporta system_instruction nativamente
        # Es más rápido, barato y eficiente que gemini-pro antiguo
        try:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=SYSTEM_INSTRUCTION
            )
            st.session_state.chat_session = model.start_chat(history=[])
        except Exception as e:
            st.error(f"Error al iniciar el Maestro: {e}")
            return

    st.markdown("<h3>El Oráculo del Silencio</h3>", unsafe_allow_html=True)
    
    # Mensaje inicial en UI si está vacío
    if not st.session_state.messages:
        initial_msg = "Bienvenido al espacio del silencio. Estoy aquí para escuchar."
        st.session_state.messages.append({"role": "assistant", "content": initial_msg})

    # 4. MOSTRAR HISTORIAL VISUAL
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 5. INPUT Y RESPUESTA
    if prompt := st.chat_input("Escribe tu pregunta..."):
        # Guardar y mostrar pregunta
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generar respuesta
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            try:
                # Enviar solo el prompt nuevo (el historial ya está en el objeto chat_session)
                response = st.session_state.chat_session.send_message(prompt)
                text_response = response.text
                
                message_placeholder.markdown(text_response)
                st.session_state.messages.append({"role": "assistant", "content": text_response})
            except Exception as e:
                message_placeholder.error(f"El silencio se ha roto: {e}")

# --- RUTAS ---
if st.session_state.page == 'landing':
    show_landing()
elif st.session_state.page == 'chat':
    show_chat()
