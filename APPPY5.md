import streamlit as st
import requests
import numpy as np

st.set_page_config(page_title="EduHub – Conecta tu perfil con el mundo real", layout="wide")

# ------------------------
# SESIÓN
# ------------------------
if "user_logged_in" not in st.session_state:
    st.session_state.user_logged_in = False
if "user_data" not in st.session_state:
    st.session_state.user_data = {}
if "test_results" not in st.session_state:
    st.session_state.test_results = {}

def login():
    st.subheader("🔐 Inicia sesión")
    with st.form("login_form"):
        email = st.text_input("Correo electrónico")
        pais = st.selectbox("País de residencia", ["Panamá","Colombia","México","Argentina","Otro"])
        submitted = st.form_submit_button("Continuar")
        if submitted and email:
            st.session_state.user_logged_in = True
            st.session_state.user_data = {"email": email, "pais": pais}
            st.success("✅ ¡Bienvenido!")

# ------------------------
# TEST RIASEC EXTENDIDO
# ------------------------
def show_test():
    st.subheader("🧠 Test Vocacional Extendido")
    preguntas = {
        "analitico_1":"¿Te gusta resolver problemas matemáticos?",
        "analitico_2":"¿Disfrutas investigar cómo funcionan las cosas?",
        "analitico_3":"¿Te atrae el análisis de datos y estadísticas?",
        "creativo_1":"¿Te interesa escribir o diseñar contenido visual?",
        "creativo_2":"¿Disfrutas idear soluciones originales?",
        "creativo_3":"¿Te atrae el arte y la expresión cultural?",
        "social_1":"¿Te motiva ayudar a otros a aprender?",
        "social_2":"¿Te gustaría trabajar en equipo y guiar personas?",
        "social_3":"¿Te sientes cómodo gestionando conflictos?",
        "tecnico_1":"¿Te apasiona programar o experimentar con tecnología?",
        "tecnico_2":"¿Te atrae entender sistemas y lógica de máquinas?",
        "tecnico_3":"¿Prefieres herramientas y procesos prácticos?",
        "empresarial_1":"¿Te motiva liderar proyectos o negocios?",
        "empresarial_2":"¿Te interesa la planificación estratégica?",
        "empresarial_3":"¿Disfrutas negociar y vender ideas?",
        "realista_1":"¿Prefieres trabajos manuales y concretos?",
        "realista_2":"¿Te atrae la operación de equipos o construcción?",
        "realista_3":"¿Te gusta la logística y la gestión de recursos?"
    }
    respuestas = {}
    for k, txt in preguntas.items():
        respuestas[k] = st.slider(txt, 1, 5, 3)
    if st.button("Guardar resultados"):
        st.session_state.test_results = respuestas
        st.success("Test guardado. Ve al Dashboard para ver tus recomendaciones.")

def compute_scores(res):
    dims = {
        "Analítico":["analitico_1","analitico_2","analitico_3"],
        "Creativo":["creativo_1","creativo_2","creativo_3"],
        "Social":["social_1","social_2","social_3"],
        "Técnico":["tecnico_1","tecnico_2","tecnico_3"],
        "Empresarial":["empresarial_1","empresarial_2","empresarial_3"],
        "Realista":["realista_1","realista_2","realista_3"]
    }
    return {dim: np.mean([res[k] for k in keys]) for dim, keys in dims.items()}

# ------------------------
# APIs Externas y Mockups
# ------------------------
def obtener_universidades(pais):
    try:
        url = f"http://universities.hipolabs.com/search?country={pais}"
        r = requests.get(url, timeout=5); r.raise_for_status()
        return r.json()[:15]
    except:
        return []

def becas_mockup(pais):
    pool = {
        "Panamá":[
            {"nombre":"IFARHU - Excelencia Acad.","link":"https://ifarhu.gob.pa"},
            {"nombre":"SENACYT Postgrados","link":"https://senacyt.gob.pa"}],
        "México":[
            {"nombre":"CONACYT Maestría","link":"https://conacyt.gob.mx"},
            {"nombre":"Becas UNAM","link":"https://unam.mx"}],
        "Global":[
            {"nombre":"Scholarship Portal EU","link":"https://scholarshipportal.com"},
            {"nombre":"DAAD Alemania","link":"https://daad.de"}]
    }
    return pool.get(pais, pool["Global"])

def buscar_trabajos_jooble(pais, perfil):
    token = "TU_JOOBLE_API_KEY"  # ← Reemplaza con tu token real
    url = f"https://jooble.org/api/{token}"
    payload = {"keywords": perfil, "location": pais}
    try:
        r = requests.post(url, json=payload, timeout=5); r.raise_for_status()
        return r.json().get("jobs", [])[:10]
    except:
        return []

# ------------------------
# DASHBOARD
# ------------------------
def show_dashboard():
    user = st.session_state.user_data
    res  = st.session_state.test_results
    if not res:
        st.info("Primero completa el Test Vocacional.")
        return

    st.subheader("📊 Dashboard Personal")
    st.markdown(f"**Correo:** {user['email']}  •  **País:** {user['pais']}")
    scores = compute_scores(res)

    st.markdown("### 🧭 Perfil Vocacional")
    for d, v in scores.items():
        st.progress(v/5)
        st.write(f"- **{d}:** {v:.1f}/5")

    st.markdown("### 🎓 Carreras sugeridas")
    for d, v in scores.items():
        if v >= 4:
            st.write(f"- {d}: ejemplos de carreras relacionadas")

    st.markdown("### 🏛️ Universidades")
    uni_list = obtener_universidades(user["pais"])
    if uni_list:
        for uni in uni_list:
            st.markdown(f"- [{uni['name']}]({uni['web_pages'][0]})")
    else:
        st.info("No se encontraron universidades para tu país.")

    st.markdown("### 💰 Becas")
    for b in becas_mockup(user["pais"]):
        st.markdown(f"- [{b['nombre']}]({b['link']})")

    st.markdown("### 💼 Vacantes (Jooble)")
    perfil_keys = " ".join([d for d, v in scores.items() if v >= 4])
    for job in buscar_trabajos_jooble(user["pais"], perfil_keys):
        title = job.get("title", "Sin título")
        link  = job.get("link", "#")
        loc   = job.get("location", "Ubicación no disponible")
        st.markdown(f"- [{title}]({link}) • {loc}")

# ------------------------
# APP Principal
# ------------------------
st.title("🌐 EduHub – Conecta tu perfil con el mundo real")

if not st.session_state.user_logged_in:
    login()
else:
    choice = st.sidebar.selectbox("🔎 Navegación", ["Inicio", "Test Vocacional", "Dashboard"])
    if choice == "Inicio":
        st.write("¡Bienvenido a EduHub! Empieza tu Test Vocacional o explora tu Dashboard.")
    elif choice == "Test Vocacional":
        show_test()
    else:
        show_dashboard()
