"""Compare step 27 with the sibling repository eq-laws-without-small-models (read only, must sit next to this one).

The sibling decides the rows of its four laws with infinite models by its own term models (different
definitions: one generator G, and f(t) = t or a product kept formal where ours keeps F(t)), in
results/refutations_term_models.json: "certificates" are refuted targets, "not_refuted" the others. This script
requires the same split as ours: every pair we refute is refuted there, every pair we derive is not refuted
there, and nothing is missing on either side. It only compares verdicts; it does not re-check the sibling.

Usage: python src/compare_nine_laws_sibling.py laws_json refutations_json derivations_json sibling_json
"""
import json
import sys


def main():
    laws_file, ref_file, der_file, sib_file = sys.argv[1:]
    texts = [e["text"] for e in json.load(open(laws_file))]
    ours_ref = {tuple(map(int, k.split(","))) for k in json.load(open(ref_file))}
    ours_der = {tuple(map(int, k.split(","))) for k in json.load(open(der_file))["pairs"]}
    sib = json.load(open(sib_file))
    law_of = {m: texts.index(x["law"]) for m, x in sib["models"].items()}
    problems = []

    def pairs(items, kind):
        out = set()
        for c in items:
            a, b = law_of[c["model"]], c["target_id"] - 1
            if texts[b] != c["target"]:
                problems.append(f"sibling {kind} entry: target id {c['target_id']} is not {c['target']!r} here")
            out.add((a, b))
        return out

    sib_ref, sib_not = pairs(sib["certificates"], "certificate"), pairs(sib["not_refuted"], "not_refuted")
    print(f"sibling: {len(sib_ref)} refuted, {len(sib_not)} not refuted, laws {sorted(a + 1 for a in law_of.values())}")
    print(f"here:    {len(ours_ref)} refuted, {len(ours_der)} derived")
    for name, x, y in (("refuted here, not there", ours_ref, sib_ref), ("refuted there, not here", sib_ref, ours_ref),
                       ("derived here, not 'not refuted' there", ours_der, sib_not),
                       ("'not refuted' there, not derived here", sib_not, ours_der)):
        diff = sorted(x - y)
        print(f"{name}: {len(diff)}")
        problems += [f"{name}: {p}" for p in diff[:5]]
    for p in problems[:20]:
        print("PROBLEM", p)
    print("SAME VERDICTS" if not problems else f"{len(problems)} PROBLEMS")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
