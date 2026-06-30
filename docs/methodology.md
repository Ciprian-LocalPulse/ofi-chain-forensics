# Metodologie și limitări

Acest document explică exact ce face și ce NU face `ofi-chain-forensics`,
pentru ca oricine îl folosește — analist, cercetător sau dezvoltator —
să înțeleagă limitele instrumentului înainte de a-i acorda încredere.

## Ce face biblioteca

Analizează structura unui graf de tranzacții (cine trimite cui, când,
cât) și caută tipare structurale cunoscute, asociate în literatura de
cercetare cu activități de obfuscare a fondurilor sau spălare de bani:

- **Common-Input-Ownership Heuristic (CIOH)** — Meiklejohn et al., 2013,
  *"A Fistful of Bitcoins: Characterizing Payments Among Men with No
  Names"*. Dacă mai multe adrese apar ca inputuri în aceeași tranzacție,
  probabil aparțin aceluiași portofel/entitate.
- **Peeling chain detection** — tipar documentat în multiple studii de
  forensic blockchain (ex. Chainalysis, Elliptic — rapoarte publice),
  unde o sumă mare e treptat "exfoliată" prin tranzacții succesive.
- **Fan-out / Fan-in** — semnale structurale generice de distribuție sau
  agregare neobișnuită a fondurilor.
- **Rapid pass-through** — adrese care funcționează ca "hop" rapid,
  tipic pentru layering automatizat.

## Ce NU face biblioteca

- **Nu identifică identități reale.** Tot ce produce sunt adrese și
  scoruri de risc — nu nume, nu persoane, nu entități juridice.
- **Nu e probă legală.** Un scor de risc ridicat e un semnal pentru
  investigație suplimentară, nu o concluzie. Folosirea rezultatelor ca
  bază unică pentru acuzații sau decizii cu impact legal e o eroare de
  utilizare a instrumentului.
- **Nu detectează tot.** Tehnici moderne de obfuscare — CoinJoin,
  mixere bine implementate, cross-chain swaps, privacy coins (Monero,
  Zcash în modul shielded) — pot eluda intenționat aceste euristici.
  Absența unui semnal NU înseamnă absența fraudei.
- **Nu se conectează automat la blockchain-uri reale.** Biblioteca
  lucrează pe date deja extrase și normalizate. Conectarea la un
  explorer/nod (Bitcoin Core, Etherscan API, etc.) e responsabilitatea
  utilizatorului — vezi `docs/data_sources.md` pentru sugestii.
- **Nu folosește machine learning antrenat.** Scoring-ul e bazat pe
  reguli explicite și ponderate, exact pentru a rămâne auditabil. Dacă
  ai nevoie de ML, modulul `risk_scoring.py` oferă o interfață
  (`RiskFactor`) ușor de extins cu propriile semnale.

## Rate de fals-pozitiv cunoscute

- **Fan-out/Fan-in**: exchange-urile legitime (procesatoare de plăți,
  servicii de payroll în crypto) generează în mod natural fan-out/fan-in
  ridicat. Pragurile implicite (10) sunt conservatoare, dar tot pot
  semnaliza activitate complet legitimă.
- **Peeling chain**: portofele care fac rebalansare automată a UTXO-urilor
  pot produce tipare similare fără nicio intenție de obfuscare.
- **Rapid pass-through**: serviciile de swap/bridge legitime (DEX-uri,
  cross-chain bridges) au exact acest comportament prin design.

**Concluzie practică**: orice scor produs de această bibliotecă trebuie
interpretat de un analist uman, în context, niciodată automat ca
"verdict".

## Referințe

- Meiklejohn, S. et al. (2013). *A Fistful of Bitcoins: Characterizing
  Payments Among Men with No Names.* IMC '13.
- Androulaki, E. et al. (2013). *Evaluating User Privacy in Bitcoin.*
  Financial Cryptography and Data Security.
- Chainalysis & Elliptic — rapoarte publice anuale de crime report
  (terminologie și tipare structurale general acceptate în industrie).
