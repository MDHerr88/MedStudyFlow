import streamlit as st
import pandas as pd
from pptx import Presentation
from PIL import Image
import io
import openai

# ----------------- CONFIG -----------------
st.set_page_config(page_title="MedStudyFlow", page_icon="🧠", layout="centered")

st.markdown("""
    <style>
    body {background-color:#fff;}
    h1,h2,h3 {color:#444;font-family:'Nunito Sans',sans-serif;}
    .stButton>button {
        background-color:#F5A6C1;color:white;border:none;
        border-radius:10px;padding:8px 16px;font-weight:600;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💗 MedStudyFlow")
st.write("Tu asistente visual de estudio médico — crea, valida y practica con tus propias flashcards.")

# ----------------- CLAVE API -----------------
with st.expander("🔐 Configura tu clave OpenAI"):
    api_key = st.text_input("Clave OpenAI:", type="password")
if not api_key:
    st.warning("Introduce tu clave de OpenAI para continuar.")
else:
    openai.api_key = api_key

# ----------------- EXTRACCIÓN SIMPLE -----------------
def extraer_texto(archivo):
    nombre = archivo.name.lower()
    texto = ""
    if nombre.endswith(".pptx"):
        prs = Presentation(io.BytesIO(archivo.read()))
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    texto += shape.text + "\n"
    elif nombre.endswith((".csv", ".xlsx")):
        if nombre.endswith(".csv"):
            df = pd.read_csv(archivo)
        else:
            df = pd.read_excel(archivo)
        texto = " ".join(df.astype(str).values.flatten())
    elif nombre.endswith(".txt"):
        texto = archivo.read().decode("utf-8")
    elif nombre.endswith((".jpg", ".png", ".jpeg")):
        texto = "[Imagen cargada: análisis visual no disponible en la nube]"
    elif nombre.endswith(".pdf"):
        texto = "[PDF cargado: solo lectura de texto no disponible]"
    else:
        texto = archivo.read().decode(errors="ignore")
    return texto.strip()

# ----------------- FUNCIONES GPT -----------------
def verificar_contenido(texto):
    prompt = f"""
Eres un profesor de medicina. Evalúa brevemente la precisión científica del siguiente texto:
---
{texto[:2000]}
---
Responde con:
1. Nivel (Correcto, Parcial o Incorrecto)
2. Breve explicación (máx 2 líneas)
3. Corrección o sugerencia.
"""
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Eres un médico docente preciso y claro."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        return respuesta.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error: {e}"

def generar_preguntas(texto, tipo, n):
    prompt = f"""
Crea {n} preguntas tipo MIR/USMLE sobre el siguiente contenido:
---
{texto[:2500]}
---
Nivel: {tipo}
Formato:
PREGUNTA: ...
A) ...
B) ...
C) ...
D) ...
RESPUESTA: ...
EXPLICACIÓN: ...
"""
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Eres un profesor de medicina que formula preguntas didácticas."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1200
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error al generar: {e}"

# ----------------- INTERFAZ -----------------
st.header("📂 1. Sube tus archivos de estudio")
archivos = st.file_uploader(
    "Sube tus flashcards, presentaciones o notas (pptx, csv, xlsx, txt, pdf, imágenes)",
    accept_multiple_files=True
)

if archivos and api_key:
    contenido_total = ""
    for archivo in archivos:
        texto = extraer_texto(archivo)
        contenido_total += texto + "\n"
        st.success(f"✅ {archivo.name} procesado ({len(texto.split())} palabras)")

    st.header("🩺 2. Verificación médica")
    if st.button("Verificar contenido"):
        with st.spinner("Analizando..."):
            resultado = verificar_contenido(contenido_total)
        st.info(resultado)

    st.header("🧠 3. Generación de preguntas")
    tipo_examen = st.radio("Nivel del examen:", ["Básico", "Clínico"])
    n_preguntas = st.slider("Número de preguntas", 3, 10, 5)
    if st.button("Generar examen"):
        with st.spinner("Creando preguntas..."):
            preguntas = generar_preguntas(contenido_total, tipo_examen, n_preguntas)
        st.text_area("Preguntas generadas:", preguntas, height=400)

st.write("---")
st.caption("© 2025 MedStudyFlow — versión ligera para Streamlit Cloud.")
