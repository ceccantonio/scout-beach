"""Statistiche beach volley da un semplice file di testo.

Ogni riga del file è una azione:   data;giocatore;fondamentale;esito
    2026-10-13;Mario;attacco;punto
Le righe che iniziano con # (e quelle non valide, come un'intestazione) vengono ignorate.

Per break point e sideout si usano due "fondamentali" speciali:
    break    -> giocatore = chi batte,    esito = vinto | perso  (punto vinto/perso mentre battiamo)
    sideout  -> giocatore = chi riceve,   esito = vinto | perso  (punto vinto/perso mentre riceviamo)

Uso da terminale:   python scout.py storico.csv [Giocatore]
"""
import io
import sys

import numpy as np
import pandas as pd

COLONNE = ["data", "giocatore", "fondamentale", "esito"]

# fondamentale -> {esito: True se conta come "riuscito"}
FONDAMENTALI = {
    "muro":      {"punto": True, "tocco": False, "errore": False},
    "battuta":   {"ace": True, "in_gioco": False, "errore": False},
    "ricezione": {"perfetta": True, "positiva": True, "negativa": False, "errore": False},
    "difesa":    {"riuscita": True, "errore": False},
    "attacco":   {"punto": True, "continua": False, "errore": False},
    "alzata":    {"riuscita": True, "errore": False},
    "break":     {"vinto": True, "perso": False},
    "sideout":   {"vinto": True, "perso": False},
}


def carica(src):
    """Legge il file (percorso o file-like) in un DataFrame con le colonne COLONNE."""
    righe = np.loadtxt(src, dtype=str, delimiter=";", comments="#", ndmin=2, encoding="utf-8-sig")
    df = pd.DataFrame(righe, columns=COLONNE).apply(lambda c: c.str.strip().str.lower())
    df["giocatore"] = df.giocatore.str.title()
    return df[df.fondamentale.isin(FONDAMENTALI)]  # scarta intestazioni e righe sbagliate


def salva(df):
    """Il DataFrame come testo, rileggibile con carica()."""
    return "#" + ";".join(COLONNE) + "\n" + df.to_csv(sep=";", header=False, index=False)


def statistiche(df, per=("giocatore", "fondamentale")):
    """Totale, riusciti, errori, % riusciti ed efficienza, raggruppati per le colonne in `per`.

    percentuale = riusciti / totale
    efficienza  = (riusciti - errori) / totale   (per l'attacco è l'efficienza classica)
    """
    df = df.assign(ok=[FONDAMENTALI[f][e] for f, e in zip(df.fondamentale, df.esito)],
                   err=df.esito == "errore")
    s = df.groupby(list(per)).agg(totale=("ok", "size"), riusciti=("ok", "sum"), errori=("err", "sum"))
    s["percentuale"] = (100 * s.riusciti / s.totale).round(1)
    s["efficienza"] = (100 * (s.riusciti - s.errori) / s.totale).round(1)
    return s


if __name__ == "__main__":
    df = carica(sys.argv[1])
    if len(sys.argv) > 2:
        df = df[df.giocatore == sys.argv[2].title()]
    print(statistiche(df).to_string())
