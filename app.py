"""Web app per lo scout di allenamento: python -m streamlit run app.py"""
import io
from datetime import date

import pandas as pd
import streamlit as st

from scout import BATTUTA, BREAK, COLONNE, RICEZIONE, SIDEOUT, VOCI, carica, salva, statistiche

st.set_page_config(page_title="Scout Beach", page_icon="🏐", layout="wide")
st.title("🏐 Scout Beach Volley")

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=COLONNE)

# --- Barra laterale: lo storico va caricato all'inizio e scaricato alla fine
with st.sidebar:
    st.header("Il tuo storico")
    up = st.file_uploader("1. Carica il file dei precedenti allenamenti (se ce l'hai)", type="txt")
    if up and st.session_state.get("up_id") != up.file_id:  # carica una sola volta per file
        st.session_state.df = carica(io.StringIO(up.getvalue().decode("utf-8-sig")))
        st.session_state.up_id = up.file_id
    st.download_button("2. Scarica lo storico aggiornato", salva(st.session_state.df),
                       file_name="storico_scout.txt", mime="text/plain", type="primary", use_container_width=True)
    st.warning("I dati restano solo finché questa pagina è aperta: "
               "**scarica il file a fine allenamento** e ricaricalo la volta dopo.")

df = st.session_state.df
tab_scout, tab_andamento = st.tabs(["📝 Scout", "📈 Andamento"])

# --- Scout: scegli atleta, poi clicca ogni azione appena la vedi
with tab_scout:
    c1, c2, c3 = st.columns(3)
    giorno = c1.date_input("Data dell'allenamento", date.today())
    esistente = c2.selectbox("Atleta / coppia", sorted(df.atleta.unique()), index=None, placeholder="scegli…")
    nuovo = c3.text_input("…oppure scrivi un nuovo nome")
    atleta = nuovo.strip().title() or esistente

    def bottoni(titolo, voci):
        st.markdown(f"**{titolo}**")
        for col, voce in zip(st.columns(len(voci)), voci):
            if col.button(voce.replace("_", " "), key=voce, use_container_width=True, disabled=not atleta):
                df.loc[len(df)] = [str(giorno), atleta, voce, 1]

    bottoni("Battuta", BATTUTA)
    bottoni("Dopo la battuta (break)", BREAK)
    bottoni("Ricezione", RICEZIONE)
    bottoni("Side out", SIDEOUT)

    with st.expander("Hai già i totali (es. contati su carta)? Inseriscili qui"):
        with st.form("totali", clear_on_submit=True):
            n = {v: col.number_input(v.replace("_", " "), 0, step=1, key=f"tot_{v}")
                 for v, col in zip(VOCI, st.columns(len(VOCI) // 2 + 1) * 2)}
            if st.form_submit_button("Aggiungi i totali") and atleta:
                for voce, tot in n.items():
                    if tot:
                        df.loc[len(df)] = [str(giorno), atleta, voce, tot]

    if atleta:
        st.subheader(f"{atleta} – {giorno}")
        brk, sid = statistiche(df[(df.data == str(giorno)) & (df.atleta == atleta)])
        st.dataframe(brk, use_container_width=True)
        st.dataframe(sid, use_container_width=True)

    st.caption("Ultime righe inserite")
    st.dataframe(df.tail(8).iloc[::-1], use_container_width=True, hide_index=True)
    if st.button("↩️ Annulla l'ultima", disabled=df.empty):
        st.session_state.df = df.iloc[:-1]
        st.rerun()

# --- Andamento: come cambiano le valutazioni da un allenamento all'altro
with tab_andamento:
    if df.empty:
        st.info("Ancora nessun dato: inserisci qualche azione nella scheda Scout o carica il tuo storico.")
    else:
        a = st.selectbox("Atleta / coppia", sorted(df.atleta.unique()), key="a_andamento")
        mio = df[df.atleta == a]
        for nome, tot, nel_tempo in zip(("Break (battuta)", "Side out (ricezione)"),
                                        statistiche(mio), statistiche(mio, ["data", "atleta"])):
            st.subheader(nome)
            if nel_tempo.empty:
                st.caption("Nessun dato.")
                continue
            val = nel_tempo.droplevel("atleta").filter(like="val.")   # solo le valutazioni, indice = data
            val.index = pd.to_datetime(val.index)
            (st.bar_chart if len(val) == 1 else st.line_chart)(val)
            st.caption("Totale di tutti gli allenamenti")
            st.dataframe(tot, use_container_width=True)
