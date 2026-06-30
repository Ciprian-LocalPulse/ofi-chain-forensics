"""
cli.py
------
Interfață de linie de comandă pentru ofi-chain-forensics.

Utilizare:
    python -m ofi_chain_forensics.cli analyze data/sample/sample_transactions.json \
        --blacklist data/sample/sample_blacklist.txt \
        --out-csv results.csv --out-json results.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .graph import TransactionGraph
from .risk_scoring import score_addresses, top_risk_addresses
from .export import export_csv, export_json, export_ofi_compatible
from .clustering import common_input_clustering, cluster_summary


def _load_transactions(path: str) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Fișierul de tranzacții trebuie să conțină o listă JSON.")
    return data


def _load_blacklist(path: str | None) -> set[str]:
    if not path:
        return set()
    return {line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ofi-chain-forensics",
        description="Analiză de fraudă/AML pe grafuri de tranzacții blockchain.",
    )
    parser.add_argument("transactions", help="Fișier JSON cu lista de tranzacții normalizate.")
    parser.add_argument("--blacklist", help="Fișier .txt cu o adresă pe linie, listă neagră cunoscută.")
    parser.add_argument("--out-csv", help="Cale fișier CSV pentru rezultate.")
    parser.add_argument("--out-json", help="Cale fișier JSON pentru rezultate complete.")
    parser.add_argument("--out-ofi", help="Cale fișier JSON compatibil cu formatul OFI (doar risc >= prag).")
    parser.add_argument("--min-score", type=float, default=30.0, help="Prag minim de scor pentru --out-ofi (implicit 30).")
    parser.add_argument("--top", type=int, default=15, help="Câte adrese cu risc maxim să afișeze în consolă.")
    parser.add_argument("--show-clusters", action="store_true", help="Afișează și rezumatul clusterelor CIOH.")

    args = parser.parse_args(argv)

    transactions = _load_transactions(args.transactions)
    blacklist = _load_blacklist(args.blacklist)

    graph = TransactionGraph.from_transactions(transactions)
    print(f"Graf construit: {graph.num_addresses} adrese, {graph.num_transactions} tranzacții.\n")

    scores = score_addresses(graph, blacklist=blacklist)
    top = top_risk_addresses(scores, n=args.top)

    print(f"Top {len(top)} adrese după scor de risc:")
    print(f"{'Adresa':<45}{'Scor':>8}  Nivel")
    print("-" * 70)
    for s in top:
        print(f"{s.address:<45}{s.score:>8.2f}  {s.risk_level}")

    if args.show_clusters:
        clusters = common_input_clustering(transactions)
        summary = cluster_summary(graph, clusters)
        print("\nTop clustere (common-input-ownership heuristic):")
        for c in summary[:10]:
            print(f"  cluster ({c['size']} adrese) — in: {c['total_in']:.4f}, out: {c['total_out']:.4f}")

    if args.out_csv:
        export_csv(scores, args.out_csv)
        print(f"\nCSV salvat: {args.out_csv}")
    if args.out_json:
        export_json(scores, args.out_json)
        print(f"JSON salvat: {args.out_json}")
    if args.out_ofi:
        export_ofi_compatible(scores, args.out_ofi, min_score=args.min_score)
        print(f"Export compatibil OFI salvat: {args.out_ofi} (prag >= {args.min_score})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
