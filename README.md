# ofi-chain-forensics

Bibliotecă Python open-source pentru **detecție de fraudă și spălare de
bani pe blockchain**, prin analiza structurală a graficului de
tranzacții (adrese, fluxuri, tipare). Modul complementar proiectului
[Open Fraud Intelligence (OFI)](https://github.com/Ciprian-LocalPulse/open-fraud-intelligence).

**100% gratuit, licență MIT, fără cont, fără API key, fără limite de
utilizare.**

## De ce există

Majoritatea uneltelor de "blockchain forensics" sunt fie produse
comerciale închise (Chainalysis, Elliptic — neaccesibile pentru
cercetători independenți, ONG-uri sau jurnaliști de investigație fără
buget), fie scripturi izolate, nedocumentate, fără teste. Acest proiect
implementează euristicile consacrate din literatura de cercetare
(citate explicit în [docs/methodology.md](docs/methodology.md)) într-o
bibliotecă curată, testată și auditabilă, utilizabilă de oricine.

**Important — citește înainte să folosești rezultatele**: niciun scor
produs aici NU e probă legală de fraudă. E un instrument de
prioritizare pentru analiști umani. Detalii complete despre limitări și
rate de fals-pozitiv cunoscute: [docs/methodology.md](docs/methodology.md).

## Ce face

- **Construiește un graf de tranzacții** dintr-o listă normalizată de
  tranzacții (`ofi_chain_forensics.graph.TransactionGraph`).
- **Clustering de adrese** prin Common-Input-Ownership Heuristic și
  detecție de adrese de rest (`ofi_chain_forensics.clustering`).
- **Detectoare de tipare suspecte**: peeling chain, fan-out, fan-in,
  rapid pass-through (`ofi_chain_forensics.patterns`).
- **Scoring de risc explicabil**, bazat pe reguli transparente — fiecare
  punct de scor vine cu o explicație în limbaj natural
  (`ofi_chain_forensics.risk_scoring`).
- **Export** în CSV, JSON, și un format compatibil direct cu dataset-ul
  OFI (`ofi_chain_forensics.export`).
- **CLI funcțional**, gata de folosit din linia de comandă.

## Instalare

```bash
git clone https://github.com/Ciprian-LocalPulse/ofi-chain-forensics.git
cd ofi-chain-forensics
pip install -r requirements.txt
```

Sau ca pachet editabil:

```bash
pip install -e .
```

## Utilizare rapidă — CLI

```bash
python -m ofi_chain_forensics.cli data/sample/sample_transactions.json \
    --blacklist data/sample/sample_blacklist.txt \
    --show-clusters \
    --out-csv results.csv \
    --out-json results.json \
    --top 15
```

Output:

```
Graf construit: 88 adrese, 42 tranzacții.

Top 15 adrese după scor de risc:
Adresa                                           Scor  Nivel
----------------------------------------------------------------------
CASHOUT0003                                    100.00  ridicat
CASHOUT0005                                    100.00  ridicat
PEEL0003                                         45.00  moderat
...
```

## Utilizare rapidă — ca bibliotecă

```python
from ofi_chain_forensics import TransactionGraph, score_addresses, top_risk_addresses

graph = TransactionGraph.from_transactions(my_transactions)
scores = score_addresses(graph, blacklist=my_known_bad_addresses)

for s in top_risk_addresses(scores, n=10):
    print(s.address, s.score, s.risk_level)
```

Vezi [examples/basic_usage.py](examples/basic_usage.py) pentru un exemplu
complet, rulabil direct.

## Format de date așteptat

```json
{
  "txid": "abc123",
  "timestamp": 1700000000,
  "inputs": ["adresa_sursa_1", "adresa_sursa_2"],
  "outputs": [
    {"address": "adresa_dest_1", "amount": 0.5},
    {"address": "adresa_dest_2", "amount": 1.2}
  ],
  "fee": 0.0001
}
```

Biblioteca nu se conectează la niciun blockchain live — lucrează pe date
deja extrase și normalizate, indiferent de sursă (Bitcoin, Ethereum,
orice altă rețea). Ghid pentru obținerea și normalizarea datelor reale:
[docs/data_sources.md](docs/data_sources.md).

## Rulare teste

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

21 de teste, acoperă fiecare modul (graf, clustering, detectoare de
tipare, scoring).

## Integrare cu OFI

Funcția `export_ofi_compatible()` produce direct format de intrare
compatibil cu structura dataset-ului
[Open Fraud Intelligence](https://github.com/Ciprian-LocalPulse/open-fraud-intelligence),
pentru a putea importa adresele cu risc ridicat ca alerte/indicatori în
ecosistemul OFI (compatibil OpenCTI/MISP via SDK-ul OFI existent).

## Limitări — pe scurt

- Nu identifică identități reale, doar adrese.
- Nu detectează obfuscare avansată (CoinJoin, mixere bune, privacy coins).
- Scoring bazat pe reguli, nu pe ML antrenat — predictibil și auditabil,
  dar nu "învață" din date noi automat.
- Rezultatele cer întotdeauna review uman.

Detalii complete: [docs/methodology.md](docs/methodology.md).

## Contribuții

Vezi [CONTRIBUTING.md](CONTRIBUTING.md). Conectori pentru surse de date
reale (Etherscan, Blockstream, noduri proprii) sunt deosebit de
binevenite.

## Licență

MIT — vezi [LICENSE](LICENSE). Gratuit pentru orice utilizare, comercială
sau necomercială, fără nicio condiție în afara păstrării notificării de
copyright.

## Susținere

Acest proiect e dezvoltat și întreținut independent, fără finanțare
instituțională. Dacă ți-a fost util,poti dona .

</div>

This repository is maintained independently, on personal time. If it has saved you hours of searching, taught you something, or you simply want to back independent open-access research and keep this list free for everyone, you can contribute directly through any of the channels below.

<table>
<tr><td colspan="2">

### 🇪🇺 European Payment — SEPA / EUR <sub>· CEA · AES-256</sub>

| Field | Detail |
|---|---|
| Recipient | Ciprian Stefan Plesca |
| IBAN | `BE83 9679 1975 8915` |
| SWIFT / BIC | `TRWIBEB1XXX` |
| Bank | Wise, Rue du Trône 100, 3rd floor, Brussels, 1050, Belgium |

</td></tr>
<tr><td colspan="2">

### 🇬🇧 United Kingdom Payment — Faster Payments / GBP <sub>· AIA · SHA-3</sub>

| Field | Detail |
|---|---|
| Recipient | Ciprian Stefan Plesca |
| Account number | `92055372` |
| Sort code | `23-14-70` |
| IBAN | `GB68 TRWI 2314 7092 0553 72` |
| SWIFT / BIC | `TRWIGB2LXXX` |
| Bank | Wise Payments Limited, 1st Floor, Worship Square, 65 Clifton Street, London, EC2A 4JE, United Kingdom |

</td></tr>
<tr><td colspan="2">

### 🇺🇸 United States Payment — ACH / Wire / USD <sub>· ICA · RSA-4096</sub>

| Field | Detail |
|---|---|
| Recipient | Ciprian Stefan Plesca |
| Account type | Checking |
| Routing number | `026073150` |
| Account number | `8314225367` |
| SWIFT / BIC | `CMFGUS33` |
| Bank | Community Federal Savings Bank, 89-16 Jamaica Ave, Woodhaven, NY, 11421, United States |

</td></tr>
</table>

<div align="center">

| ₿ Bitcoin (BTC) | Ξ Ethereum (ETH) | PP PayPal |
|---|---|---|
| `bc1qf3yy0w8z37rwavxpu38wem3yffpanw7wzj32qj` | `0x27d9a6a5b8507e6031bb044319410da96222d402` | [paypal.me/agentflowenterprise](https://paypal.me/agentflowenterprise) |

</div>
