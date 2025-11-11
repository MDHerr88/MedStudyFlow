import streamlit as st
from PIL import Image
import PyMuPDF as fitz  # PyMuPDF
from pptx import Presentation
import pandas as pd
import io

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Med-Flash AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS VISUALES (Según tu prompt) ---
# Paleta: #F5A6C1 (Rosa), #E0E0E0 (Gris claro), #4A4A4A (Gris oscuro), #FFFFFF (Blanco)
st.markdown("""
<style>
/* Paleta de Colores */
:root {
    --color-principal: #F5A6C1;
    --color-principal-hover: #E08BAA; /* Rosa más oscuro */
    --gris-claro: #E0E0E0;
    --gris-oscuro: #4A4A4A;
    --blanco: #FFFFFF;
    --verde-correcto: #28a745;
    --amarillo-parcial: #ffc107;
    --rojo-incorrecto: #dc3545;
}

/* Fondo de la app */
.main {
    background-color: #F8F9FA; /* Un gris muy sutil */
}

/* Botones Redondeados */
.stButton>button {
    border-radius: 20px !important;
    background-color: var(--color-principal) !important;
    color: var(--blanco) !important;
    border: none !important;
    padding: 10px 20px !important;
    font-weight: bold !important;
}
.stButton>button:hover {
    background-color: var(--color-principal-hover) !important;
    color: var(--blanco) !important;
}

/* Estilo de Tarjetas (Flashcards) */
.flashcard {
    background-color: var(--blanco);
    border: 2px solid var(--gris-claro);
    border-radius: 15px;
    padding: 25px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    min-height: 250px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

/* Títulos */
h1, h2 {
    color: var(--gris-oscuro);
}

/* Verificación Médica Colores */
.verif-correcto { color: var(--verde-correcto); border-left: 5px solid var(--verde-correcto); padding-left: 10px; }
.verif-parcial { color: var(--amarillo-parcial); border-left: 5px solid var(--amarillo-parcial); padding-left: 10px; }
.verif-incorrecto { color: var(--rojo-incorrecto); border-left: 5px solid var(--rojo-incorrecto); padding-left: 10px; }

</style>
""", unsafe_allow_html=True)

# --- Funciones de Extracción (Placeholders) ---
# (Aquí iría la lógica completa de Tika, PyMuPDF, etc.)

def extraer_texto_pdf(file_stream):
    try:
        doc = fitz.open(stream=file_stream.read(), filetype="pdf")
        texto = ""
        for page in doc:
            texto += page.get_text()
        return texto
    except Exception as e:
        return f"Error al procesar PDF: {e}"

def extraer_texto_pptx(file_stream):
    try:
        prs = Presentation(file_stream)
        texto = ""
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    texto += shape.text + "\n"
        return texto
    except Exception as e:
        return f"Error al procesar PPTX: {e}"

# --- Estado de Sesión ---
if 'page' not in st.session_state:
    st.session_state.page = "Cargar Contenido"
if 'extracted_content' not in st.session_state:
    st.session_state.extracted_content = None

# --- BARRA LATERAL (Navegación) ---
with st.sidebar:
    st.title("🧠 Med-Flash AI")
    st.markdown("Tu asistente de estudio médico con IA.")
    
    # Usamos st.radio para la navegación principal
    page = st.radio(
        "Navegación",
        ["Cargar Contenido", "Verificación IA", "Generar Examen", "Mi Progreso"],
        label_visibility="collapsed"
    )
    st.session_state.page = page
    
    st.markdown("---")
    # Placeholder para icono "doodle"
    st.image("https://placehold.co/250x150/F5A6C1/FFFFFF?text=Icono+Médico+Doodle", use_column_width=True)
    st.markdown(f"<p style='color:var(--gris-oscuro); text-align: center;'>¡Hola Dr. David!</p>", unsafe_allow_html=True)


# --- CUERPO PRINCIPAL DE LA APP ---

# 1. Carga de Contenido
if st.session_state.page == "Cargar Contenido":
    st.header("1. Cargar Contenido 📤")
    st.markdown("Sube tu material de estudio. Extraeremos el texto y las imágenes automáticamente.")

    uploaded_file = st.file_uploader(
        "Sube archivos .pdf, .pptx, .jpg, .png, .txt, .csv, .xlsx",
        type=["pdf", "pptx", "jpg", "png", "txt", "csv", "xlsx"],
        accept_multiple_files=False
    )
    
    if uploaded_file is not None:
        st.info(f"Procesando archivo: `{uploaded_file.name}`...")
        
        # Lógica de extracción
        content = None
        if uploaded_file.type == "application/pdf":
            content = extraer_texto_pdf(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
            content = extraer_texto_pptx(uploaded_file)
        elif uploaded_file.type in ["image/jpeg", "image/png"]:
            img = Image.open(uploaded_file)
            st.image(img, caption="Imagen cargada. (La extracción de texto de imagen (OCR) se implementará aquí).")
            content = "[Placeholder: Texto extraído de imagen con OCR]"
        elif uploaded_file.type == "text/plain":
            content = str(uploaded_file.read(), "utf-8")
        elif uploaded_file.type in ["text/csv", "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
            df = pd.read_csv(uploaded_file) if uploaded_file.type == "text/csv" else pd.read_excel(uploaded_file)
            st.dataframe(df.head())
            content = df.to_string()
            
        if content:
            st.session_state.extracted_content = content
            st.success("¡Contenido extraído! Puedes ir a 'Verificación IA' o 'Generar Examen'.")
            with st.expander("Ver texto extraído (primeros 1000 caracteres)"):
                st.text_area("Texto", value=content[:1000]+"...", height=300, disabled=True)

# 2. Verificación Médica
elif st.session_state.page == "Verificación IA":
    st.header("2. Verificación Médica con IA 🔬")
    st.markdown("Analizamos la precisión científica de tu contenido.")

    if not st.session_state.extracted_content:
        st.warning("Por favor, carga un archivo primero en la sección 'Cargar Contenido'.")
    else:
        st.text_area("Contenido a Verificar", value=st.session_state.extracted_content, height=250, disabled=True)
        
        if st.button("🔬 Analizar Precisión"):
            # --- PLACEHOLDER: Llamada a OpenAI API (GPT-4/5) ---
            # Aquí se enviaría el texto a la API con un prompt de verificación médica.
            
            # Simulación de respuesta de la IA
            st.subheader("Resultados del Análisis:")
            
            st.markdown("""
            <div class.verif-correcto">
                <p><strong>🟢 Correcto:</strong> "El lóbulo frontal es clave para las funciones ejecutivas."</p>
                <small>Análisis: Esta afirmación es precisa y bien definida.</small>
            </div>
            <br>
            <div class="verif-parcial">
                <p><strong>🟡 Parcialmente Correcto:</strong> "La epilepsia siempre causa convulsiones."</p>
                <small>Sugerencia IA: Requiere aclaración. "Epilepsia" es un trastorno de predisposición a crisis. No todas las crisis son convulsivas (ej. ausencias). Fuente: ILAE 2017.</small>
            </div>
            <br>
            <div class="verif-incorrecto">
                <p><strong>🔴 Incorrecto:</strong> "La bioquímica estudia solo las plantas."</p>
                <small>Corrección IA: Esto es incorrecto. La bioquímica estudia los procesos químicos en todos los seres vivos. Fuente: Lehninger Principles of Biochemistry.</small>
            </div>
            """, unsafe_allow_html=True)

# 3. Generador de Preguntas
elif st.session_state.page == "Generar Examen":
    st.header("3. Generar Examen Tipo USMLE/MIR 🎓")
    st.markdown("Generamos preguntas basadas en tu material de estudio.")

    if not st.session_state.extracted_content:
        st.warning("Por favor, carga un archivo primero para generar preguntas sobre él.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Nivel de Dificultad:", ["Automático (Adaptativo)", "Fácil", "Medio", "Difícil"])
        with col2:
            st.selectbox("Tipo de Materia:", ["Materias Básicas (Anatomía, Fisio...)", "Materias Clínicas (Neuro, Pediatría...)"])
        
        if st.button("🚀 Generar Flashcards"):
            # --- PLACEHOLDER: Llamada a OpenAI API ---
            # Aquí la IA generaría preguntas basadas en st.session_state.extracted_content
            
            st.subheader("Tu Examen (Flashcard 1 de 5):")
            
            st.markdown('<div class="flashcard">', unsafe_allow_html=True)
            
            # Contenido de la Flashcard (Simulado)
            st.markdown("<h5>Pregunta (Opción Múltiple)</h5>", unsafe_allow_html=True)
            st.write("Paciente pediátrico de 6 años presenta episodios de mirada fija y desconexión de 10 segundos, sin caída, recuperándose inmediatamente. El EEG muestra complejo punta-onda generalizado a 3Hz. ¿Cuál es el diagnóstico más probable?")
            
            st.radio("Selecciona tu respuesta:", 
                     ["A. Crisis focal compleja", 
                      "B. Epilepsia de Ausencia Infantil (EAI)", 
                      "C. Síncope vasovagal", 
                      "D. Crisis tónico-clónica generalizada"], 
                     index=None, key="q1")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.button("Responder y ver explicación"):
                # Lógica de evaluación (simulada)
                st.success("¡Respuesta registrada!")
                st.info("Explicación: La EAI se caracteriza por ausencias típicas en niños en edad escolar, con el patrón EEG descrito. [Incluiría mini-video o esquema].")


# 4. Progreso y Gamificación
elif st.session_state.page == "Mi Progreso":
    st.header("4. Mi Progreso y Gamificación 🏆")
    st.markdown("Tu avance, niveles e insignias.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Nivel Actual:")
        st.progress(70)
        st.markdown("<h4>Nivel: Intermedio 🩺</h4>", unsafe_allow_html=True)
        st.caption("¡Sigue así para alcanzar el Nivel Clínico!")
    
    with col2:
        st.subheader("Mis Insignias 🧬")
        st.markdown(
            "- 🧠 **Dominio en Neurofisiología**\n"
            "- 👶 **Fundamentos de Pediatría**\n"
            "- 🧪 **Maestro de Bioquímica** (Bloqueada)"
        )
        
    st.subheader("Resumen de Desempeño (Placeholder)")
    st.markdown("Aquí irían los gráficos de Plotly con tu desempeño por materia.")
    
    # Placeholder para gráfico
    chart_data = pd.DataFrame(
        {'Materia': ['Anatomía', 'Fisiología', 'Neurología', 'Pediatría'],
         'Puntaje': [85, 92, 78, 81]}
    )
    st.bar_chart(chart_data, x='Materia', y='Puntaje')

    st.markdown("---")
    st.subheader("Frase Motivacional:")
    st.info("Recuerda, la medicina se aprende un caso a la vez. ¡Sigue estudiando!")
