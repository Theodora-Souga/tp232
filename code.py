import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# Configuration de la page
st.set_page_config(page_title="Data Collect Cameroun", page_icon="🇨🇲", layout="wide")

# Style CSS personnalisé pour l'interface
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DONNÉES ---
def get_connection():
    return sqlite3.connect('enseignants_cm.db', check_same_thread=False)

def init_db():
    conn = get_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS data (
                    matricule TEXT PRIMARY KEY, 
                    nom TEXT, 
                    fonction TEXT, 
                    region TEXT)''')
    conn.commit()

# --- LOGIQUE APP ---
init_db()

st.sidebar.title("🛠 Navigation")
page = st.sidebar.radio("Aller vers :", ["Formulaire d'Enregistrement", "Tableau de Bord (Stats)"])

REGIONS = ["Adamaoua", "Centre", "Est", "Extrême-Nord", "Littoral", "Nord", "Nord-Ouest", "Ouest", "Sud", "Sud-Ouest"]
FONCTIONS = ["Professeur", "Proviseur", "Directeur de CES", "Vacataire en poste"]

if page == "Formulaire d'Enregistrement":
    st.header("📝 Collecte des données des enseignants du secondaire au Cameroun")
    st.info("Veuillez remplir tous les champs ci-dessous pour vous enregistrer.")
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            matricule = st.text_input("Matricule unique", placeholder="Ex: 0582349Z").upper()
            nom = st.text_input("Nom Complet", placeholder="Ex: ATANGANA Bernard")
        with col2:
            fonction = st.selectbox("Fonction occupée", FONCTIONS)
            region = st.selectbox("Région de service", REGIONS)
        
        btn = st.button("Soumettre l'enregistrement")
        
        if btn:
            if matricule and nom:
                try:
                    conn = get_connection()
                    conn.execute("INSERT INTO data VALUES (?,?,?,?)", (matricule, nom, fonction, region))
                    conn.commit()
                    st.success(f"✅ Enregistrement réussi pour le matricule {matricule}")
                except sqlite3.IntegrityError:
                    st.error("❌ Ce matricule existe déjà dans la base de données.")
            else:
                st.warning("⚠️ Le matricule et le nom sont obligatoires.")

else:
    st.header("📊 Statistiques et Visualisation")
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM data", conn)
    
    if not df.empty:
        # Chiffres clés
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Inscrits", len(df))
        c2.metric("Régions couvertes", df['region'].nunique())
        c3.metric("Vacataires", len(df[df['fonction'] == "Vacataire en poste"]))
        
        st.divider()
        
        # Graphiques
        g1, g2 = st.columns(2)
        with g1:
            fig_reg = px.bar(df['region'].value_counts(), title="Répartition par Région", 
                             labels={'value':'Effectif', 'index':'Région'}, color_discrete_sequence=['#28a745'])
            st.plotly_chart(fig_reg, use_container_width=True)
        
        with g2:
            fig_fct = px.pie(df, names='fonction', title="Proportion par Fonction", hole=0.4)
            st.plotly_chart(fig_fct, use_container_width=True)
            
        st.subheader("📋 Liste brute des données")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Aucune donnée enregistrée pour le moment.")
