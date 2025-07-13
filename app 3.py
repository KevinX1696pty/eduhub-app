
import streamlit as st

st.set_page_config(page_title="EduHub App", layout="wide")

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
        pais = st.selectbox("País", ["Panamá", "Colombia", "México", "Argentina", "Otro"])
        submit = st.form_submit_button("Ingresar")
        if submit and email:
            st.session_state.user_logged_in = True
            st.session_state.user_data = {"email": email, "pais": pais}
            st.success("Sesión iniciada")

def show_test():
    st.subheader("🧠 Test Vocacional - RIASEC Extendido")
    st.write("Contesta de 1 (nada) a 5 (mucho)")
    preguntas = {
        "analitico_1": "¿Te gusta resolver problemas matemáticos?",
        "analitico_2": "¿Disfrutas investigar cómo funcionan las cosas?",
        "creativo_1": "¿Te interesa escribir, dibujar o diseñar?",
        "creativo_2": "¿Te gustaría trabajar en publicidad o arte?",
        "social_1": "¿Te importa ayudar a los demás?",
        "social_2": "¿Te gustaría enseñar o trabajar con personas?",
        "tecnico_1": "¿Te atrae programar o trabajar con sistemas?",
        "tecnico_2": "¿Te gustaría construir software o hardware?",
        "empresarial_1": "¿Te gustaría liderar proyectos o negocios?",
        "empresarial_2": "¿Te interesa generar dinero a través de ideas?",
        "realista_1": "¿Prefieres actividades manuales o prácticas?",
        "realista_2": "¿Disfrutas arreglar cosas o trabajar con herramientas?"
    }

    resultados = {}
    for key, pregunta in preguntas.items():
        resultados[key] = st.slider(pregunta, 1, 5, 3)

    if st.button("Guardar resultados"):
        st.session_state.test_results = resultados
        st.success("Test completado. Revisa el dashboard.")

def show_dashboard():
    st.subheader("📊 Dashboard de Orientación")
    user = st.session_state.user_data
    results = st.session_state.test_results

    st.markdown(f"**📧 Correo:** {user['email']}")
    st.markdown(f"**🌎 País:** {user['pais']}")

    st.markdown("### 🧭 Perfil Vocacional")
    scores = {
        "Analítico": (results.get("analitico_1", 0) + results.get("analitico_2", 0)) / 2,
        "Creativo": (results.get("creativo_1", 0) + results.get("creativo_2", 0)) / 2,
        "Social": (results.get("social_1", 0) + results.get("social_2", 0)) / 2,
        "Técnico": (results.get("tecnico_1", 0) + results.get("tecnico_2", 0)) / 2,
        "Empresarial": (results.get("empresarial_1", 0) + results.get("empresarial_2", 0)) / 2,
        "Realista": (results.get("realista_1", 0) + results.get("realista_2", 0)) / 2,
    }

    for area, puntaje in scores.items():
        st.progress(puntaje / 5)
        st.write(f"**{area}:** {puntaje:.1f}/5")

    st.markdown("### 🎓 Carreras sugeridas")
    if scores["Analítico"] >= 4:
        st.write("- Ciencias, Ingeniería, Matemáticas")
    if scores["Técnico"] >= 4:
        st.write("- Desarrollo de software, Ciberseguridad")
    if scores["Creativo"] >= 4:
        st.write("- Diseño gráfico, Arquitectura")
    if scores["Social"] >= 4:
        st.write("- Psicología, Educación")
    if scores["Empresarial"] >= 4:
        st.write("- Administración, Finanzas, Marketing")
    if scores["Realista"] >= 4:
        st.write("- Técnico industrial, Construcción")

    st.markdown("### 🏛️ Universidades recomendadas")
    pais = user["pais"]
    universidades = {
        "Panamá": ["Universidad de Panamá", "USMA", "ULATINA"],
        "Colombia": ["Uniandes", "Javeriana", "EAFIT"],
        "México": ["UNAM", "IPN", "Tec de Monterrey"],
        "Argentina": ["UBA", "UTN", "Universidad Austral"],
        "Otro": ["Coursera", "edX", "Udemy"]
    }
    st.write(f"**Basado en tu país ({pais})**:")
    for u in universidades.get(pais, universidades["Otro"]):
        st.markdown(f"- {u}")

    st.markdown("### 💼 Trabajos sugeridos")
    if scores["Analítico"] >= 4:
        st.write("- Data analyst, científico de datos")
    if scores["Empresarial"] >= 4:
        st.write("- Project manager, emprendedor")
    if scores["Técnico"] >= 4:
        st.write("- Backend developer, DevOps")
    if scores["Social"] >= 4:
        st.write("- Coach, terapeuta, maestro")

# App principal
st.title("🌐 EduHub: Plataforma Vocacional Inteligente")

if not st.session_state.user_logged_in:
    login()
else:
    menu = ["Inicio", "Test Vocacional", "Dashboard"]
    choice = st.sidebar.selectbox("Navegación", menu)

    if choice == "Inicio":
        st.write("Bienvenido a EduHub. Responde el test para obtener sugerencias de carrera, universidades y trabajos.")
    elif choice == "Test Vocacional":
        show_test()
    elif choice == "Dashboard":
        show_dashboard()
