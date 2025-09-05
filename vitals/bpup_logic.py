from common.rule_engine import evaluate_rules

# BPUP（SBP上昇時）に関連する複数薬剤介入（CONT, HANP, VASO）含む

def evaluate_bpup(vitals, tree_df, thresholds=None, phase='a'):
    """Evaluate BPUP-related rules from the tree data.

    Parameters
    ----------
    vitals : dict
        Latest vital values.
    tree_df : DataFrame-like
        Rules loaded via ``load_tree``.
    thresholds : dict, optional
        Threshold values used inside conditions.
    phase : str, default 'a'
        'a' for acute phase or 'r' for reevaluation.
    """
    prefixes = ["BPUP", "CONT", "HANP", "VASO"]
    instructions = evaluate_rules(vitals, tree_df, prefixes, thresholds, phase)

    for inst in instructions:
        if inst.get("id") != "BPUP_A":
            continue
        na = vitals.get("noradrenaline") or 0
        pit = vitals.get("pitressin") or 0
        hanp = vitals.get("hanp") or 0
        cont = vitals.get("contomin") or 0

        msg = inst.get("instruction", "")
        if na > 0:
            msg = "ノルアドレナリンを減量してもよいです"
        elif pit >= 0.03:
            msg = "ピトレシンを減量してもよいです"
        elif 0 <= pit <= 0.02:
            if 0 <= hanp < 0.2:
                msg = "ハンプを増量してもよいです"
            elif 0.2 <= hanp <= 0.3:
                if cont == 0:
                    msg = "コントミンを0.1で開始してもよいです"
                elif 0.11 <= cont <= 0.3:
                    msg = "昇圧と降圧薬調整での降圧は難しい可能性があります"
        inst["instruction"] = msg

    return instructions
