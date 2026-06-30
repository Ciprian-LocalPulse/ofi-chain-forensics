"""
risk_scoring.py
----------------
Motor de scoring de risc PE BAZĂ DE REGULI, explicabile și auditabile.

Nu folosim un model "black box" — fiecare punct de scor are o explicație
atașată. Asta e o decizie deliberată: într-un domeniu cu impact legal real
(AML/fraud), un scor neexplicabil e inutil și potențial periculos. Dacă
vrei scoring bazat pe ML antrenat pe date proprii, acest modul oferă
`RiskFactor` ca interfață pe care o poți extinde cu propriile semnale.

Scorul final e normalizat 0-100. Pragurile sugerate (configurabile):
  0-29   : risc scăzut
  30-59  : risc moderat — recomandat review manual
  60-100 : risc ridicat — recomandat investigație prioritară

ATENȚIE: acest scor NU constituie probă legală de activitate ilicită.
E un instrument de prioritizare pentru analiști, nu un verdict.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .graph import TransactionGraph
from .patterns import PatternMatch, run_all_detectors

# greutăți implicite per tip de tipar — pot fi suprascrise de utilizator
DEFAULT_WEIGHTS: dict[str, float] = {
    "fan_out": 15.0,
    "fan_in": 15.0,
    "rapid_passthrough": 25.0,
    "peeling_chain": 30.0,
    "known_blacklist": 100.0,  # vezi blacklist_match() mai jos
    "mixer_proximity": 20.0,
}


@dataclass
class RiskFactor:
    name: str
    contribution: float
    explanation: str


@dataclass
class RiskScore:
    address: str
    score: float
    risk_level: str
    factors: list[RiskFactor] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "address": self.address,
            "score": self.score,
            "risk_level": self.risk_level,
            "factors": [
                {"name": f.name, "contribution": f.contribution, "explanation": f.explanation}
                for f in self.factors
            ],
        }


def _risk_level(score: float) -> str:
    if score >= 60:
        return "ridicat"
    if score >= 30:
        return "moderat"
    return "scazut"


def blacklist_match(address: str, blacklist: set[str]) -> bool:
    return address in blacklist


def score_addresses(
    graph: TransactionGraph,
    blacklist: set[str] | None = None,
    weights: dict[str, float] | None = None,
    detector_kwargs: dict[str, Any] | None = None,
) -> dict[str, RiskScore]:
    """Calculează un RiskScore per adresă din graf.

    blacklist: set de adrese cunoscute ca asociate cu fraudă/sancțiuni
               (ex. importate din OFI sau din liste publice OFAC/DNSC).
    """
    weights = weights or DEFAULT_WEIGHTS
    blacklist = blacklist or set()
    detector_kwargs = detector_kwargs or {}

    matches: list[PatternMatch] = run_all_detectors(graph, **detector_kwargs)
    matches_by_address: dict[str, list[PatternMatch]] = {}
    for m in matches:
        matches_by_address.setdefault(m.address, []).append(m)

    scores: dict[str, RiskScore] = {}

    for address in graph.graph.nodes:
        factors: list[RiskFactor] = []
        raw_total = 0.0

        for m in matches_by_address.get(address, []):
            weight = weights.get(m.pattern, 10.0)
            contribution = round(weight * m.score, 2)
            raw_total += contribution
            factors.append(
                RiskFactor(
                    name=m.pattern,
                    contribution=contribution,
                    explanation=_explain_pattern(m),
                )
            )

        if blacklist_match(address, blacklist):
            contribution = weights.get("known_blacklist", 100.0)
            raw_total += contribution
            factors.append(
                RiskFactor(
                    name="known_blacklist",
                    contribution=contribution,
                    explanation="Adresa apare pe o listă de adrese cunoscute ca asociate cu fraudă/sancțiuni.",
                )
            )

        # adresele direct conectate (1 hop) cu o adresă din blacklist primesc
        # un semnal de "proximitate" — fonduri care au tranzitat aproape de
        # o sursă cunoscută ca riscantă
        if blacklist and not blacklist_match(address, blacklist):
            neighbors = graph.address_neighbors(address, "both")
            if neighbors & blacklist:
                contribution = weights.get("mixer_proximity", 20.0)
                raw_total += contribution
                factors.append(
                    RiskFactor(
                        name="mixer_proximity",
                        contribution=contribution,
                        explanation="Adresa a interacționat direct (1 hop) cu o adresă din blacklist.",
                    )
                )

        score = round(min(100.0, raw_total), 2)
        scores[address] = RiskScore(
            address=address,
            score=score,
            risk_level=_risk_level(score),
            factors=factors,
        )

    return scores


def _explain_pattern(match: PatternMatch) -> str:
    explanations = {
        "fan_out": f"Adresa a trimis fonduri către {match.details.get('distinct_recipients')} adrese distincte — posibilă distribuire/smurfing.",
        "fan_in": f"Adresa a primit fonduri de la {match.details.get('distinct_senders')} adrese distincte — posibilă agregare pre-cash-out.",
        "rapid_passthrough": f"Adresa a retransmis {round((1 - match.details.get('retained_ratio', 0)) * 100, 1)}% din fonduri în {match.details.get('seconds_between')}s — posibil layering automatizat.",
        "peeling_chain": f"Adresa e punctul de start al unui lanț de {match.details.get('chain_length')} pași cu exfoliere graduală — tipar clasic de obfuscare a fondurilor.",
    }
    return explanations.get(match.pattern, f"Tipar detectat: {match.pattern}")


def top_risk_addresses(scores: dict[str, RiskScore], n: int = 20) -> list[RiskScore]:
    return sorted(scores.values(), key=lambda s: s.score, reverse=True)[:n]
