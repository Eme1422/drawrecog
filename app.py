import os
import streamlit as st
import base64
from openai import OpenAI
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import platform

# Configuración de la página (Debe ser el primer comando de Streamlit)
st.set_page_config(
    page_title='Tablero Inteligente 🎨',
    page_icon='🟣',
    layout='centered',
    initial_sidebar_state='expanded'
)

# Estilos CSS personalizados con paleta de tonos morados / violetas
st.markdown("""
    <style>
    /* Fondo principal y color de texto general */
    .stApp {
        background-color: #F8F7FC;
        color: #2D2342;
    }
    
    /* Encabezados */
    h1, h2, h3 {
        color: #4A154B !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #2D2342;
        color: #FFFFFF;
    }
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] span, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #E2DFEC !important;
    }
    
    /* Campos de texto y selectores */
    .stTextInput input {
        background-color: #FFFFFF !important;
        color: #2D2342 !important;
        border: 1px solid #D1C4E9 !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus {
        border-color: #7B1FA2 !important;
        box-shadow: 0 0 0 2px rgba(123, 31, 162, 0.2) !important;
    }
    
    /* Botones principales */
    .stButton button {
        background-color: #7B1FA2 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        transition: background-color 0.3s ease;
    }
    .stButton button:hover {
        background-color: #6A1B9A !important;
    }
    
    /* Tarjeta o contenedor para la respuesta */
    .response-box {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #7B1FA2;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-top: 15px;
    }
    
    /* Alertas */
    .stAlert {
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Función para codificar imagen a base64
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."

# Configuración y Panel Lateral con Propiedades del Tablero
with st.sidebar:
    st.image("https://img.icons8.com/clouds/100/combo-chart.png", width=80)
    st.subheader("🟣 Acerca de:")
    st.markdown("En esta aplicación exploraremos la capacidad que tiene la IA para interpretar bocetos y dibujos en tiempo real.")
    
    st.markdown("---")
    st.subheader("⚙️ Propiedades del Tablero")
    
    # Controles configurables del canvas
    stroke_width = st.slider('Ancho de línea (Pincel)', 1, 30, 5)
    stroke_color = st.color_picker('Color del Pincel', '#000000')
    bg_color = st.color_picker('Color de Fondo', '#FFFFFF')
    
    canvas_width = st.slider('Ancho del Tablero (px)', 200, 600, 400, step=50)
    canvas_height = st.slider('Alto del Tablero (px)', 200, 500, 300, step=50)
    
    st.markdown("---")
    st.markdown(f"**Python:** `{platform.python_version()}`")

# Título y presentación
st.title("🎨 Tablero Inteligente")
st.markdown("### Dibuja un boceto en el panel y presiona el botón para que la IA lo analice.")
st.markdown("---")

# Componente Canvas interactivo con propiedades dinámicas
canvas_result = st_canvas(
    fill_color="rgba(123, 31, 162, 0.3)", 
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=canvas_height,
    width=canvas_width,
    drawing_mode="freedraw",
    key="canvas",
)

st.markdown("---")

# Ingreso de la Clave OpenAI
st.subheader("🔑 Credenciales de Acceso")
ke = st.text_input('Ingresa tu Clave de OpenAI', type="password", help="Tu clave se mantiene segura durante la sesión.")
if ke:
    os.environ['OPENAI_API_KEY'] = ke

api_key = os.environ.get('OPENAI_API_KEY', '')

# Botón para analizar
analyze_button = st.button("🚀 Analiza la imagen", type="secondary")

# Lógica principal de análisis
if canvas_result.image_data is not None and api_key and analyze_button:
    # Validar si el canvas está vacío (verificando si hay trazos)
    if np.max(canvas_result.image_data) == 0 and bg_color == '#000000':
        st.warning("⚠️ Por favor, dibuja algo en el tablero antes de analizar.", icon="⚠️")
    else:
        with st.spinner("🟣 Analizando boceto con Inteligencia Artificial..."):
            # Procesar y guardar imagen temporalmente
            input_numpy_array = np.array(canvas_result.image_data)
            input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
            input_image.save('img.png')
            
            # Codificar imagen en base64
            base64_image = encode_image_to_base64("img.png")
            prompt_text = "Describe detalladamente lo que ves en este boceto o dibujo en español."
            
            # Inicializar cliente OpenAI correctamente
            client = OpenAI(api_key=api_key)
            
            try:
                # Petición a la API de OpenAI
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}"
                                    },
                                },
                            ],
                        }
                    ],
                    max_tokens=500,
                )
                
                response_content = response.choices[0].message.content
                
                if response_content:
                    st.markdown("### 📌 Resultado del Análisis:")
                    st.markdown(f'<div class="response-box">{response_content}</div>', unsafe_allow_html=True)
                    
                    # Guardar en session_state si se requiere
                    st.session_state.mi_respuesta = response_content
            
            except Exception as e:
                st.error(f"Ocurrió un error al procesar la solicitud: {e}", icon="🚨")

else:
    if analyze_button:
        if not canvas_result.image_data is not None:
            st.warning("⚠️ Por favor realiza un trazo en el tablero.", icon="⚠️")
        if not api_key:
            st.warning("🔒 Por favor ingresa tu Clave de OpenAI para continuar.", icon="⚠️")
