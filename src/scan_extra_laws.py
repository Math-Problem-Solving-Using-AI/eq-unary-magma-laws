"""Search for a refutation of A => B by completing A together with one extra law E (step 20).

If A and E together complete (as in step 18, with new symbols allowed) and B's two sides keep different normal
forms, the structure of normal forms satisfies A and E but not B, so A does not imply B. Every law E of size 1
to 4 (src/laws.py, 8,805 laws) is tried, with both precedences of step 18 and its limits (40 rules, term size
14, 3,000 equations). Only the outcome is stored; a completed run with B failing would be the lead for a
certificate, and none was found in step 20 (every completed run makes B hold).

Saves after every 20 laws and resumes from the output file. Stops after about 500 seconds; run again to go on.

Output: {"A": text, "B": [texts], "done": n, "laws": {id: [outcome per precedence tried]}}, where an outcome
is a stop reason (first 40 characters) or [precedence, [verdict per B], number of rules].

Usage: python src/scan_extra_laws.py laws_json a_id b_id[,b_id...] out_json
"""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import complete_new_symbols as cn  # noqa: E402
from complete_open import kbo_greater, size  # noqa: E402
from laws import enumerate_laws, show_law  # noqa: E402
from prove import tuplify  # noqa: E402


class ExtraLawCompletion(cn.NewSymbolCompletion):
    """Completion of A (fact 0) and E (fact 1, marked "axiom"); the loop is that of step 18."""

    def run_with(self, e):
        self.facts.append((e[0], e[1], "axiom"))
        self.next_var = max(self.next_var, 1 + max(cn.variables(e[0]) | cn.variables(e[1])))
        todo = [(self.facts[0][0], self.facts[0][1], [(0, 1, (), self.ident(0))]),
                (e[0], e[1], [(1, 1, (), self.ident(1))])]
        seen = 0
        while todo:
            seen += 1
            if seen > cn.MAX_EQUATIONS:
                return "equation limit"
            todo.sort(key=lambda q: size(q[0]) + size(q[1]))
            s, t, chain = todo.pop(0)
            s2, st = self.normalize(s)
            t2, tt = self.normalize(t)
            if s2 == t2:
                continue
            chain = [(f, -d, p, sb) for f, d, p, sb in reversed(st)] + chain + tt
            if max(size(s2), size(t2)) > cn.MAX_SIZE:
                return "term size limit"
            if kbo_greater(s2, t2, self.prec):
                rule = (s2, t2, 1)
            elif kbo_greater(t2, s2, self.prec):
                rule = (t2, s2, -1)
            else:
                rule = None
            self.facts.append((s2, t2, chain))
            fid = len(self.facts) - 1
            if rule is not None:
                self.add_rule(rule[0], rule[1], fid, rule[2], todo)
            else:
                new = self.new_symbol(s2, t2, fid)
                if isinstance(new, str):
                    return new
                for r in new:
                    self.add_rule(*r, todo)
            if len(self.rules) > cn.MAX_RULES:
                return "rule limit"
        return "complete"


def main():
    laws_file, a_id, b_ids, out = sys.argv[1:]
    entries = json.load(open(laws_file))
    by_text = {e["text"]: tuplify(e["law"]) for e in entries}
    a_text = entries[int(a_id) - 1]["text"]
    b_texts = [entries[int(b) - 1]["text"] for b in b_ids.split(",")]
    extra = [(show_law(law), law) for law in enumerate_laws(4)]
    res = json.load(open(out)) if os.path.exists(out) else {"A": a_text, "B": b_texts, "laws": {}}
    t0 = time.time()
    for k, (text, e) in enumerate(extra, start=1):
        if str(k) in res["laws"] or text == a_text:
            continue
        rec = []
        for prec in ({"f": 2, "m": 1}, {"f": 1, "m": 2}):
            c = ExtraLawCompletion(by_text[a_text], dict(prec))
            outcome = c.run_with(e)
            if outcome != "complete":
                rec.append(outcome[:40])
                continue
            verdicts = []
            for b in b_texts:
                left, _ = c.normalize(by_text[b][0])
                right, _ = c.normalize(by_text[b][1])
                verdicts.append("holds" if left == right else "fails")
            rec.append([cn.precedence_text(c.prec), verdicts, len(c.rules)])
            if "fails" in verdicts:
                print(f"LEAD: E = {text}: {verdicts}", flush=True)
            break
        res["laws"][str(k)] = rec
        if k % 20 == 0:
            json.dump(res, open(out, "w"), indent=0)
        if time.time() - t0 > 500:
            break
    res["done"] = len(res["laws"])
    json.dump(res, open(out, "w"), indent=0)
    completed = [v[-1] for v in res["laws"].values() if isinstance(v[-1], list)]
    fails = sum("fails" in v[1] for v in completed)
    print(f"extra laws tried: {res['done']} of {len(extra) - 1}; completed: {len(completed)}; "
          f"B fails in a completed run: {fails}")


if __name__ == "__main__":
    main()
