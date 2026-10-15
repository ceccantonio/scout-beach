# 🏐 Scout Beach Volley

Strumento per fare lo scout in allenamento (**Break** e **Side Out**) e vedere **come cambia il rendimento nel tempo**.
Le statistiche sono quelle del foglio Excel "Scout – Beach Space", riportate in Python.
Non serve saper programmare: si usa dal browser.

## Come si usa (web app)

1. Apri l'app e, se hai già fatto altri allenamenti, carica il tuo file `storico_scout.txt` nella barra a sinistra.
2. Nella scheda **Scout** scegli la data e **cosa scoutizzi oggi**: *servizio e break* oppure *ricezione e side out*
   (compaiono solo i bottoni che servono).
3. Scegli la coppia (o creane una nuova scrivendo i due nomi) e se registri i dati **della coppia** o di **un singolo
   giocatore** della coppia. Poi clicca i bottoni a ogni azione che vedi: su ogni bottone c'è il conteggio di oggi,
   e sotto compare subito l'istogramma con tutte le coppie a confronto. Se hai già i totali contati su carta,
   inseriscili nel riquadro apposito.
4. A fine allenamento clicca **Scarica lo storico aggiornato** e conserva il file: la volta dopo lo ricarichi.
5. Nella scheda **Confronto** metti a confronto le coppie (o i giocatori) che vuoi, su un allenamento o su tutti.
   Nella scheda **Andamento** vedi come cambia una coppia (o un giocatore) allenamento dopo allenamento.

> ⚠️ L'app non salva nulla sui server: i dati sono solo nel tuo file. Se chiudi la pagina senza scaricare, li perdi.

## Cosa si conta e come si calcola

| Blocco | Voci contate | Valutazioni (0–100) |
|---|---|---|
| **Break** | battuta: ace · efficace · non efficace · errore; poi: utile · trasformato · errore su utile | *val. servizio*, *val. break*, *val. globale* |
| **Side out** | ricezione: ace subito · ricezione+ · ricezione−; poi: side out diretto · indiretto · perso | *val. ricezione*, *val. side out*, *val. globale* |

I pesi delle valutazioni sono quelli dei "Parametri personali" dell'Excel e si cambiano in cima a [`scout.py`](scout.py).

- **val. servizio** = pesi su ace/efficace/non efficace/errore (3, 1, 0, −1), riportati su scala 0–100.
- **val. break** = `utili% × (1 + 3·trasformati% − 2·errore su utile%) / 4`, con trasformati ed errori calcolati sugli utili.
- **val. ricezione** = pesi su ace subiti/ricezioni+/ricezioni− (−0,5, 1, −0,2).
- **val. side out** = pesi su diretto/indiretto/perso (1, 0,8, −0,7); "perso" comprende anche gli ace subiti.
- **val. globale** = media pesata delle due valutazioni (break 40/60, side out 1,5/3,5).

## Avviarla sul tuo PC

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

Per provarla subito, carica `esempio/storico_esempio.txt` (dati inventati).

## Pubblicarla online (gratis)

Su [share.streamlit.io](https://share.streamlit.io) collega questo repository e scegli `app.py` come file principale:
otterrai un link da mandare ai giocatori.

## Il file dei dati

Testo semplice, un conteggio per riga:

```
#data;coppia;giocatore;voce;n
2026-06-08;Anna - Bruno;;ace;2
2026-06-08;Anna - Bruno;Anna;ricezione_pos;7
```

Il campo `giocatore` è vuoto quando il dato è della coppia. I dati dei singoli sono tenuti separati da quelli
della coppia: le statistiche dei giocatori sommano le righe di quel giocatore in tutte le sue coppie.

Voci ammesse: `ace efficace non_efficace errore utile trasformato errore_su_utile`
`ace_subito ricezione_pos ricezione_neg so_diretto so_indiretto so_perso`.

## Il codice

- [`scout.py`](scout.py): lettura con `loadtxt` e calcolo delle statistiche (3 funzioni). Da terminale: `python scout.py storico.txt "Anna - Bruno"`.
- [`app.py`](app.py): interfaccia web.
