"""Web app per lo scout di allenamento: python -m streamlit run app.py"""
import io
from datetime import date

import pandas as pd
import streamlit as st

from scout import COLONNE, FONDAMENTALI, carica, salva, statistiche

st.set_page_config(page_title="Scout Beach", page_icon="🏐", layout="wide")
st.title("🏐 Scout Beach Volley")

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=COLONNE)

# --- Barra laterale: il tuo storico va caricato all'inizio e scaricato alla fine
with st.sidebar:
    st.header("Il tuo storico")
    up = st.file_uploader("1. Carica il file dei precedenti allenamenti (se ce l'hai)", type=["csv", "txt"])
    if up and st.session_state.get("up_id") != up.file_id:  # carica una sola volta per file
        st.session_state.df = carica(io.StringIO(up.getvalue().decode("utf-8-sig")))
        st.session_state.up_id = up.file_id
    st.download_button("2. Scarica lo storico aggiornato", salva(st.session_state.df),
                       file_name="storico_scout.csv", type="primary", use_container_width=True)
    st.warning("I dati restano solo finché questa pagina è aperta: "
               "**scarica il file a fine allenamento** e ricaricalo la volta dopo.")

df = st.session_state.df
tab_scout, tab_andamento = st.tabs(["📝 Scout", "📈 Andamento"])

# --- Scout: scegli giocatore e fondamentale, poi clicca l'esito di ogni azione
with tab_scout:
    c1, c2, c3 = st.columns(3)
    giorno = c1.date_input("Data dell'allenamento", date.today())
    esistente = c2.selectbox("Giocatore", sorted(df.giocatore.unique()), index=None, placeholder="scegli…")
    nuovo = c3.text_input("…oppure scrivi un nuovo nome")
    giocatore = nuovo.strip().title() or esistente

    fond = st.radio("Fondamentale", list(FONDAMENTALI), horizontal=True)
    st.caption("Clicca l'esito di ogni azione appena la vedi: i bottoni blu sono le azioni riuscite.")
    for col, (esito, ok) in zip(st.columns(len(FONDAMENTALI[fond])), FONDAMENTALI[fond].items()):
        if col.button(esito.replace("_", " "), key=f"{fond}-{esito}", use_container_width=True,
                      type="primary" if ok else "secondary", disabled=not giocatore):
            df.loc[len(df)] = [str(giorno), giocatore, fond, esito]

    if giocatore:
        oggi = df[(df.data == str(giorno)) & (df.giocatore == giocatore)]
        st.subheader(f"{giocatore} – {giorno}")
        st.dataframe(statistiche(oggi, ["fondamentale"]), use_container_width=True)

    st.caption("Ultime azioni inserite")
    st.dataframe(df.tail(8).iloc[::-1], use_container_width=True, hide_index=True)
    if st.button("↩️ Annulla l'ultima azione", disabled=df.empty):
        st.session_state.df = df.iloc[:-1]
        st.rerun()

# --- Andamento: come cambiano le percentuali da un allenamento all'altro
with tab_andamento:
    if df.empty:
        st.info("Ancora nessun dato: inserisci qualche azione nella scheda Scout o carica il tuo storico.")
    else:
        g = st.selectbox("Giocatore", sorted(df.giocatore.unique()), key="g_andamento")
        misura = st.radio("Misura", ["percentuale", "efficienza"], horizontal=True,
                          help="Percentuale = riusciti / totale. Efficienza = (riusciti − errori) / totale.")
        per_data = statistiche(df[df.giocatore == g], ["data", "fondamentale"])[misura].unstack()
        per_data.index = pd.to_datetime(per_data.index)
        (st.bar_chart if len(per_data) == 1 else st.line_chart)(per_data)
        st.subheader("Totale di tutti gli allenamenti")
        st.dataframe(statistiche(df[df.giocatore == g], ["fondamentale"]), use_container_width=True)
