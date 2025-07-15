
import streamlit as st

st.set_page_config(page_title="EduHub | Tu Futuro en Marcha", layout="wide")

st.markdown(
    '''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        background-color: #F3F7FB;
    }
    .card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
        text-align: center;
        transition: transform 0.2s ease;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0px 6px 16px rgba(0,0,0,0.1);
    }
    .card h3 {
        color: #0A1D37;
    }
    .card p {
        color: #555;
        font-size: 14px;
    }
    .stButton>button {
        background-color: #0A1D37;
        color: white;
        border: none;
        padding: 0.5rem 1.2rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        margin-top: 10px;
    }
    .stButton>button:hover {
        background-color: #11335D;
    }
    </style>
    ''',
    unsafe_allow_html=True
)

st.title("🌐 Bienvenido a EduHub")
st.markdown("### Tu ecosistema de orientación vocacional, empleabilidad y formación continua")

# Paneles
panels = [
    {"icon": "🧠", "title": "Test Vocacional", "desc": "Descubre tus intereses y fortalezas profesionales."},
    {"icon": "🌐", "title": "Panorama de Carreras", "desc": "Explora opciones de estudio alineadas a tu perfil."},
    {"icon": "💼", "title": "Vacantes Laborales", "desc": "Encuentra empleos según tu perfil y país."},
    {"icon": "🎓", "title": "Universidades", "desc": "Busca dónde estudiar tu carrera ideal."},
    {"icon": "💰", "title": "Becas", "desc": "Aplica a oportunidades de financiamiento educativo."},
    {"icon": "📚", "title": "Cursos", "desc": "Refuerza tus habilidades con formación complementaria."},
    {"icon": "📈", "title": "Indicadores Salariales", "desc": "Consulta rangos salariales por carrera y país."},
    {"icon": "🧭", "title": "Plan de Acción", "desc": "Recibe una hoja de ruta personalizada."}
]

cols = st.columns(4)
for i, panel in enumerate(panels):
    with cols[i % 4]:
        st.markdown(f"<div class='card'><h3>{panel['icon']} {panel['title']}</h3><p>{panel['desc']}</p><form action='#'><button>Ir al panel</button></form></div>", unsafe_allow_html=True)
    if (i + 1) % 4 == 0 and i + 1 < len(panels):
        cols = st.columns(4)
