# 🏐 Scout Beach Volley

Uno strumento semplice per fare lo scout in allenamento e vedere **come cambia il rendimento nel tempo**.
Non serve saper programmare: si usa dal browser.

## Come si usa (web app)

1. Apri l'app e, se hai già fatto altri allenamenti, carica il tuo file `storico_scout.csv` nella barra a sinistra.
2. Nella scheda **Scout** scegli data, giocatore e fondamentale, poi clicca l'esito di ogni azione appena la vedi
   (i bottoni blu sono le azioni riuscite). Con **Annulla** correggi l'ultimo errore.
3. A fine allenamento clicca **Scarica lo storico aggiornato** e conserva il file: la volta dopo lo ricarichi.
4. Nella scheda **Andamento** vedi i grafici allenamento dopo allenamento.

> ⚠️ L'app non salva nulla sui server: i dati sono solo nel tuo file. Se chiudi la pagina senza scaricare, li perdi.

### Fondamentali ed esiti

| Fondamentale | Esiti (✅ = riuscito) |
|---|---|
| muro | ✅ punto · tocco · errore |
| battuta | ✅ ace · in gioco · errore |
| ricezione | ✅ perfetta · ✅ positiva · negativa · errore |
| difesa | ✅ riuscita · errore |
| attacco | ✅ punto · continua · errore |
| alzata | ✅ riuscita · errore |
| break | ✅ vinto · perso: punto giocato **mentre battiamo** (giocatore = chi batte) |
| sideout | ✅ vinto · perso: punto giocato **mentre riceviamo** (giocatore = chi riceve) |

- **Percentuale** = azioni riuscite / azioni totali.
- **Efficienza** = (riuscite − errori) / azioni totali.

## Avviarla sul tuo PC

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

Per provarla subito, carica `esempio/storico_esempio.csv` (dati inventati).

## Pubblicarla online (gratis)

Su [share.streamlit.io](https://share.streamlit.io) collega questo repository e scegli `app.py` come file principale:
otterrai un link da mandare ai giocatori.

## Il file dei dati

È un testo semplice, una azione per riga (si apre anche con Excel):

```
#data;giocatore;fondamentale;esito
2026-10-13;Mario;attacco;punto
2026-10-13;Mario;ricezione;positiva
```

## Il codice

Tutto il calcolo è in [`scout.py`](scout.py) (3 funzioni, `loadtxt` per leggere i dati);
l'interfaccia web è in [`app.py`](app.py). Da terminale: `python scout.py storico.csv Mario`.
