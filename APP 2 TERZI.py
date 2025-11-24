import streamlit as st
import pandas as pd
from io import StringIO


st.maxUploadSize = 400
st.set_page_config(layout="wide")

@st.dialog("Esito operazione")
def messaggio(testo):
    st.write(testo)


st.subheader("CARICA I TUOI FILE",divider="orange")
FileGdm = st.file_uploader("Carica il file del giornale di magazzino", type = ["xlsx", "csv", "xls","parquet","txt"],accept_multiple_files=False)
FileAreas = st.file_uploader("Carica il file degli ordini", type = ["xlsx", "csv", "xls","parquet","txt"],accept_multiple_files=False)
FileAnag = st.file_uploader("Carica il file dell'anagrafica", type = ["xlsx", "csv", "xls","parquet","txt"],accept_multiple_files=False)

if FileGdm:
    try:
        if FileGdm.name.endswith(".csv") or FileGdm.name.endswith(".txt"):
                df = pd.read_csv(FileGdm, sep = ";", encoding="latin-1",dtype={"Riferimento DDT Carico":str})      
        elif FileGdm.name.endswith(".xlsx") or FileGdm.name.endswith(".xls"):
            try:
                df = pd.read_excel(FileGdm,engine="openpyxl",dtype={"Riferimento DDT Carico":str})
            except:
                df = pd.read_excel(FileGdm,engine="pyxlsb",dtype={"Riferimento DDT Carico":str})
        df["Data Attività"]=pd.to_datetime(df["Data Attività"],dayfirst=True)
        df["Data DDT Carico"]=pd.to_datetime(df["Data DDT Carico"],dayfirst=True)
        df["Data scadenza"]=pd.to_datetime(df["Data scadenza"],dayfirst=True)
        st.session_state.gdm=df
    except:
         messaggio("Non è stato possibile caricare il file!")

if FileAreas:
    # try:
        if FileAreas.name.endswith(".csv") or FileAreas.name.endswith(".txt"):
                df = pd.read_csv(FileAreas, sep = ";", encoding="latin-1")        
        elif FileAreas.name.endswith(".xlsx") or FileAreas.name.endswith(".xls"):
            try:
                df = pd.read_excel(FileAreas,engine="openpyxl")
            except:
                df = pd.read_excel(FileAreas,engine="calamine")
        campi = [
        "Anno", "Num.", "Data ordine",
        "Fornitore",
        "Autorizzazione", "Prodotto", "Descrizione","Qta/Val Rettificata", 
        "Prezzo Unit."
        ]
        df=df[campi]
        df["Data ordine"]=pd.to_datetime(df["Data ordine"],dayfirst=True)
        st.session_state.ord=df
    # except:
    #      messaggio("Non è stato possibile caricare il file!")

if FileAnag:
    try:
        if FileAnag.name.endswith(".csv") or FileAnag.name.endswith(".txt"):
                df = pd.read_csv(FileAnag, sep = ";", encoding="latin-1",dtype={"MinSan10":str})     
        elif FileAnag.name.endswith(".xlsx") or FileAnag.name.endswith(".xls"):
            try:
                df = pd.read_excel(FileAnag,engine="openpyxl",dtype={"MinSan10":str})
            except:
                df = pd.read_excel(FileAnag,engine="pyxlsb",dtype={"MinSan10":str})
        
        df=df.rename(columns={"MinSan10":"Minsan"})
        st.session_state.anag=df
    except:
         messaggio("Non è stato possibile caricare il file!")
