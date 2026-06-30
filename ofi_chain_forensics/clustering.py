"""
clustering.py
--------------
Euristici clasice de clustering al adreselor pe baza graficului de
tranzacții. Acestea sunt tehnici consacrate în literatura de cercetare
blockchain (Meiklejohn et al. 2013, "A Fistful of Bitcoins"; Androulaki
et al. 2013) — NU sunt magie nouă, sunt implementări corecte și
documentate ale unor metode dovedite, utile pentru cine vrea să le
folosească fără să reinventeze roata.

1. Common-Input-Ownership Heuristic (CIOH):
   Dacă mai multe adrese apar ca inputuri în aceeași tranzacție, e foarte
   probabil să fie controlate de aceeași entitate (pentru a semna o
   tranzacție ai nevoie de cheile private ale tuturor inputurilor).

2. Change-Address Heuristic (euristică simplă, opțională):
   Dacă o tranzacție are exact un output "nou" (adresă apărută o singură
   dată în tot setul de date) și restul outputurilor sunt adrese deja
   cunoscute/reutilizate, output-ul nou e candidat la "adresă de rest"
   (change), aparținând aceluiași proprietar ca inputurile.

Aceste euristici NU sunt infailibile (CoinJoin, mixere și portofele
moderne le pot eluda intenționat) — orice rezultat trebuie tratat ca
indiciu, nu ca certitudine. Vezi docs/methodology.md pentru limitări.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Mapping, Any

from .graph import TransactionGraph


class UnionFind:
    """Structură simplă union-find pentru gruparea adreselor în clustere."""

    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def find(self, x: str) -> str:
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb

    def groups(self) -> dict[str, set[str]]:
        result: dict[str, set[str]] = defaultdict(set)
        for node in self.parent:
            result[self.find(node)].add(node)
        return dict(result)


def common_input_clustering(transactions: Iterable[Mapping[str, Any]]) -> dict[str, set[str]]:
    """Aplică CIOH pe o listă de tranzacții brute (nu graf) și întoarce clustere.

    Returnează un dict {cluster_id: {adrese}} — cluster_id e un reprezentant
    arbitrar din interiorul clusterului, nu un ID semantic.
    """
    uf = UnionFind()
    for tx in transactions:
        inputs = list(tx.get("inputs", []))
        if len(inputs) < 2:
            # tot înregistrăm adresa, ca să apară ca propriul ei cluster
            for addr in inputs:
                uf.find(addr)
            continue
        first = inputs[0]
        for other in inputs[1:]:
            uf.union(first, other)
    return uf.groups()


def change_address_candidates(
    transactions: Iterable[Mapping[str, Any]],
) -> dict[str, str]:
    """Identifică, pentru fiecare tranzacție eligibilă, candidatul la adresă
    de rest (change). Returnează {txid: adresa_candidata}.

    Eligibilitate: tranzacția are >=2 outputuri, dintre care exact unul
    e o adresă "nouă" (nu a mai apărut ca output în nicio altă tranzacție
    din set), iar restul outputurilor sunt adrese deja văzute.
    """
    transactions = list(transactions)
    output_seen_count: dict[str, int] = defaultdict(int)
    for tx in transactions:
        for addr in tx.get("outputs", []):
            output_seen_count[addr] += 1

    candidates: dict[str, str] = {}
    for tx in transactions:
        outputs = tx.get("outputs", [])
        if len(outputs) < 2:
            continue
        novel = [a for a in outputs if output_seen_count[a] == 1]
        if len(novel) == 1:
            candidates[tx["txid"]] = novel[0]
    return candidates


def cluster_summary(graph: TransactionGraph, clusters: Mapping[str, set[str]]) -> list[dict[str, Any]]:
    """Generează un rezumat per cluster: număr adrese, volum total in/out."""
    summary = []
    for cluster_id, addresses in clusters.items():
        total_in = sum(graph.total_in(a) for a in addresses)
        total_out = sum(graph.total_out(a) for a in addresses)
        summary.append(
            {
                "cluster_id": cluster_id,
                "size": len(addresses),
                "addresses": sorted(addresses),
                "total_in": round(total_in, 8),
                "total_out": round(total_out, 8),
            }
        )
    summary.sort(key=lambda c: c["size"], reverse=True)
    return summary
