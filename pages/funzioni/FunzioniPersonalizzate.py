import pandas as pd
import streamlit as st
from dateutil.relativedelta import relativedelta as rd
from io import BytesIO
import numpy as np

def ConvertiOrdine(ord):
    anno=ord[0:5]
    n_ord=str(int(ord[-4:]))
    if anno[-2:]=="24":
        anno="2024"
    else:
        anno="2025"
    return f"DPC-{anno}-{n_ord}"


def CreaOrdine(anno,numero):
    anno=str(anno)
    numero=str(numero)
    return f"DPC-{anno}-{numero}"

def EvasioneOrdini(carichi,ordini,data_in_carico):
    lista_ord=carichi[carichi["Data Attività"].dt.date>=data_in_carico]["Riferimento Ordine Carico"].unique()
    tot_car=carichi.groupby(["Riferimento Ordine Carico","Minsan"])["Qta Movimentata"].sum().reset_index()
    ordini=pd.merge(ordini,tot_car.rename(columns={"Qta Movimentata":"Caricato"}),left_on=["Ordine","Minsan"],
                    right_on=["Riferimento Ordine Carico","Minsan"],how="left")
    ordini["Caricato"]=ordini["Caricato"].fillna(0)
    ordini["Da caricare"]=ordini["Qta/Val Rettificata"]-ordini["Caricato"]
    ordini=ordini[ordini["Ordine"].isin(lista_ord)]
    ordini["Evasione prodotto"]=ordini.apply(lambda x: "TOTALE" if x["Caricato"]==x["Qta/Val Rettificata"] else "PARZIALE" if x["Caricato"]!=0 and x["Caricato"] <
                                             x["Qta/Val Rettificata"] else "NON EVASO",axis=1)
    st.session_state["ordini_caricati"]=ordini
    lista_ev_tot=[]
    lista_ev_parz=[]
    lista_non_ev =[]
    for ord in ordini["Ordine"].unique():
        lista_stato=ordini[ordini["Ordine"]==ord]["Evasione prodotto"].unique()
        if "PARZIALE" in lista_stato or ("TOTALE" and "NON EVASO") in lista_stato:
            lista_ev_parz.append(ord)
        elif "TOTALE" in lista_stato and ("PARZIALE" and "NON EVASO") not in lista_stato:
            lista_ev_tot.append(ord)
        elif "NON EVASO" in lista_stato and ("TOTALE" and "PARZIALE") not in lista_stato:
            lista_non_ev.append(ord)
    return lista_ev_tot, lista_ev_parz, lista_non_ev 

def to_excel(df,ordine):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=f'Esito 2 terzi {ordine}')
    processed_data = output.getvalue()
    return processed_data

def creaMail(df_f,gdm):
    
    fornitore=df_f["Fornitore"].unique()[0]
    ordine=df_f["Ordine"].unique()[0]
    data_ordine=format(df_f["Data ordine"].unique()[0],'%d/%m/%Y')

    intestazione=f"Spett.le {fornitore},\n\n"

    ddt=gdm[["Riferimento DDT Carico","Data DDT Carico"]].drop_duplicates()
    inferiore=gdm[gdm["Esito"]=="INFERIORE"][["Qta Movimentata","Minsan","Descrizione","Lotto","Data scadenza"]]

    lista_ddt=[]
    for i in range(0,len(ddt)):
        testo=ddt.iloc[i,:].values
        lista_ddt.append(testo)
    
    testo_ddt=""
    for indice,lista in enumerate(lista_ddt):
        testo_ddt+=f"{lista[0]} del {format(lista[1].date(),'%d/%m/%Y')}, "
    testo_ddt=f"in riferimento a quanto in oggetto, si comunica che con DDT n. {testo_ddt[:-2]} - in allegato - (rif. " \
    f"nostro ordine n. {ordine} del {data_ordine}) sono stati consegnati:\n\n"

    lista_righe=[]
    for i in range(0,len(inferiore)):
        riga=inferiore.iloc[i,:].values
        lista_righe.append(riga)

    testo_righe_prodotti=""
    testo_ritiro=""
    for indice,riga in enumerate(lista_righe):
        qta=riga[0]
        minsan=riga[1]
        descrizione=riga[2]
        lotto=riga[3]
        scadenza=format(riga[4],'%d/%m/%Y')
        data_ritiro=format(riga[4]-rd(months=2),'%d/%m/%Y')
        testo_righe_prodotti+=f"N. {qta} conf di {descrizione}-{minsan} con scadenza ravvicinata (lotto {lotto} - Scadenza al {scadenza}),"\
        f" inferiore a DUE TERZI della scadenza nominale del prodotto;\n"
        testo_ritiro+=f"{data_ritiro} per {descrizione}-{minsan}, data ultima di utilizzo del prodotto nella catena di distribuzione DPC;\n"
    

    testo_intermezzo="Valutati i consumi della DPC di Area Vasta Regione Veneto, il Servizio scrivente si rende disponibile a trattenere la merce, "\
        "con richiesta di Vs impegno al reso/nota di accredito della quantità eventualmente rimanente al:\n\n"
    
    chiusura="Si ringrazia anticipatamente per la collaborazione e, in attesa di un Vostro riscontro, si porgono cordiali saluti.\n\n"

    mail=intestazione+testo_ddt+testo_righe_prodotti+"\n"+testo_intermezzo+testo_ritiro+"\n"+chiusura

    return mail
