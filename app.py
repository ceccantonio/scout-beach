"""Web app per lo scout di allenamento: python -m streamlit run app.py"""
import io
from datetime import date

import pandas as pd
import streamlit as st

from scout import BATTUTA, BREAK, COLONNE, RICEZIONE, SIDEOUT, carica, salva, statistiche

# cosa si può scoutizzare in un allenamento: gruppi di bottoni (titolo, voci)
FOCUS = {
    "Servizio e break": [("Battuta", BATTUTA), ("Dopo la battuta (break)", BREAK)],
    "Ricezione e side out": [("Ricezione", RICEZIONE), ("Side out", SIDEOUT)],
}
NUOVA = "➕ Nuova coppia…"

st.set_page_config(page_title="Scout Beach", page_icon="🏐", layout="wide")
st.title("🏐 Scout Beach Volley")

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=COLONNE).astype({"n": int})


def aggiungi(riga):
    d = st.session_state.df
    d.loc[len(d)] = riga


def annulla():
    st.session_state.df = st.session_state.df.iloc[:-1]


def vista(dati, singoli):
    """I dati delle coppie (giocatore vuoto) oppure dei singoli giocatori, e la colonna che li identifica."""
    return (dati[dati.giocatore != ""], "giocatore") if singoli else (dati[dati.giocatore == ""], "coppia")


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
tab_scout, tab_confronto, tab_andamento = st.tabs(["📝 Scout", "📊 Confronto", "📈 Andamento"])

# --- Scout: scegli cosa scoutizzi e per chi, poi clicca ogni azione appena la vedi
with tab_scout:
    c1, c2 = st.columns(2)
    giorno = c1.date_input("Data dell'allenamento", date.today())
    blocco = c2.radio("Cosa scoutizzi oggi?", list(FOCUS), horizontal=True)
    singoli = st.radio("Registro i dati per", ["la coppia", "un singolo giocatore"], horizontal=True) != "la coppia"

    coppie = sorted(df.coppia.unique())
    scelta = st.selectbox("Coppia", coppie + [NUOVA])
    if scelta == NUOVA:
        a, b = st.columns(2)
        g1, g2 = a.text_input("Giocatore 1").strip(), b.text_input("Giocatore 2").strip()
        coppia = f"{g1} - {g2}".title() if g1 and g2 else None
    else:
        coppia = scelta
    giocatore = ""
    if singoli and coppia:
        giocatore = st.radio("Quale giocatore?", coppia.split(" - "), horizontal=True)

    # i bottoni mostrano quante azioni hai già registrato oggi per questa coppia/giocatore
    gia = df[(df.data == str(giorno)) & (df.coppia == coppia) & (df.giocatore == giocatore)].groupby("voce").n.sum()
    for titolo, gruppo in FOCUS[blocco]:
        st.markdown(f"**{titolo}**")
        for col, voce in zip(st.columns(len(gruppo)), gruppo):
            col.button(f"{voce.replace('_', ' ')} · {gia.get(voce, 0)}", key=voce, use_container_width=True,
                       on_click=aggiungi, args=([str(giorno), coppia, giocatore, voce, 1],), disabled=not coppia)
    st.button("↩️ Annulla l'ultima", on_click=annulla, disabled=df.empty)

    with st.expander("Hai già i totali (es. contati su carta)? Inseriscili qui"):
        with st.form("totali", clear_on_submit=True):
            voci = [v for _, gruppo in FOCUS[blocco] for v in gruppo]
            colonne = st.columns(4)
            n = {v: colonne[i % 4].number_input(v.replace("_", " "), 0, step=1, key=f"tot_{v}")
                 for i, v in enumerate(voci)}
            if st.form_submit_button("Aggiungi i totali", disabled=not coppia):
                for voce, tot in n.items():
                    if tot:
                        aggiungi([str(giorno), coppia, giocatore, voce, tot])
                st.rerun()

    # istogramma di oggi: tutte le coppie (o i singoli) a confronto
    st.subheader(f"Confronto di oggi – {giorno}")
    dati, chiave = vista(df[df.data == str(giorno)], singoli)
    oggi = statistiche(dati, [chiave])[list(FOCUS).index(blocco)]
    if oggi.empty:
        st.caption("Appena inserisci dei dati compare qui il confronto tra coppie.")
    else:
        st.bar_chart(oggi.filter(like="val."), stack=False)
        st.dataframe(oggi, use_container_width=True)
    st.caption("Ultime righe inserite")
    st.dataframe(df.tail(5).iloc[::-1], use_container_width=True, hide_index=True)

# --- Confronto: scegli tu quali coppie (o giocatori) e quali misure mettere a confronto
with tab_confronto:
    if df.empty:
        st.info("Ancora nessun dato: inserisci qualche azione nella scheda Scout o carica il tuo storico.")
    else:
        c1, c2, c3 = st.columns(3)
        singoli_c = c1.radio("Confronta", ["Coppie", "Singoli giocatori"], horizontal=True) != "Coppie"
        blocco_c = c2.radio("Statistiche", list(FOCUS), horizontal=True)
        quando = c3.selectbox("Allenamento", ["Tutti insieme"] + sorted(df.data.unique(), reverse=True))
        dati, chiave = vista(df if quando == "Tutti insieme" else df[df.data == quando], singoli_c)
        tab = statistiche(dati, [chiave])[list(FOCUS).index(blocco_c)]
        if tab.empty:
            st.info("Nessun dato per questa scelta.")
        else:
            scelti = st.multiselect(f"{chiave.title()} da confrontare", list(tab.index), default=list(tab.index))
            misure = st.multiselect("Misure", list(tab.columns[1:]), default=[c for c in tab if c.startswith("val.")])
            st.bar_chart(tab.loc[scelti, misure], stack=False)
            st.dataframe(tab.loc[scelti], use_container_width=True)

# --- Andamento: come cambiano le valutazioni da un allenamento all'altro
with tab_andamento:
    c1, c2 = st.columns(2)
    singoli_a = c1.radio("Mostra", ["Coppie", "Singoli giocatori"], horizontal=True) != "Coppie"
    dati, chiave = vista(df, singoli_a)
    if dati.empty:
        st.info("Ancora nessun dato: inserisci qualche azione nella scheda Scout o carica il tuo storico.")
    else:
        scelto = c2.selectbox(chiave.title(), sorted(dati[chiave].unique()))
        mio = dati[dati[chiave] == scelto]
        for nome, tot, nel_tempo in zip(FOCUS, statistiche(mio, [chiave]), statistiche(mio, ["data", chiave])):
            st.subheader(nome)
            if nel_tempo.empty:
                st.caption("Nessun dato.")
                continue
            val = nel_tempo.droplevel(chiave).filter(like="val.")   # solo le valutazioni, indice = data
            val.index = pd.to_datetime(val.index)
            (st.bar_chart if len(val) == 1 else st.line_chart)(val)
            st.caption("Totale di tutti gli allenamenti")
            st.dataframe(tot, use_container_width=True)
