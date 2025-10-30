import streamlit as st
import pandas as pd
from io import StringIO


st.maxUploadSize = 400
st.set_page_config(layout="wide")

@st.dialog("Esito operazione")
def messaggio(testo):
    st.write(testo)
st.title("Incolla dati da Excel")


st.subheader("GIORNALE DI MAGAZZINO",divider="orange")
gdm_data = st.text_area("Incolla qui i dati del giornale di magazzino, con le intestazioni (Ctrl+V):",height=400,key="tab_gdm")

if gdm_data:
    intestazioni=[
    "Data Attività","Magazzino", "Prodotto","Riferimento Ordine Carico","Riferimento DDT Carico","Lotto",
    "Qta Movimentata","Causale Rettifica"]
    gdm = pd.read_csv(StringIO(gdm_data), sep="\t",dtype={"Riferimento DDT Carico":str})
    gdm["Data Attività"]=pd.to_datetime(gdm["Data Attività"],dayfirst=True)
    gdm["Data DDT Carico"]=pd.to_datetime(gdm["Data DDT Carico"],dayfirst=True)
    gdm["Data scadenza"]=pd.to_datetime(gdm["Data scadenza"],dayfirst=True)
    if st.button("Carica GDM",key="carica_gdm"):
        st.session_state["gdm"]=gdm
        messaggio("Dati caricati con successo!")
        
st.subheader("ORDINI AREAS",divider="blue")
ordini_data = st.text_area("Incolla qui i dati degli ordini Areas, con le intestazioni (Ctrl+V):",height=400,key="tab_ordini")

if ordini_data:
    ord = pd.read_csv(StringIO(ordini_data), sep="\t")
    campi = [
    "Anno", "Num.", "Data ordine",
    "Fornitore",
    "Autorizzazione", "Prodotto", "Descrizione","Qta/Val Rettificata", 
    "Prezzo Unit."
    ]
    ord=ord[campi]
    ord["Data ordine"]=pd.to_datetime(ord["Data ordine"],dayfirst=True)
    if st.button("Carica Ordini",key="carica_ordini"):
        st.session_state["ord"]=ord
        messaggio("Dati caricati con successo!")

st.subheader("ANAGRAFICA",divider="green")
anagrafica = st.text_area("Incolla qui i dati dell'anagrafica, con le intestazioni (Ctrl+V):",height=400,key="tab_anagrafica")

if anagrafica:
    anag = pd.read_csv(StringIO(anagrafica), sep="\t",dtype={"MinSan10":str})
    anag=anag.rename(columns={"MinSan10":"Minsan"})
    if st.button("Carica Anagrafica",key="carica_anag"):
        st.session_state["anag"]=anag
        messaggio("Dati caricati con successo!")