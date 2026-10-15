"""Statistiche Break (battuta) e Side Out (ricezione) di beach volley: le stesse del file Excel.

Ogni riga del file è un conteggio:   data;coppia;giocatore;voce;n
    2026-06-08;Anna - Bruno;;ace;2          (la coppia ha fatto 2 ace)
    2026-06-08;Anna - Bruno;Anna;ace;1      (Anna, singolarmente, ha fatto 1 ace)
Il campo giocatore è vuoto per i dati della coppia. Le righe che iniziano con # (o non valide) sono ignorate.

Uso da terminale:   python scout.py storico.txt [Coppia]
"""
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", message="Input line")  # avviso innocuo di loadtxt sulla riga d'intestazione

COLONNE = ["data", "coppia", "giocatore", "voce", "n"]

# Le voci che si contano (come le colonne "Assoluto" dell'Excel)
BATTUTA = ["ace", "efficace", "non_efficace", "errore"]  # tipo di battuta: si escludono a vicenda
BREAK = ["utile", "trasformato", "errore_su_utile"]      # esito delle battute "utili"
RICEZIONE = ["ace_subito", "ricezione_pos", "ricezione_neg"]
SIDEOUT = ["so_diretto", "so_indiretto", "so_perso"]
VOCI = BATTUTA + BREAK + RICEZIONE + SIDEOUT

# Pesi delle valutazioni: sono i "Parametri personali" dell'Excel, modificali a piacere
P_SERVIZIO = [3, 1, 0, -1]      # ace, efficace, non efficace, errore
P_BREAK = [1, 3, -2]            # utili, trasformati (su utili), errore su utili (su utili)
P_GLOBALE_BREAK = [0.4, 0.6]    # peso di valutazione servizio, valutazione break
P_RICEZIONE = [-0.5, 1, -0.2]   # ace subiti, ricezioni+, ricezioni-
P_SIDEOUT = [1, 0.8, -0.7]      # side out diretto, indiretto, perso (perso include gli ace subiti)
P_GLOBALE_SIDEOUT = [1.5, 3.5]  # peso di valutazione ricezione, valutazione side out


def carica(src):
    """Legge il file (percorso o file-like) in un DataFrame con le colonne COLONNE."""
    righe = np.loadtxt(src, dtype=str, delimiter=";", comments="#", ndmin=2, encoding="utf-8-sig")
    if righe.shape[1] == 4:  # vecchio formato data;atleta;voce;n -> aggiunge la colonna giocatore (vuota)
        righe = np.insert(righe, 2, "", axis=1)
    df = pd.DataFrame(righe, columns=COLONNE).apply(lambda c: c.str.strip())
    df["voce"] = df.voce.str.lower()
    df[["coppia", "giocatore"]] = df[["coppia", "giocatore"]].apply(lambda c: c.str.title())
    df = df[df.voce.isin(VOCI)]  # scarta intestazioni e righe sbagliate
    return df.astype({"n": int})


def salva(df):
    """Il DataFrame come testo, rileggibile con carica()."""
    return "#" + ";".join(COLONNE) + "\n" + df.to_csv(sep=";", header=False, index=False, lineterminator="\n")


def statistiche(df, per=("coppia",)):
    """Ritorna (tabella break, tabella side out), una riga per ogni gruppo di `per`
    (es. per=("data", "coppia") per vedere l'andamento nel tempo). Percentuali e valutazioni da 0 a 100."""
    c = df.astype({"n": int}).pivot_table(index=list(per), columns="voce", values="n", aggfunc="sum", fill_value=0)
    c = c.reindex(columns=VOCI, fill_value=0)

    # --- Break: servizio + battute utili
    bat = c[BATTUTA].sum(axis=1)
    pb = c[BATTUTA].div(bat, axis=0)                      # quota di ogni tipo di battuta
    utili = c.utile / bat
    trasf = (c.trasformato / c.utile).fillna(0)           # sugli utili (0 se non ce ne sono)
    err_ut = (c.errore_su_utile / c.utile).fillna(0)
    val_serv = (pb @ P_SERVIZIO - min(P_SERVIZIO)) / (max(P_SERVIZIO) - min(P_SERVIZIO)) * 100
    val_brk = utili * (P_BREAK[0] + P_BREAK[1] * trasf + P_BREAK[2] * err_ut) / (P_BREAK[0] + P_BREAK[1]) * 100
    brk = pd.DataFrame({
        "battute": bat, "ace %": pb.ace, "efficace %": pb.efficace, "non efficace %": pb.non_efficace,
        "errore %": pb.errore, "utili %": utili, "trasformati %": trasf, "errore su utile %": err_ut})
    percentuali = [col for col in brk if "%" in col]
    brk[percentuali] *= 100                               # da frazioni a percentuali
    brk["val. servizio"], brk["val. break"] = val_serv, val_brk
    brk["val. globale"] = (val_serv * P_GLOBALE_BREAK[0] + val_brk * P_GLOBALE_BREAK[1]) / sum(P_GLOBALE_BREAK)

    # --- Side out: ricezione + side out
    ric = c[RICEZIONE].sum(axis=1)
    pr = c[RICEZIONE].div(ric, axis=0)
    so = pd.DataFrame({"diretto": c.so_diretto / ric, "indiretto": c.so_indiretto / ric,
                       "perso": (c.ace_subito + c.so_perso) / ric})
    val_ric, val_so = (pr @ P_RICEZIONE) * 100, (so @ P_SIDEOUT) * 100
    sid = pd.DataFrame({
        "ricezioni": ric, "ace subiti %": pr.ace_subito * 100, "ricezioni+ %": pr.ricezione_pos * 100,
        "ricezioni- %": pr.ricezione_neg * 100, "diretto %": so.diretto * 100,
        "indiretto %": so.indiretto * 100, "perso %": so.perso * 100,
        "val. ricezione": val_ric, "val. side out": val_so,
        "val. globale": (val_ric * P_GLOBALE_SIDEOUT[0] + val_so * P_GLOBALE_SIDEOUT[1]) / sum(P_GLOBALE_SIDEOUT)})

    return brk[brk.battute > 0].round(1), sid[sid.ricezioni > 0].round(1)


if __name__ == "__main__":
    df = carica(sys.argv[1])
    if len(sys.argv) > 2:
        df = df[df.coppia == sys.argv[2].title()]
    for tabella in statistiche(df):
        print(tabella.to_string(), "\n")
