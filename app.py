
import streamlit as st

st.set_page_config(page_title="EduHub - Tu Futuro en Marcha", layout="wide")

st.markdown(
    '''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    .stApp {
        background-color: #F3F7FB;
    }
    h1, h2, h3 {
        color: #0A1D37;
    }
    .menu-title {
        font-size: 22px;
        font-weight: 600;
        margin-bottom: 10px;
    }
    </style>
    ''',
    unsafe_allow_html=True
)

st.title("🚀 EduHub: Ecosistema de Orientación y Empleabilidad")

# Sidebar menú
menu = st.sidebar.radio("Navegar a:", [
    "1. Test Vocacional",
    "2. Panorama de Carreras",
    "3. Vacantes Laborales",
    "4. Universidades",
    "5. Becas",
    "6. Cursos",
    "7. Indicadores Salariales",
    "8. Plan Personal de Acción"
])

# Contenido de cada panel
if menu == "1. Test Vocacional":
    st.header("🧠 Test Vocacional")
    st.write("Responde un test interactivo para descubrir tu perfil e intereses profesionales.")

elif menu == "2. Panorama de Carreras":
    st.header("🌐 Panorama de Carreras")
    st.write("Explora opciones profesionales alineadas a tu perfil vocacional. Conoce qué se estudia, qué habilidades se requieren y qué oportunidades ofrece cada carrera.")

elif menu == "3. Vacantes Laborales":
    st.header("💼 Vacantes Laborales")
    st.write("Accede a ofertas laborales actualizadas según tu país, perfil o interés.")

elif menu == "4. Universidades":
    st.header("🎓 Universidades")
    st.write("Busca dónde estudiar tu carrera ideal, según país, modalidad y requisitos.")

elif menu == "5. Becas":
    st.header("💰 Becas")
    st.write("Encuentra oportunidades de financiamiento para tu educación. Filtra por país y nivel académico.")

elif menu == "6. Cursos":
    st.header("📚 Cursos Complementarios")
    st.write("Accede a cursos que te ayudarán a reforzar habilidades clave o reconvertirte profesionalmente.")

elif menu == "7. Indicadores Salariales":
    st.header("📈 Indicadores Salariales")
    st.write("Consulta rangos salariales por profesión, país y nivel de experiencia.")

elif menu == "8. Plan Personal de Acción":
    st.header("🧭 Plan Personal de Acción")
    st.write("Recibe una hoja de ruta personalizada con los próximos pasos para alcanzar tu meta profesional.")

st.info("💡 Tip: Este demo solo muestra el esquema general. Podemos conectar APIs y bases de datos reales para tenerlo 100% funcional.")
