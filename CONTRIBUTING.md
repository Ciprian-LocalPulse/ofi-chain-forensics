# Cum contribui

Mulțumesc pentru interes! Câteva reguli simple, ca să rămânem
consecvenți cu spiritul proiectului — cod funcțional, testat, fără
pretenții neacoperite.

## Reguli de bază

1. **Orice funcție nouă de detecție vine cu teste.** Nu acceptăm
   detectoare "pe încredere" — dacă pretinzi că ceva detectează un tipar,
   arată un test care construiește acel tipar și verifică detecția.
2. **Orice afirmație metodologică (citate, rate de fals-pozitiv) trebuie
   să aibă sursă verificabilă** sau să fie marcată explicit ca observație
   empirică proprie, nu ca fapt stabilit.
3. **Nu adăuga dependențe grele fără discuție.** Biblioteca rămâne
   intenționat minimalistă (în prezent: doar `networkx`).
4. **Cod în engleză, comentarii/documentație pot fi în română sau
   engleză** — proiectul servește în primul rând comunitatea română, dar
   contribuțiile internaționale sunt binevenite.

## Cum propui o schimbare

1. Deschide un issue descriind problema/feature-ul înainte de a scrie
   cod, dacă e o schimbare semnificativă (evită munca irosită).
2. Fork + branch descriptiv (`feature/etherscan-connector`,
   `fix/peeling-chain-infinite-loop`).
3. Rulează `pytest tests/ -v` local — toate testele trebuie să treacă.
4. Deschide PR cu descriere clară a ce s-a schimbat și de ce.

## Zone unde contribuțiile sunt deosebit de binevenite

- **Conectori pentru surse de date reale** (Etherscan, Blockstream,
  noduri proprii) — vezi `docs/data_sources.md`.
- **Detectoare noi de tipare**, documentate cu sursa conceptuală.
- **Suport pentru alte rețele** (Ethereum/EVM are particularități legate
  de contracte și evenimente, neacoperite încă în profunzime).
- **Benchmark-uri pe date publice etichetate** (dacă există dataset-uri
  publice cu adrese cunoscute ca frauduloase, validarea detectoarelor pe
  ele ar crește mult încrederea în rezultate).

## Raportare probleme de securitate

Dacă găsești o vulnerabilitate (nu un bug obișnuit), deschide un issue
marcat clar `security` sau contactează direct maintainerul, fără să
publici detalii de exploatare în clar.
