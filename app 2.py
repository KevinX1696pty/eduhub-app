
import streamlit as st

st.set_page_config(page_title="EduHub Demo", layout="centered")

if "user_logged_in" not in st.session_state:
    st.session_state.user_logged_in = False
if "user_data" not in st.session_state:
    st.session_state.user_data = {}
if "test_results" not in st.session_state:
    st.session_state.test_results = {}

def login():
    st.subheader("🔐 Inicia sesión para continuar")
    with st.form("login_form"):
        email = st.text_input("Correo electrónico")
        pais = st.selectbox("País", ["Panamá", "Colombia", "México", "Argentina", "Otro"])
        submit = st.form_submit_button("Ingresar")
        if submit and email:
            st.session_state.user_logged_in = True
            st.session_state.user_data = {"email": email, "pais": pais}
            st.success("Sesión iniciada")

def show_test():
    st.subheader("🎯 Test Vocacional RIASEC")
    preguntas = {
        "analitico": "¿Te gusta resolver problemas lógicos?",
        "creativo": "¿Disfrutas crear cosas nuevas (arte, diseño)?",
        "social": "¿Te sientes bien ayudando a otros?",
        "tecnico": "¿Te interesa la tecnología?",
        "empresarial": "¿Te interesa emprender o liderar?",
        "realista": "¿Prefieres trabajos prácticos y manuales?"
    }
    respuestas = {}
    for key, pregunta in preguntas.items():
        respuestas[key] = st.slider(pregunta, 1, 5, 3)

    if st.button("Guardar y ver resultados"):
        st.session_state.test_results = respuestas
        st.success("Resultados guardados. Accede al dashboard desde el menú lateral.")

def show_dashboard():
    st.subheader("📊 Tu Dashboard Personal")
    user = st.session_state.user_data
    results = st.session_state.test_results

    st.markdown(f"**Correo:** {user['email']}")
    st.markdown(f"**País:** {user['pais']}")
    st.markdown("### Perfil Vocacional:")
    st.json(results)

    st.markdown("### Carreras sugeridas:")
    if results:
        if results["analitico"] >= 4 and results["tecnico"] >= 4:
            st.write("- Ingeniería de Software")
        if results["social"] >= 4:
            st.write("- Psicología / Trabajo social")
        if results["creativo"] >= 4:
            st.write("- Diseño gráfico / Publicidad")
        if results["realista"] >= 4:
            st.write("- Técnico en mantenimiento / Construcción")
    else:
        st.info("Completa primero el test vocacional.")

# App principal
st.title("🌐 EduHub: Plataforma Vocacional Inteligente")

if not st.session_state.user_logged_in:
    login()
else:
    menu = ["Inicio", "Test Vocacional", "Dashboard"]
    choice = st.sidebar.selectbox("Navegación", menu)

    if choice == "Inicio":
        st.write("Bienvenido a EduHub. Tu guía hacia una mejor decisión profesional.")
    elif choice == "Test Vocacional":
        show_test()
    elif choice == "Dashboard":
        show_dashboard()
