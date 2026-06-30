# Surse de date

`ofi-chain-forensics` nu include conectori la blockchain-uri live —
deliberat, pentru a rămâne o bibliotecă de analiză pură, fără
dependențe de API-uri externe, chei sau rate limits impuse de terți.

Mai jos sunt opțiuni reale prin care poți obține tranzacții și le poți
normaliza la formatul așteptat (vezi `ofi_chain_forensics/graph.py`
pentru schema exactă).

## Bitcoin / UTXO-based chains

- **Bitcoin Core (nod propriu)** — `getrawtransaction` + `decoderawtransaction`
  via RPC, pentru control complet și fără dependență de servicii terțe.
- **Blockstream Esplora API** (`https://blockstream.info/api/`) — API
  public, gratuit, fără autentificare pentru interogări de bază.
- **Mempool.space API** — alternativă similară, open-source.

## Ethereum / EVM-compatible chains

- **Etherscan API** (necesită cheie gratuită) — `txlist` per adresă.
- **Nod propriu (Geth/Erigon) + `eth_getTransactionByHash`** — pentru
  control complet.
- Atenție: pe EVM, conceptul de "input/output" diferă de UTXO — pentru
  tranzacții simple, input = adresa `from`, output = adresa `to`. Pentru
  contracte și DeFi (swap-uri, multi-hop), normalizarea cere parsarea
  evenimentelor (logs), nu doar a câmpurilor de bază ale tranzacției.

## Normalizare

Indiferent de sursă, transformă fiecare tranzacție în formatul:

```json
{
  "txid": "...",
  "timestamp": 1700000000,
  "inputs": ["adresa1", "adresa2"],
  "outputs": [
    {"address": "adresa3", "amount": 0.5},
    {"address": "adresa4", "amount": 1.2}
  ],
  "fee": 0.0001
}
```

Folosește formatul cu sume explicite per output ori de câte ori sursa ta
de date le oferă — detectorii sensibili la proporții (peeling chain)
sunt mult mai precisi cu sume exacte decât cu distribuție egală
presupusă.

## Contribuții binevenite

Dacă construiești un conector pentru o sursă de date specifică
(Etherscan, Blockstream, un nod propriu etc.), un PR care adaugă un
modul `connectors/` e binevenit — vezi `CONTRIBUTING.md`.
