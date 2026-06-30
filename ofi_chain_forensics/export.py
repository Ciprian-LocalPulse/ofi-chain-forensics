"""
export.py
---------
Exportă rezultatele de risk scoring în formate utile pentru analiști și
pentru integrare cu alte unelte din ecosistemul OFI (Open Fraud
Intelligence) — în particular formatul JSON e compatibil ca structură cu
intrările din dataset-ul OFI, ca să poată fi combinate ușor.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .risk_scoring import RiskScore


def export_csv(scores: dict[str, RiskScore], path: str | Path) -> None:
    path = Path(path)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["address", "score", "risk_level", "top_factor", "num_factors"])
        for s in sorted(scores.values(), key=lambda x: x.score, reverse=True):
            top_factor = max(s.factors, key=lambda f: f.contribution).name if s.factors else ""
            writer.writerow([s.address, s.score, s.risk_level, top_factor, len(s.factors)])


def export_json(scores: dict[str, RiskScore], path: str | Path) -> None:
    path = Path(path)
    data = [s.to_dict() for s in sorted(scores.values(), key=lambda x: x.score, reverse=True)]
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def export_ofi_compatible(
    scores: dict[str, RiskScore],
    path: str | Path,
    source_name: str = "ofi-chain-forensics",
    min_score: float = 30.0,
) -> None:
    """Exportă doar adresele cu risc >= min_score, într-un format de
    intrare compatibil cu structura dataset-ului OFI (vezi ofi_sdk),
    pentru a putea fi importate direct ca alerte.
    """
    path = Path(path)
    entries: list[dict[str, Any]] = []
    for s in sorted(scores.values(), key=lambda x: x.score, reverse=True):
        if s.score < min_score:
            continue
        entries.append(
            {
                "indicator_type": "crypto_address",
                "indicator_value": s.address,
                "risk_score": s.score,
                "risk_level": s.risk_level,
                "source": source_name,
                "tags": [f.name for f in s.factors],
                "description": "; ".join(f.explanation for f in s.factors) or "Niciun tipar specific detectat.",
            }
        )
    path.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
