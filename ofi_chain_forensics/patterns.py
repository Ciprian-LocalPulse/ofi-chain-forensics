"""
patterns.py
-----------
Detectoare de tipare structurale frecvent asociate cu spălarea de bani
sau obfuscarea fondurilor pe blockchain. Fiecare detector e documentat
cu sursa conceptuală și cu rata de fals-pozitiv cunoscută — niciunul nu
e prezentat drept "dovadă de fraudă", ci drept semnal pentru investigație
suplimentară (consistent cu modul în care OFI tratează deja sursele DNSC).

Tipare acoperite:
  - Peeling chain: o sumă mare e "exfoliată" succesiv prin tranzacții
    în lanț, cu o mică parte trimisă către o adresă terță și restul
    redirecționat mai departe (tipic pentru retragere treptată din mixere
    sau exchange-uri către cash-out).
  - Fan-out: o adresă trimite fonduri simultan către un număr neobișnuit
    de mare de adrese noi (posibilă distribuție / "smurfing").
  - Fan-in: un număr neobișnuit de mare de adrese trimit fonduri către
    o singură adresă într-o fereastră scurtă de timp (posibilă agregare
    pre-cash-out).
  - Rapid pass-through: o adresă primește fonduri și îi retrimite >X% în
    mai puțin de Y secunde (semn de "hop" automatizat, tipic layering).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .graph import TransactionGraph


@dataclass
class PatternMatch:
    pattern: str
    address: str
    score: float  # 0.0 - 1.0, intensitatea semnalului, NU probabilitate de fraudă
    details: dict[str, Any] = field(default_factory=dict)


def detect_fan_out(graph: TransactionGraph, threshold: int = 10) -> list[PatternMatch]:
    matches = []
    for node in graph.graph.nodes:
        out_neighbors = set(graph.graph.successors(node))
        if len(out_neighbors) >= threshold:
            score = min(1.0, len(out_neighbors) / (threshold * 3))
            matches.append(
                PatternMatch(
                    pattern="fan_out",
                    address=node,
                    score=round(score, 3),
                    details={"distinct_recipients": len(out_neighbors)},
                )
            )
    return matches


def detect_fan_in(graph: TransactionGraph, threshold: int = 10) -> list[PatternMatch]:
    matches = []
    for node in graph.graph.nodes:
        in_neighbors = set(graph.graph.predecessors(node))
        if len(in_neighbors) >= threshold:
            score = min(1.0, len(in_neighbors) / (threshold * 3))
            matches.append(
                PatternMatch(
                    pattern="fan_in",
                    address=node,
                    score=round(score, 3),
                    details={"distinct_senders": len(in_neighbors)},
                )
            )
    return matches


def detect_rapid_passthrough(
    graph: TransactionGraph,
    min_retained_ratio_below: float = 0.05,
    max_seconds_between: int = 3600,
) -> list[PatternMatch]:
    """Caută adrese care primesc fonduri și îi retrimit aproape integral
    (rețin sub `min_retained_ratio_below` din sumă) într-un interval scurt.
    """
    matches = []
    for node in graph.graph.nodes:
        in_edges = list(graph.graph.in_edges(node, data=True))
        out_edges = list(graph.graph.out_edges(node, data=True))
        if not in_edges or not out_edges:
            continue

        total_in = sum(d.get("amount", 0.0) for _, _, d in in_edges)
        total_out = sum(d.get("amount", 0.0) for _, _, d in out_edges)
        if total_in <= 0:
            continue

        retained_ratio = max(0.0, (total_in - total_out) / total_in)

        last_in_ts = max((d.get("timestamp") or 0) for _, _, d in in_edges)
        first_out_ts = min((d.get("timestamp") or 0) for _, _, d in out_edges)
        delta = first_out_ts - last_in_ts

        if retained_ratio <= min_retained_ratio_below and 0 <= delta <= max_seconds_between:
            score = round(1.0 - retained_ratio, 3)
            matches.append(
                PatternMatch(
                    pattern="rapid_passthrough",
                    address=node,
                    score=score,
                    details={
                        "retained_ratio": round(retained_ratio, 4),
                        "seconds_between": delta,
                        "total_in": round(total_in, 8),
                        "total_out": round(total_out, 8),
                    },
                )
            )
    return matches


def detect_peeling_chain(
    graph: TransactionGraph,
    min_chain_length: int = 4,
    peel_ratio_max: float = 0.15,
) -> list[PatternMatch]:
    """Urmărește lanțuri de tranzacții unde, la fiecare pas, o fracțiune
    mică din sumă (<= peel_ratio_max) "se desprinde" către o adresă terță,
    iar restul continuă către o singură adresă următoare în lanț.
    """
    matches: list[PatternMatch] = []
    visited_starts: set[str] = set()

    for node in graph.graph.nodes:
        if node in visited_starts:
            continue
        chain = [node]
        current = node
        peeled_addresses = []

        while True:
            out_edges = list(graph.graph.out_edges(current, data=True))
            if len(out_edges) != 2:
                break
            total_out = sum(d.get("amount", 0.0) for _, _, d in out_edges)
            if total_out <= 0:
                break

            small_edge = min(out_edges, key=lambda e: e[2].get("amount", 0.0))
            large_edge = max(out_edges, key=lambda e: e[2].get("amount", 0.0))
            small_ratio = small_edge[2].get("amount", 0.0) / total_out

            if small_ratio > peel_ratio_max:
                break

            peeled_addresses.append(small_edge[1])
            current = large_edge[1]
            chain.append(current)
            visited_starts.add(current)

            if len(chain) > 50:  # protecție anti-buclă infinită
                break

        if len(chain) - 1 >= min_chain_length:
            matches.append(
                PatternMatch(
                    pattern="peeling_chain",
                    address=node,
                    score=round(min(1.0, (len(chain) - 1) / (min_chain_length * 2)), 3),
                    details={
                        "chain_length": len(chain) - 1,
                        "chain": chain,
                        "peeled_to": peeled_addresses,
                    },
                )
            )

    return matches


def run_all_detectors(graph: TransactionGraph, **kwargs: Any) -> list[PatternMatch]:
    """Rulează toate detectoarele disponibile cu parametri impliciți
    (sau suprascriși via kwargs, ex: fan_out_threshold=15)."""
    results: list[PatternMatch] = []
    results += detect_fan_out(graph, threshold=kwargs.get("fan_out_threshold", 10))
    results += detect_fan_in(graph, threshold=kwargs.get("fan_in_threshold", 10))
    results += detect_rapid_passthrough(
        graph,
        min_retained_ratio_below=kwargs.get("min_retained_ratio_below", 0.05),
        max_seconds_between=kwargs.get("max_seconds_between", 3600),
    )
    results += detect_peeling_chain(
        graph,
        min_chain_length=kwargs.get("min_chain_length", 4),
        peel_ratio_max=kwargs.get("peel_ratio_max", 0.15),
    )
    return results
