
import streamlit as st
import requests
import numpy as np

st.set_page_config(page_title="EduHub Premium", layout="wide")

# Custom CSS for marketing-friendly design
st.markdown(
    '''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    .big-font { font-size:35px !important; color:#0A1D37; font-weight:bold; }
    .sub-header { font-size:25px !important; color:#0A1D37; }
    .stApp { background-color: #F4F7FB; }
    .stButton>button {
        background-color:#3D7DD9;
        color:white;
        border-radius:8px;
        padding:10px 20px;
        font-weight:bold;
    }
    </style>
    ''',
    unsafe_allow_html=True
)

# Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = {}
if "results" not in st.session_state:
    st.session_state.results = {}
if "page" not in st.session_state:
    st.session_state.page = "Inicio"

def login():
    st.sidebar.header("🔐 Inicia sesión")
    with st.sidebar.form("login_form"):
        email = st.text_input("Correo electrónico")
        country = st.selectbox("País", ["Panamá", "Colombia", "México", "Chile", "Otro"])
        submitted = st.form_submit_button("Ingresar")
        if submitted and email:
            st.session_state.logged_in = True
            st.session_state.user = {"email": email, "country": country}
            st.session_state.page = "Inicio"
            st.sidebar.success("Bienvenido, " + email)

def show_landing():
    st.markdown('<p class="big-font">Bienvenido a EduHub</p>', unsafe_allow_html=True)
    st.write("Descubre qué estudiar, dónde y cómo conseguir becas y trabajo según tu perfil.")
    if st.button("🧠 Comenzar Test"):
        st.session_state.page = "Test"

def show_test():
    st.markdown('<p class="sub-header">🧠 Test Vocacional</p>', unsafe_allow_html=True)
    st.write("Selecciona tu afinidad con cada actividad (1 nada - 5 mucho).")
    questions = {
        "Analítico": ["Resolver problemas matemáticos", "Investigar cómo funcionan las cosas", "Analizar grandes volúmenes de datos"],
        "Creativo": ["Diseñar logos o contenido visual", "Proponer soluciones innovadoras", "Expresarte artísticamente"],
        "Social": ["Ayudar a otros", "Trabajar en equipo", "Escuchar y aconsejar a personas"],
        "Técnico": ["Programar sistemas", "Entender cómo funcionan las máquinas", "Optimizar procesos industriales"],
        "Empresarial": ["Liderar proyectos", "Planificar recursos", "Negociar o vender"],
        "Realista": ["Armar/desarmar cosas", "Conducir u operar equipos", "Trabajar con las manos"]
    }
    results = {}
    for dim, qs in questions.items():
        st.write(f"### {dim}")
        scores = []
        for i, q in enumerate(qs):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(q)
            with col2:
                score = st.selectbox("", [1, 2, 3, 4, 5], key=f"{dim}_{i}")
                scores.append(score)
        results[dim] = np.mean(scores)
    if st.button("✅ Ver resultados"):
        st.session_state.results = results
        st.session_state.page = "Dashboard"

def obtener_universities(country):
    try:
        r = requests.get(f"http://universities.hipolabs.com/search?country={country}", timeout=5)
        return r.json()[:5]
    except:
        return []

def mock_scholarships(country):
    pool = {
        "Panamá": [{"name": "IFARHU", "link": "https://www.ifarhu.gob.pa"}],
        "Chile": [{"name": "Becas Chile", "link": "https://www.becaschile.cl"}],
        "Global": [{"name": "Scholarship Portal", "link": "https://www.scholarshipportal.com"}]
    }
    return pool.get(country, pool["Global"])

def jobs_demo(country, profile):
    # Placeholder simulated results
    return [
        {"title": f"Analista de Datos en {country}", "location": country, "link": "#"},
        {"title": f"Ingeniero de Software Jr. en {country}", "location": country, "link": "#"},
        {"title": f"Consultor de Negocios en {country}", "location": country, "link": "#"},
    ]

def resumen_perfil(resultados):
    top_dim = max(resultados, key=resultados.get)
    recomend = {
        "Analítico": "Ciencias, ingeniería, análisis de datos",
        "Creativo": "Diseño gráfico, publicidad, UX/UI",
        "Social": "Psicología, trabajo social, educación",
        "Técnico": "Ingeniería, programación, redes",
        "Empresarial": "Administración, economía, negocios",
        "Realista": "Logística, mantenimiento, construcción"
    }
    return f"Tu perfil dominante es **{top_dim}**. Te recomendamos explorar áreas como **{recomend[top_dim]}**."

def show_dashboard():
    user = st.session_state.user
    results = st.session_state.results
    st.markdown('<p class="sub-header">📊 Tu Dashboard</p>', unsafe_allow_html=True)

    st.write("### Resultado del Test")
    st.info(resumen_perfil(results))
    st.write("")

    st.write("### 🔎 Vacantes sugeridas")
    for job in jobs_demo(user["country"], " ".join([k for k,v in results.items() if v>3.5])):
        st.markdown(f"- [{job['title']}]({job['link']}) • {job['location']}")

    st.write("### 🎓 Universidades destacadas")
    for u in obtener_universities(user["country"]):
        st.markdown(f"- [{u['name']}]({u['web_pages'][0]})")

    st.write("### 💰 Becas disponibles")
    for b in mock_scholarships(user["country"]):
        st.markdown(f"- [{b['name']}]({b['link']})")

# MAIN
if not st.session_state.logged_in:
    login()
else:
    # Sidebar navigation
    with st.sidebar:
        st.title("EduHub")
        nav = st.radio("Ir a:", ["Inicio", "Test", "Dashboard"])
        st.session_state.page = nav

    if st.session_state.page == "Inicio":
        show_landing()
    elif st.session_state.page == "Test":
        show_test()
    elif st.session_state.page == "Dashboard":
        show_dashboard()
