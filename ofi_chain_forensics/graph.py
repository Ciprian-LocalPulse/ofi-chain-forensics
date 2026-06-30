"""
graph.py
--------
Construiește un graf orientat de tranzacții blockchain (adrese = noduri,
tranzacții = muchii ponderate) pornind de la o listă de tranzacții normalizate.

Format minim așteptat per tranzacție (dict sau pandas.Series):
    {
        "txid": str,
        "timestamp": int (unix epoch, secunde),
        "inputs": list[str]   -> adresele care trimit fonduri (pot fi mai multe)
        "outputs": list[str]  -> adresele care primesc fonduri (pot fi mai multe)
        "amount": float       -> suma totală tranzacționată (în unitatea aleasă, ex. BTC/ETH/token)
        "fee": float          -> comision (opțional, default 0.0)
    }

Nu facem nicio presupunere despre rețeaua sursă (Bitcoin, Ethereum, etc.) —
SDK-ul lucrează pe date deja normalizate. Conectorii pentru extragerea
datelor brute dintr-un explorer/nod sunt responsabilitatea utilizatorului
sau a unui modul `connectors/` separat (vezi docs/data_sources.md).
"""

from __future__ import annotations

import networkx as nx
from typing import Iterable, Mapping, Any


class TransactionGraph:
    """Wrapper peste un networkx.MultiDiGraph specializat pentru analiză AML."""

    def __init__(self) -> None:
        self.graph = nx.MultiDiGraph()
        self._tx_count = 0

    @classmethod
    def from_transactions(cls, transactions: Iterable[Mapping[str, Any]]) -> "TransactionGraph":
        tg = cls()
        for tx in transactions:
            tg.add_transaction(tx)
        return tg

    def add_transaction(self, tx: Mapping[str, Any]) -> None:
        """Adaugă o tranzacție la graf.

        `outputs` poate fi în două formate:
          - listă de adrese (str): suma totală e distribuită egal pe fiecare
            pereche input->output (simplificare folosită când nu avem sume
            exacte per output).
          - listă de dict-uri {"address": str, "amount": float}: sumele
            exacte sunt folosite direct (recomandat — necesar pentru
            detectori sensibili la proporții, ex. peeling chain).
        """
        txid = tx["txid"]
        inputs = tx.get("inputs", [])
        outputs = tx.get("outputs", [])
        amount = float(tx.get("amount", 0.0))
        fee = float(tx.get("fee", 0.0))
        timestamp = tx.get("timestamp")

        if not inputs or not outputs:
            raise ValueError(f"Tranzacția {txid} trebuie să aibă cel puțin un input și un output.")

        explicit_outputs = isinstance(outputs[0], Mapping)

        if explicit_outputs:
            output_pairs = [(o["address"], float(o["amount"])) for o in outputs]
        else:
            n_pairs = len(outputs)
            per_output_amount = amount / n_pairs if n_pairs else 0.0
            output_pairs = [(addr, per_output_amount) for addr in outputs]

        n_inputs = len(inputs)
        for src in inputs:
            for dst, out_amount in output_pairs:
                self.graph.add_edge(
                    src,
                    dst,
                    key=f"{txid}:{dst}",
                    txid=txid,
                    amount=out_amount / n_inputs if n_inputs else out_amount,
                    fee=fee / (n_inputs * len(output_pairs)) if n_inputs and output_pairs else 0.0,
                    timestamp=timestamp,
                )

        self._tx_count += 1

    @property
    def num_transactions(self) -> int:
        return self._tx_count

    @property
    def num_addresses(self) -> int:
        return self.graph.number_of_nodes()

    def address_neighbors(self, address: str, direction: str = "both") -> set[str]:
        """Returnează adresele vecine direct (1 hop) ale unei adrese."""
        if direction not in {"in", "out", "both"}:
            raise ValueError("direction trebuie să fie 'in', 'out' sau 'both'")
        neighbors: set[str] = set()
        if direction in ("out", "both"):
            neighbors.update(self.graph.successors(address))
        if direction in ("in", "both"):
            neighbors.update(self.graph.predecessors(address))
        return neighbors

    def subgraph_within_hops(self, address: str, hops: int = 2) -> nx.MultiDiGraph:
        """Extrage sub-graful tuturor adreselor la maxim `hops` distanță de `address`."""
        nodes = {address}
        frontier = {address}
        for _ in range(hops):
            next_frontier: set[str] = set()
            for node in frontier:
                next_frontier.update(self.address_neighbors(node, "both"))
            next_frontier -= nodes
            nodes.update(next_frontier)
            frontier = next_frontier
        return self.graph.subgraph(nodes).copy()

    def total_in(self, address: str) -> float:
        return sum(d.get("amount", 0.0) for _, _, d in self.graph.in_edges(address, data=True))

    def total_out(self, address: str) -> float:
        return sum(d.get("amount", 0.0) for _, _, d in self.graph.out_edges(address, data=True))
