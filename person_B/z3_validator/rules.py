import re
from z3 import Solver, Bool, Implies, Not, sat, unsat

PATTERNS = {
    "plaque_decrease": re.compile(r"(plaque|amyloid).*(decrease|reduce|reduction|clear)", re.I),
    "cognition_improvement": re.compile(r"(cognit|memory|behavior).*(improv|restore|better|recover)", re.I),
    "microglia_dysfunction": re.compile(r"microglia.*(dysfunction|exhaust|impair|reduc)", re.I),
    "chronic_inflammation": re.compile(r"(chronic)?.*inflamm", re.I),
    "reduced_phagocytosis": re.compile(r"(phagocytosis|phagocytic).*(reduc|impair)", re.I),
    "cure_claim": re.compile(r"\b(cure|completely treat|completely cure)\b", re.I),
    "apoe_e4": re.compile(r"APOE[- ]?e4", re.I),
    "impaired_amyloid_beta_clearance": re.compile(r"(amyloid[- ]?beta|amyloid).*(clearance|clear).*(impair|reduc)", re.I),
    "blood_brain_barrier_disruption": re.compile(r"blood[- ]?brain[- ]?barrier.*(disrupt|impair)", re.I),
    "amyloid_beta_aggregation": re.compile(r"(amyloid[- ]?beta|amyloid).*(aggregat|accumulat)", re.I),
    "tau_phosphorylation": re.compile(r"tau.*(phosphorylat|hyperphosphorylat)", re.I),
    "neuronal_damage": re.compile(r"(neuron|neuronal).*(damage|loss|degenerat)", re.I),  # New
    "disease_progression": re.compile(r"(disease|alzheimer).*(progress|worsen|advance)", re.I)  # New
}

def parse_hypothesis_to_preds(hypothesis_text):
    """Return a dict mapping predicate names -> True/False if mentioned."""
    preds = {}
    for k, pat in PATTERNS.items():
        preds[k] = bool(pat.search(hypothesis_text))
    return preds

def z3_validate(hypothesis_text, dynamic_rules=None, classification=None, further_data=None):
    dynamic_rules = dynamic_rules or []
    classification = classification or ""
    further_data = further_data or ""

    preds = parse_hypothesis_to_preds(hypothesis_text)
    proof_trace = []
    warnings = []

    plaque_decrease = Bool("plaque_decrease")
    cognition_improvement = Bool("cognition_improvement")
    microglia_dysfunction = Bool("microglia_dysfunction")
    chronic_inflammation = Bool("chronic_inflammation")
    reduced_phagocytosis = Bool("reduced_phagocytosis")
    cure_claim = Bool("cure_claim")
    apoe_e4 = Bool("apoe_e4")
    impaired_amyloid_beta_clearance = Bool("impaired_amyloid_beta_clearance")
    blood_brain_barrier_disruption = Bool("blood_brain_barrier_disruption")
    amyloid_beta_aggregation = Bool("amyloid_beta_aggregation")
    tau_phosphorylation = Bool("tau_phosphorylation")
    neuronal_damage = Bool("neuronal_damage")
    disease_progression = Bool("disease_progression")

    kb_R2 = Not(Implies(plaque_decrease, cognition_improvement))
    kb_R3 = Implies(chronic_inflammation, microglia_dysfunction)
    kb_R4 = Implies(microglia_dysfunction, reduced_phagocytosis)
    kb_R5 = Not(cure_claim)
    kb_R6 = Implies(microglia_dysfunction, impaired_amyloid_beta_clearance)
    kb_R7 = Implies(chronic_inflammation, blood_brain_barrier_disruption)
    kb_R8 = Implies(blood_brain_barrier_disruption, microglia_dysfunction)
    kb_R9 = Implies(microglia_dysfunction, amyloid_beta_aggregation)
    kb_R10 = Implies(amyloid_beta_aggregation, tau_phosphorylation)
    kb_R11 = Implies(microglia_dysfunction, neuronal_damage)
    kb_R12 = Implies(neuronal_damage, disease_progression)

    s = Solver()
    s.add(kb_R2, kb_R3, kb_R4, kb_R5, kb_R6, kb_R7, kb_R8, kb_R9, kb_R10, kb_R11, kb_R12)
    proof_trace.append("Loaded KB rules: R2 (plaque_decrease ↛ cognition_improvement), R3 (chronic_inflammation -> microglia_dysfunction), R4 (microglia_dysfunction -> reduced_phagocytosis), R5 (no complete cure), R6 (microglia_dysfunction -> impaired_amyloid_beta_clearance), R7 (chronic_inflammation -> blood_brain_barrier_disruption), R8 (blood_brain_barrier_disruption -> microglia_dysfunction), R9 (microglia_dysfunction -> amyloid_beta_aggregation), R10 (amyloid_beta_aggregation -> tau_phosphorylation), R11 (microglia_dysfunction -> neuronal_damage), R12 (neuronal_damage -> disease_progression)")

    symbol_map = {
        "plaque_decrease": plaque_decrease,
        "cognition_improvement": cognition_improvement,
        "microglia_dysfunction": microglia_dysfunction,
        "chronic_inflammation": chronic_inflammation,
        "reduced_phagocytosis": reduced_phagocytosis,
        "cure_claim": cure_claim,
        "apoe_e4": apoe_e4,
        "impaired_amyloid_beta_clearance": impaired_amyloid_beta_clearance,
        "blood_brain_barrier_disruption": blood_brain_barrier_disruption,
        "amyloid_beta_aggregation": amyloid_beta_aggregation,
        "tau_phosphorylation": tau_phosphorylation,
        "neuronal_damage": neuronal_damage,
        "disease_progression": disease_progression
    }
    for rule in dynamic_rules:
        if "Implies(" in rule:
            try:
                match = re.match(r"Implies\(([^,]+),\s*([^)]+)\)", rule)
                if match:
                    pred1, pred2 = match.groups()
                    pred1 = pred1.strip()
                    pred2 = pred2.strip()
                    if pred1 in symbol_map and pred2 in symbol_map:
                        s.add(Implies(symbol_map[pred1], symbol_map[pred2]))
                        proof_trace.append(f"Added dynamic rule: {rule}")
                    else:
                        warnings.append(f"Unknown predicates in dynamic rule: {rule}")
                else:
                    warnings.append(f"Failed to parse dynamic rule: {rule}")
            except Exception as e:
                warnings.append(f"Error parsing dynamic rule '{rule}': {str(e)}")
        elif "If" in rule and ", then" in rule:
            try:
                match = re.match(r"If\s+([^,]+),\s*then\s+([^,\.]+)", rule)
                if match:
                    pred1, pred2 = match.groups()
                    pred1 = pred1.strip()
                    pred2 = pred2.strip()
                    if pred1 in symbol_map and pred2 in symbol_map:
                        s.add(Implies(symbol_map[pred1], symbol_map[pred2]))
                        proof_trace.append(f"Added dynamic rule: Implies({pred1}, {pred2})")
                    else:
                        warnings.append(f"Unknown predicates in dynamic rule: If {pred1}, then {pred2}")
                else:
                    warnings.append(f"Failed to parse dynamic rule: {rule}")
            except Exception as e:
                warnings.append(f"Error parsing dynamic rule '{rule}': {str(e)}")
        else:
            warnings.append(f"Dynamic rule not in recognized format: {rule}")

    assertions = []
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
    if preds["impaired_amyloid_beta_clearance"]:
        assertions.append((impaired_amyloid_beta_clearance, "Hypothesis asserts impaired_amyloid_beta_clearance"))
    if preds["blood_brain_barrier_disruption"]:
        assertions.append((blood_brain_barrier_disruption, "Hypothesis asserts blood_brain_barrier_disruption"))
    if preds["amyloid_beta_aggregation"]:
        assertions.append((amyloid_beta_aggregation, "Hypothesis asserts amyloid_beta_aggregation"))
    if preds["tau_phosphorylation"]:
        assertions.append((tau_phosphorylation, "Hypothesis asserts tau_phosphorylation"))
    if preds["neuronal_damage"]:
        assertions.append((neuronal_damage, "Hypothesis asserts neuronal_damage"))  # New
    if preds["disease_progression"]:
        assertions.append((disease_progression, "Hypothesis asserts disease_progression"))  # New

    implied = []
    hyp_lower = hypothesis_text.lower()
    if "if" in hyp_lower and "then" in hyp_lower or "->" in hyp_lower or "=>" in hyp_lower:
        if preds["plaque_decrease"] and preds["cognition_improvement"]:
            implied.append((Implies(plaque_decrease, cognition_improvement), "Hypothesis implies: plaque_decrease -> cognition_improvement"))

    s2 = Solver()
    s2.add(kb_R2, kb_R3, kb_R4, kb_R5, kb_R6, kb_R7, kb_R8, kb_R9, kb_R10, kb_R11, kb_R12)
    for (sym, desc) in assertions:
        s2.add(sym)
        proof_trace.append(desc)
    for (impl_expr, desc) in implied:
        s2.add(impl_expr)
        proof_trace.append(desc)

    sat_res = s2.check()
    if sat_res == sat:
        valid = True
        reason = "No contradiction with knowledge base and dynamic rules."
    else:
        valid = False
        reason = "Hypothesis contradicts the knowledge base or dynamic rules."
        contradictions = []
        rules = [("R2", kb_R2), ("R3", kb_R3), ("R4", kb_R4), ("R5", kb_R5), ("R6", kb_R6),
                 ("R7", kb_R7), ("R8", kb_R8), ("R9", kb_R9), ("R10", kb_R10),
                 ("R11", kb_R11), ("R12", kb_R12)]
        for rid, rule_expr in rules:
            s_temp = Solver()
            for r2id, r2expr in rules:
                if r2id != rid:
                    s_temp.add(r2expr)
            for (sym, _) in assertions:
                s_temp.add(sym)
            for (impl_expr, _) in implied:
                s_temp.add(impl_expr)
            if s_temp.check() == sat:
                contradictions.append(f"Contradiction arises due to rule {rid}")
        if contradictions:
            proof_trace.extend(contradictions)

    if classification == "unsupported":
        warnings.append("Hypothesis classified as unsupported by rule-based analysis.")
    if further_data:
        warnings.append(f"Further insights from hypothesis generation: {further_data}")

    result = {
        "valid": valid,
        "reason": reason,
        "proof_trace": proof_trace,
        "warnings": warnings
    }
    return result