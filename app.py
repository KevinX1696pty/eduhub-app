
import streamlit as st
import requests
import numpy as np

# Custom CSS for styling
st.markdown(
    '''
    <style>
    .big-font { font-size:35px !important; color:#4B0082; font-weight:bold; }
    .sub-header { font-size:25px !important; color:#4B0082; }
    .stApp { background-color: #F8F0FF; }
    .stButton>button { background-color:#800080; color:white; border-radius:8px; padding:8px 16px; }
    </style>
    ''',
    unsafe_allow_html=True
)

st.set_page_config(page_title="EduHub Premium", layout="wide")

# Initialize session state for navigation
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = {}
if "results" not in st.session_state:
    st.session_state.results = {}
if "page" not in st.session_state:
    st.session_state.page = "Inicio"

def login():
    st.sidebar.header("🔐 Login")
    with st.sidebar.form("login_form"):
        email = st.text_input("Correo electrónico")
        country = st.selectbox("País", ["Panamá", "Colombia", "México", "Argentina", "Otro"])
        submitted = st.form_submit_button("Ingresar")
        if submitted and email:
            st.session_state.logged_in = True
            st.session_state.user = {"email": email, "country": country}
            st.session_state.page = "Inicio"
            st.sidebar.success(f"Bienvenido, {email}")

def show_landing():
    st.markdown('<p class="big-font">Bienvenido a EduHub</p>', unsafe_allow_html=True)
    st.write("Tu plataforma de orientación vocacional y laboral.")
    if st.button("Iniciar Test"):
        st.session_state.page = "Test"

def show_test():
    st.markdown('<p class="sub-header">🧠 Test Vocacional</p>', unsafe_allow_html=True)
    st.write("Responde de 1 (nada) a 5 (mucho).")
    questions = {
        "Analítico": ["Resolver problemas matemáticos", "Investigar funcionamiento", "Analizar datos"],
        "Creativo": ["Diseñar contenido", "Idear soluciones", "Expresión artística"],
        "Social": ["Ayudar a otros", "Trabajo en equipo", "Gestionar conflictos"],
        "Técnico": ["Programar tecnología", "Entender sistemas", "Procesos prácticos"],
        "Empresarial": ["Liderar proyectos", "Planificación", "Negociación"],
        "Realista": ["Trabajos manuales", "Operar equipos", "Logística"]
    }
    results = {}
    for dim, qs in questions.items():
        st.write(f"**{dim}**")
        results[dim] = np.mean([st.slider(q, 1, 5, 3, key=f"{dim}_{i}") for i, q in enumerate(qs)])
    if st.button("Guardar Resultados"):
        st.session_state.results = results
        st.session_state.page = "Dashboard"
        st.success("Resultados guardados. Ve al Dashboard.")

def obtener_universities(country):
    try:
        r = requests.get(f"http://universities.hipolabs.com/search?country={country}", timeout=5)
        return r.json()[:10]
    except:
        return []

def mock_scholarships(country):
    pool = {
        "Panamá":[{"name":"IFARHU","link":"https://ifarhu.gob.pa"}],
        "Global":[{"name":"Scholarship Portal","link":"https://scholarshipportal.com"}]
    }
    return pool.get(country, pool["Global"])

def jobs_jooble(country, profile):
    token = "TU_JOOBLE_API_KEY"
    url = f"https://jooble.org/api/{token}"
    payload = {"keywords":profile, "location":country}
    try:
        r = requests.post(url, json=payload, timeout=5)
        return r.json().get("jobs", [])[:5]
    except:
        return []

def show_dashboard():
    st.markdown('<p class="sub-header">📊 Dashboard</p>', unsafe_allow_html=True)
    user = st.session_state.user
    results = st.session_state.results
    if not results:
        st.info("Por favor completa el Test.")
        return
    left, right = st.columns(2)
    with left:
        st.write("**Usuario:**", user["email"])
        st.write("**País:**", user["country"])
        st.write("### Perfil")
        for dim, sc in results.items():
            st.progress(sc/5)
            st.write(f"- {dim}: {sc:.1f}/5")
    with right:
        st.write("### 🎓 Universidades")
        for u in obtener_universities(user["country"]):
            st.markdown(f"- [{u['name']}]({u['web_pages'][0]})")
        st.write("### 💰 Becas")
        for b in mock_scholarships(user["country"]):
            st.markdown(f"- [{b['name']}]({b['link']})")
        st.write("### 💼 Vacantes")
        profile_keys = " ".join([d for d,v in results.items() if v>=4])
        for job in jobs_jooble(user["country"], profile_keys):
            st.markdown(f"- [{job.get('title','')}]({job.get('link','#')}) • {job.get('location','')}")

# MAIN
if not st.session_state.logged_in:
    login()
else:
    # Navigation
    st.sidebar.header("Navegación")
    for p in ["Inicio", "Test", "Dashboard"]:
        if st.sidebar.button(p):
            st.session_state.page = p
    # Show page
    if st.session_state.page == "Inicio":
        show_landing()
    elif st.session_state.page == "Test":
        show_test()
    else:
        show_dashboard()
