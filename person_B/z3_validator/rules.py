# person_b/z3_validator/rules.py
import re
from z3 import Solver, Bool, Implies, Not, sat, unsat

# Regex patterns to detect claims in hypothesis
PATTERNS = {
    "plaque_decrease": re.compile(r"(plaque|amyloid).*(decrease|reduce|reduction|clear)", re.I),
    "cognition_improvement": re.compile(r"(cognit|memory|behavior).*(improv|restore|better|recover)", re.I),
    "microglia_dysfunction": re.compile(r"microglia.*(dysfunction|exhaust|impair|reduc)", re.I),
    "chronic_inflammation": re.compile(r"(chronic)?.*inflamm", re.I),
    "reduced_phagocytosis": re.compile(r"(phagocytosis|phagocytic).*(reduc|impair)", re.I),
    "cure_claim": re.compile(r"\b(cure|completely treat|completely cure)\b", re.I),
    "apoe_e4": re.compile(r"APOE[- ]?e4", re.I),
}

def parse_hypothesis_to_preds(hypothesis_text):
    """Return a dict mapping predicate names -> True/False if mentioned."""
    preds = {}
    for k, pat in PATTERNS.items():
        preds[k] = bool(pat.search(hypothesis_text))
    return preds

def z3_validate(hypothesis_text):
    """
    Validate hypothesis with a small Z3 knowledge base.
    Returns dict: {valid: bool, reason: str, proof_trace: [str], warnings: [str]}
    """

    preds = parse_hypothesis_to_preds(hypothesis_text)
    proof_trace = []
    warnings = []

    # Define boolean symbols
    plaque_decrease = Bool("plaque_decrease")
    cognition_improvement = Bool("cognition_improvement")
    microglia_dysfunction = Bool("microglia_dysfunction")
    chronic_inflammation = Bool("chronic_inflammation")
    reduced_phagocytosis = Bool("reduced_phagocytosis")
    cure_claim = Bool("cure_claim")
    apoe_e4 = Bool("apoe_e4")

    # Knowledge base (hardcoded rules for MVP)
    # R1: plaque_decrease does NOT guarantee cognition_improvement
    # Represent as: Not(Implies(plaque_decrease, cognition_improvement))
    kb_R2 = Not(Implies(plaque_decrease, cognition_improvement))

    # R2: chronic_inflammation -> microglia_dysfunction
    kb_R3 = Implies(chronic_inflammation, microglia_dysfunction)

    # R3: microglia_dysfunction -> reduced_phagocytosis
    kb_R4 = Implies(microglia_dysfunction, reduced_phagocytosis)

    # R4: no current complete cure
    kb_R5 = Not(cure_claim)

    # Build solver with KB
    s = Solver()
    s.add(kb_R2)
    s.add(kb_R3)
    s.add(kb_R4)
    s.add(kb_R5)
    proof_trace.append("Loaded KB rules: R2 (plaque_decrease ↛ cognition_improvement), R3 (chronic_inflammation -> microglia_dysfunction), R4 (microglia_dysfunction -> reduced_phagocytosis), R5 (no complete cure)")

    # Translate hypothesis mentions into Z3 assertions
    # For MVP, we interpret mention of predicate as assertion that it's true.
    # Additionally, detect simple implication statements like "If X then Y" heuristically.
    # Heuristic for implication in hypothesis text:
    hyp_lower = hypothesis_text.lower()
    assertions = []
    # Direct assertions
    if preds["plaque_decrease"]:
        assertions.append((plaque_decrease, "Hypothesis asserts plaque_decrease"))
    if preds["cognition_improvement"]:
        assertions.append((cognition_improvement, "Hypothesis asserts cognition_improvement"))
    if preds["microglia_dysfunction"]:
        assertions.append((microglia_dysfunction, "Hypothesis asserts microglia_dysfunction"))
    if preds["chronic_inflammation"]:
        assertions.append((chronic_inflammation, "Hypothesis asserts chronic_inflammation"))
    if preds["reduced_phagocytosis"]:
        assertions.append((reduced_phagocytosis, "Hypothesis asserts reduced_phagocytosis"))
    if preds["cure_claim"]:
        assertions.append((cure_claim, "Hypothesis asserts cure_claim"))
    if preds["apoe_e4"]:
        assertions.append((apoe_e4, "Hypothesis mentions APOE-e4"))

    # Heuristic implication detection: look for "if" and "then" or "->"
    implied = []
    if "if" in hyp_lower and "then" in hyp_lower:
        # try to map simple patterns: "If plaques decrease, then cognition improves"
        # naive approach: check for presence of plaque and cognition keywords
        if preds["plaque_decrease"] and preds["cognition_improvement"]:
            # hypothesis asserts Implies(plaque_decrease, cognition_improvement)
            implied.append((Implies(plaque_decrease, cognition_improvement), "Hypothesis implies: plaque_decrease -> cognition_improvement"))
    elif "->" in hyp_lower or "=>" in hyp_lower:
        if preds["plaque_decrease"] and preds["cognition_improvement"]:
            implied.append((Implies(plaque_decrease, cognition_improvement), "Hypothesis implies: plaque_decrease -> cognition_improvement"))

    # Add hypothesis assertions to solver temporarily and check for contradictions
    # Create a fresh solver copying KB
    s2 = Solver()
    s2.add(kb_R2, kb_R3, kb_R4, kb_R5)

    # Add direct assertions
    for (sym, desc) in assertions:
        s2.add(sym)
        proof_trace.append(desc)

    # Add implications
    for (impl_expr, desc) in implied:
        s2.add(impl_expr)
        proof_trace.append(desc)

    # Check satisfiability
    sat_res = s2.check()
    if sat_res == sat:
        valid = True
        reason = "No contradiction with knowledge base."
    else:
        valid = False
        reason = "Hypothesis contradicts the hardcoded Alzheimer rules."

        # Try to identify which rule is contradicted by testing removing one rule at a time
        contradictions = []
        # Check each rule removal to see which rule causes UNSAT when combined with hypothesis
        rules = [("R2", kb_R2), ("R3", kb_R3), ("R4", kb_R4), ("R5", kb_R5)]
        for rid, rule_expr in rules:
            s_temp = Solver()
            # add all rules except the one under test
            for r2id, r2expr in rules:
                if r2id != rid:
                    s_temp.add(r2expr)
            # add hypothesis assertions/implications
            for (sym, _) in assertions:
                s_temp.add(sym)
            for (impl_expr, _) in implied:
                s_temp.add(impl_expr)
            if s_temp.check() == sat:
                contradictions.append(f"Contradiction arises due to rule {rid}")
        if contradictions:
            proof_trace.extend(contradictions)

    # Warnings for weak evidence or risky claims
    if preds["cure_claim"]:
        warnings.append("Hypothesis contains a 'cure' claim which is not supported by current evidence.")
    if preds["apoe_e4"]:
        warnings.append("APOE-e4 mentioned: consider genetic stratification in experiments.")

    result = {
        "valid": valid,
        "reason": reason,
        "proof_trace": proof_trace,
        "warnings": warnings
    }
    return result