"""
Exemplu de utilizare a ofi-chain-forensics ca bibliotecă Python
(nu prin CLI). Rulează: python examples/basic_usage.py
"""

import json
from pathlib import Path

from ofi_chain_forensics import (
    TransactionGraph,
    score_addresses,
    top_risk_addresses,
    common_input_clustering,
    cluster_summary,
    run_all_detectors,
    export_ofi_compatible,
)

DATA_PATH = Path(__file__).parent.parent / "data" / "sample" / "sample_transactions.json"
BLACKLIST_PATH = Path(__file__).parent.parent / "data" / "sample" / "sample_blacklist.txt"


def main() -> None:
    transactions = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    blacklist = {line.strip() for line in BLACKLIST_PATH.read_text(encoding="utf-8").splitlines() if line.strip()}

    graph = TransactionGraph.from_transactions(transactions)
    print(f"Graf: {graph.num_addresses} adrese, {graph.num_transactions} tranzacții\n")

    # 1. Detectoare brute de tipare
    matches = run_all_detectors(graph)
    print(f"Tipare detectate: {len(matches)}")
    for m in matches[:5]:
        print(f"  - {m.pattern} @ {m.address} (scor: {m.score})")

    # 2. Scoring de risc complet, cu blacklist
    scores = score_addresses(graph, blacklist=blacklist)
    print("\nTop 5 adrese cu risc:")
    for s in top_risk_addresses(scores, n=5):
        print(f"  {s.address}: {s.score} ({s.risk_level})")
        for f in s.factors:
            print(f"      -> {f.name}: +{f.contribution} | {f.explanation}")

    # 3. Clustering de adrese (common-input-ownership)
    clusters = common_input_clustering(transactions)
    summary = cluster_summary(graph, clusters)
    print(f"\nClustere identificate: {len(summary)} (afișez primele 3 după mărime)")
    for c in summary[:3]:
        print(f"  cluster cu {c['size']} adrese: {c['addresses']}")

    # 4. Export compatibil OFI, gata de import în alte unelte din ecosistem
    out_path = Path("/tmp/example_ofi_export.json")
    export_ofi_compatible(scores, out_path, min_score=20.0)
    print(f"\nExport compatibil OFI salvat în: {out_path}")


if __name__ == "__main__":
    main()
