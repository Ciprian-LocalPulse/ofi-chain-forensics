<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0F2027,50:203A43,100:2C5364&height=220&section=header&text=ofi-chain-forensics&fontSize=46&fontColor=00FFB3&animation=fadeIn&fontAlignY=38&desc=Blockchain%20Fraud%20%26%20AML%20Pattern%20Detection&descAlignY=58&descSize=18" />

<br/>

<a href="https://github.com/Ciprian-LocalPulse/ofi-chain-forensics">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=24&duration=2800&pause=900&color=00FFB3&center=true&vCenter=true&multiline=true&repeat=true&width=820&height=70&lines=Open-source+blockchain+forensics+%E2%80%94+100%25+gratuit;Clustering+%E2%80%A2+Pattern+Detection+%E2%80%A2+Explainable+Risk+Scoring;Fara+cont.+Fara+API+key.+Fara+limite." />
</a>

<br/><br/>

[![MIT License](https://img.shields.io/badge/license-MIT-00FFB3?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-21%20passing-00C853?style=for-the-badge&logo=pytest&logoColor=white)](tests/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-FF6F00?style=for-the-badge&logo=github&logoColor=white)](CONTRIBUTING.md)

![Repo Size](https://img.shields.io/github/repo-size/Ciprian-LocalPulse/ofi-chain-forensics?style=flat-square&color=00FFB3&label=repo%20size)
![Last Commit](https://img.shields.io/github/last-commit/Ciprian-LocalPulse/ofi-chain-forensics?style=flat-square&color=00FFB3&label=last%20commit)
![Issues](https://img.shields.io/github/issues/Ciprian-LocalPulse/ofi-chain-forensics?style=flat-square&color=00FFB3&label=issues)
![Stars](https://img.shields.io/github/stars/Ciprian-LocalPulse/ofi-chain-forensics?style=social)

<br/>

<img src="https://media.giphy.com/media/3o7TKz2bX3WjAh3ulu/giphy.gif" width="1" height="1" alt="" />

</div>

---

<div align="center">

### ⚡ De ce există

</div>

> [!IMPORTANT]
> **Niciun scor produs aici NU e probă legală de fraudă.** E un instrument de prioritizare pentru analiști umani. Detalii complete: [docs/methodology.md](docs/methodology.md).

Majoritatea uneltelor de "blockchain forensics" sunt fie produse comerciale închise (Chainalysis, Elliptic — neaccesibile pentru cercetători independenți, ONG-uri sau jurnaliști de investigație fără buget), fie scripturi izolate, nedocumentate, fără teste.

Acest proiect implementează euristicile consacrate din literatura de cercetare (citate explicit în [docs/methodology.md](docs/methodology.md)) într-o bibliotecă **curată, testată și auditabilă**, utilizabilă de oricine — gratuit, fără cont, fără API key.

---

<div align="center">

### 🔍 Ce face

<table>
<tr>
<td align="center" width="33%">

**🕸️ Graf de tranzacții**
<br/>
Construiește un graf complet din date normalizate

</td>
<td align="center" width="33%">

**🧬 Clustering de adrese**
<br/>
Common-Input-Ownership Heuristic + detecție adrese de rest

</td>
<td align="center" width="33%">

**🚨 Detectoare de tipare**
<br/>
Peeling chain, fan-out, fan-in, rapid pass-through

</td>
</tr>
<tr>
<td align="center" width="33%">

**📊 Risk scoring explicabil**
<br/>
Fiecare punct de scor are o explicație în limbaj natural

</td>
<td align="center" width="33%">

**📤 Export multi-format**
<br/>
CSV, JSON, compatibil direct cu dataset-ul OFI

</td>
<td align="center" width="33%">

**⌨️ CLI funcțional**
<br/>
Gata de folosit din linia de comandă

</td>
</tr>
</table>

</div>

---

## 🚀 Instalare

```bash
git clone https://github.com/Ciprian-LocalPulse/ofi-chain-forensics.git
cd ofi-chain-forensics
pip install -r requirements.txt
```

Sau ca pachet editabil:

```bash
pip install -e .
```

---

## ⚙️ Utilizare rapidă — CLI

```bash
python -m ofi_chain_forensics.cli data/sample/sample_transactions.json \
    --blacklist data/sample/sample_blacklist.txt \
    --show-clusters \
    --out-csv results.csv \
    --out-json results.json \
    --top 15
```

```text
Graf construit: 88 adrese, 42 tranzacții.

Top 15 adrese după scor de risc:
Adresa                                           Scor  Nivel
----------------------------------------------------------------------
CASHOUT0003                                    100.00  ridicat
CASHOUT0005                                    100.00  ridicat
PEEL0003                                         45.00  moderat
...
```

## 🐍 Utilizare rapidă — ca bibliotecă

```python
from ofi_chain_forensics import TransactionGraph, score_addresses, top_risk_addresses

graph = TransactionGraph.from_transactions(my_transactions)
scores = score_addresses(graph, blacklist=my_known_bad_addresses)

for s in top_risk_addresses(scores, n=10):
    print(s.address, s.score, s.risk_level)
```

Vezi [examples/basic_usage.py](examples/basic_usage.py) pentru un exemplu complet, rulabil direct.

---

## 📦 Format de date așteptat

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

Biblioteca nu se conectează la niciun blockchain live — lucrează pe date deja extrase și normalizate, indiferent de sursă (Bitcoin, Ethereum, orice altă rețea). Ghid pentru obținerea și normalizarea datelor reale: [docs/data_sources.md](docs/data_sources.md).

---

## 🧪 Rulare teste

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

<div align="center">

![Tests](https://img.shields.io/badge/✓%2021%2F21%20tests%20passing-00C853?style=for-the-badge)

</div>

21 de teste, acoperă fiecare modul (graf, clustering, detectoare de tipare, scoring).

---

## 🔗 Integrare cu OFI

Funcția `export_ofi_compatible()` produce direct format de intrare compatibil cu structura dataset-ului [Open Fraud Intelligence](https://github.com/Ciprian-LocalPulse/open-fraud-intelligence), pentru a putea importa adresele cu risc ridicat ca alerte/indicatori în ecosistemul OFI (compatibil OpenCTI/MISP via SDK-ul OFI existent).

---

## ⚠️ Limitări — pe scurt

| Limitare | Detaliu |
|---|---|
| 🆔 Identitate | Nu identifică identități reale, doar adrese |
| 🌀 Obfuscare | Nu detectează CoinJoin, mixere bune, privacy coins |
| 🤖 Scoring | Bazat pe reguli, nu pe ML antrenat — predictibil și auditabil, nu "învață" automat |
| 👁️ Review | Rezultatele cer întotdeauna review uman |

Detalii complete: [docs/methodology.md](docs/methodology.md).

---

## 🤝 Contribuții

Vezi [CONTRIBUTING.md](CONTRIBUTING.md). Conectori pentru surse de date reale (Etherscan, Blockstream, noduri proprii) sunt deosebit de bineveniți.

## 📄 Licență

**MIT** — vezi [LICENSE](LICENSE). Gratuit pentru orice utilizare, comercială sau necomercială, fără nicio condiție în afara păstrării notificării de copyright.

---

<div align="center">

## 💚 Susținere

Acest proiect e dezvoltat și întreținut independent, fără finanțare instituțională.
Dacă ți-a fost util, poți dona prin oricare din canalele de mai jos.

</div>

<table align="center">
<tr><td colspan="2" align="center">

### 🇪🇺 European Payment — SEPA / EUR <sub>· CEA · AES-256</sub>

| Field | Detail |
|---|---|
| Recipient | Ciprian Stefan Plesca |
| IBAN | `BE83 9679 1975 8915` |
| SWIFT / BIC | `TRWIBEB1XXX` |
| Bank | Wise, Rue du Trône 100, 3rd floor, Brussels, 1050, Belgium |

</td></tr>
<tr><td colspan="2" align="center">

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
<tr><td colspan="2" align="center">

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

<br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:2C5364,50:203A43,100:0F2027&height=120&section=footer" />

<sub>Made with ☕ and too much entropy, independently, in Romania.</sub>

</div>
