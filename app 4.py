
import streamlit as st
import requests

# ------------------------ #
# FUNCIONES AUXILIARES
# ------------------------ #

def obtener_universidades(pais):
    try:
        url = f"http://universities.hipolabs.com/search?country={pais}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data[:10]
        else:
            return []
    except:
        return []

def becas_mockup(pais, perfil):
    becas = {
        "Panamá": [
            {"nombre": "IFARHU - Excelencia Académica", "link": "https://www.ifarhu.gob.pa"},
            {"nombre": "SENACYT - Postgrados en Ciencia", "link": "https://www.senacyt.gob.pa"},
        ],
        "México": [
            {"nombre": "CONACYT Becas de Maestría", "link": "https://www.conacyt.gob.mx"},
            {"nombre": "Becas UNAM por rendimiento", "link": "https://www.unam.mx"},
        ],
        "Global": [
            {"nombre": "Scholarship Portal EU", "link": "https://www.scholarshipportal.com"},
            {"nombre": "DAAD Alemania", "link": "https://www.daad.de/en/"},
        ]
    }
    return becas.get(pais, becas["Global"])

def buscar_trabajos_jooble(pais, profesion):
    token = "TU_API_KEY_DE_JOOBLE"  # <- reemplazar con tu token real
    url = f"https://jooble.org/api/{token}"
    payload = {
        "keywords": profesion,
        "location": pais
    }
    try:
        res = requests.post(url, json=payload)
        if res.status_code == 200:
            data = res.json()
            return data.get("jobs", [])[:10]
        else:
            return []
    except Exception as e:
        print("Error:", e)
        return []

# ------------------------ #
# APP PRINCIPAL
# ------------------------ #

st.set_page_config(page_title="EduHub", layout="wide")
st.title("🎓 EduHub: Tu camino hacia la carrera ideal")

st.markdown("Completa tu test y descubre universidades, becas y trabajos que encajan contigo.")

# Inputs simulados (para demostración)
usuario_pais = st.selectbox("🌍 ¿En qué país estás?", ["Panamá", "México", "Colombia", "Argentina"])
perfil_vocacional = st.selectbox("🧠 ¿Cuál fue tu perfil vocacional?", ["Investigador", "Artístico", "Social", "Empresarial", "Realista"])

if st.button("🔍 Mostrar resultados"):
    st.subheader("🎓 Universidades recomendadas")
    universidades = obtener_universidades(usuario_pais)
    if universidades:
        for uni in universidades:
            st.markdown(f"- [{uni['name']}]({uni['web_pages'][0]})")
    else:
        st.info("No se encontraron universidades.")

    st.subheader("💰 Becas disponibles")
    becas = becas_mockup(usuario_pais, perfil_vocacional)
    for beca in becas:
        st.markdown(f"- [{beca['nombre']}]({beca['link']})")

    st.subheader("💼 Vacantes sugeridas")
    vacantes = buscar_trabajos_jooble(usuario_pais, perfil_vocacional)
    if vacantes:
        for job in vacantes:
            st.markdown(f"🔹 [{job['title']}]({job['link']}) - {job.get('location', 'Ubicación no disponible')}")
    else:
        st.info("No se encontraron vacantes para tu perfil.")
