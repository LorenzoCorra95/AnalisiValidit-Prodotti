import pandas as pd
import streamlit as st
from datetime import datetime
from io import BytesIO
import numpy as np
import pages.funzioni.FunzioniPersonalizzate as f

st.set_page_config(layout="wide")

if ("gdm" and "ord" and "anag") in st.session_state:

    st.subheader("Tabella Giornale di magazzino")
    gdm_def=st.session_state["gdm"].copy()
    gdm_def["Minsan"]=gdm_def["Prodotto"].apply(lambda x: x[0:9])
    gdm_def["Descrizione"]=gdm_def["Prodotto"].apply(lambda x:x[12:])
    gdm_def=gdm_def.drop("Prodotto",axis=1)
    gdm_def["Riferimento Ordine Carico"]=gdm_def["Riferimento Ordine Carico"].apply(lambda x: f.ConvertiOrdine(x) if len(x)==9 else x)
    gdm_def["Validità residua"]=(gdm_def["Data scadenza"]-gdm_def["Data DDT Carico"])/np.timedelta64(1,"D")/30.44
    gdm_def["Validità confezione integra"]=gdm_def.merge(st.session_state.anag,on="Minsan",how="left")["Validità confezione integra"]
    gdm_def["Validità confezione integra num"]=gdm_def["Validità confezione integra"].apply(lambda x: int(str(x)[0:2]) if "MESI" in str(x) else 0)*2/3
    gdm_def["Esito"]=gdm_def.apply(lambda x: "SUPERIORE" if x["Validità residua"] > x["Validità confezione integra num"] else "INFERIORE",axis=1)
    intestazioni=[
    "Data Attività","Magazzino", "Minsan","Descrizione","Riferimento Ordine Carico","Riferimento DDT Carico","Data DDT Carico","Lotto",
    "Data scadenza","Qta Movimentata","Validità residua","Validità confezione integra","Esito"]
    indiceInt=[indice for indice in [gdm_def.columns.get_loc(i) for i in intestazioni]]
    st.session_state["gdm_def"]=gdm_def
    st.dataframe(st.session_state["gdm_def"].iloc[:,indiceInt],use_container_width=True)

    st.subheader("Tabella Ordini")
    ord=st.session_state["ord"]
    anag=st.session_state["anag"]
    ord_def=pd.merge(ord,anag,left_on="Prodotto",right_on="Codice",how="left")
    ord_def["Ordine"]=ord_def.apply(lambda x: f.CreaOrdine(x["Anno"],x["Num."]),axis=1)
    intestazioni=[
    "Ordine", "Data ordine",
    "Fornitore",
    "Autorizzazione", "Minsan","Descrizione","Qta/Val Rettificata", 
    "Prezzo Unit.","Validità confezione integra"]
    indiceInt=[indice for indice in [ord_def.columns.get_loc(i) for i in intestazioni]]
    st.session_state["ord_def"]=ord_def
    st.dataframe(st.session_state["ord_def"].iloc[:,indiceInt],use_container_width=True)

    st.subheader("Elaborazione Due Terzi",divider="blue")
    data_in_carico=st.date_input("Seleziona una data iniziale di carico")
    evasi_tot,evasi_parz,non_evasi=f.EvasioneOrdini(st.session_state.gdm_def, st.session_state.ord_def,data_in_carico)
    df=st.session_state["ordini_caricati"]
    lista_ord=df["Ordine"].unique()
    ordine_sel=st.selectbox("Seleziona l'ordine da visualizzare",lista_ord,key="ordine_sel")
    cont=st.container(border=True)
    c1,c2,c3,c4=cont.columns(4)
    stato_ord=c1.text_input("Stato ordine",value="EVASO TOTALE" if ordine_sel in evasi_tot else "EVASO PARZIALE" if ordine_sel in evasi_parz else "NON EVASO")
    intestazioni=[
    "Data Attività","Magazzino","Minsan","Descrizione","Riferimento Ordine Carico","Riferimento DDT Carico","Data DDT Carico","Lotto",
    "Data scadenza","Qta Movimentata","Validità residua","Validità confezione integra","Esito"]
    indiceInt=[indice for indice in [gdm_def.columns.get_loc(i) for i in intestazioni]]
    gdm=st.session_state.gdm_def[st.session_state.gdm_def["Riferimento Ordine Carico"]==ordine_sel].iloc[:,indiceInt]
    esito_ord=c2.text_input("Esito 2/3",value= "INFERIORE" if "INFERIORE" in gdm["Esito"].tolist() else "SUPERIORE",disabled=True)
                        
    df=st.session_state["ordini_caricati"]
    df_f=df[df["Ordine"]==ordine_sel]
    st.write(f"Ordinato con ordine {ordine_sel}")
    st.dataframe(df_f,use_container_width=True)
    st.write(f"Caricato per ordine {ordine_sel}")
    st.dataframe(gdm,use_container_width=True)

    cont=st.container()
    c1,c2,c3=cont.columns([0.2,0.2,1-0.2*2])

    excel_bytes = f.to_excel(gdm,ordine_sel)
    c1.download_button(
        label="📥 Scarica Excel",
        data=excel_bytes,
        file_name=f"Esito 2 terzi ordine {ordine_sel}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True)
    
    testo = f.creaMail(df_f,gdm)
    c2.download_button(
        label="📨 Scrivi Mail",
        data=testo,
        file_name=f"Mail 2 terzi ordine {ordine_sel}.txt",
        mime="text/plain",
        use_container_width=True
    )



   
