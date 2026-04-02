import json
import os

RANKS = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']

def get_all_169_hands():
    hands = []
    for r in RANKS:
        hands.append(f"{r}{r}")
    for i in range(len(RANKS)):
        for j in range(i + 1, len(RANKS)):
            hands.append(f"{RANKS[i]}{RANKS[j]}s")
            hands.append(f"{RANKS[i]}{RANKS[j]}o")
    return list(set(hands))

def parse_pokerstove(range_list):
    """Basic parser for formats like '88+', 'AJs+', 'KTo+'"""
    hands = set()
    for item in range_list:
        if item.endswith('+'):
            base = item[:-1]
            if len(base) == 2: # Pairs like '66'
                start_idx = RANKS.index(base[0])
                for i in range(start_idx, -1, -1):
                    hands.add(f"{RANKS[i]}{RANKS[i]}")
            else: # Suited/Offsuit like 'A3s', 'KJo'
                r1_chr = base[0]
                r2_chr = base[1]
                suit = base[2]
                r1_idx = RANKS.index(r1_chr)
                r2_idx = RANKS.index(r2_chr)
                for i in range(r2_idx, r1_idx, -1):
                    hands.add(f"{r1_chr}{RANKS[i]}{suit}")
        elif '-' in item and len(item) == 5: # e.g. 22-99
            # Not fully supported in this simple parser, falling back to explicit
            pass
        else:
            hands.add(item)
    return hands

def get_ranges_for_matchup(defender, opener):
    """Returns (call_range_list, 3b_range_list) in pokerstove notation based on positions."""
    if defender == "BB":
        if opener in ["LJ", "HJ"]:
            call = ["22+", "A2s+", "K8s+", "Q9s+", "J9s+", "T8s+", "98s", "87s", "76s", "65s", "54s", "ATo+", "KTo+", "QJo"]
            three_bet = ["QQ+", "AKs", "AKo", "A4s", "A5s"] # Value + bluffs
        elif opener == "CO":
            call = ["22+", "A2s+", "K5s+", "Q8s+", "J8s+", "T8s+", "97s+", "87s", "76s", "65s", "54s", "A9o+", "KTo+", "QTo+", "JTo"]
            three_bet = ["JJ+", "AQs+", "AQo", "A5s", "A4s", "A3s", "A2s", "K9s", "Q9s"]
        elif opener == "BTN":
            call = ["22+", "A2s+", "K2s+", "Q2s+", "J5s+", "T6s+", "96s+", "85s+", "75s+", "64s+", "54s", "A2o+", "K8o+", "Q9o+", "J9o+", "T9o"]
            three_bet = ["TT+", "AJs+", "AQo+", "A5s", "A4s", "A3s", "A2s", "K9s", "K8s", "QTs", "JTs", "T9s"]
        elif opener == "SB":
            call = ["22+", "A2s+", "K2s+", "Q2s+", "J2s+", "T4s+", "95s+", "85s+", "74s+", "64s+", "53s+", "43s", "A2o+", "K4o+", "Q8o+", "J8o+", "T8o+", "98o"]
            three_bet = ["88+", "ATs+", "AJo+", "KJs+", "KQo", "K9s", "Q9s", "J9s", "T9s", "98s"]
    elif defender == "SB":
        if opener in ["LJ", "HJ", "CO"]:
            call = ["88+", "AJs+", "KQs"] # SB is 3b or fold mostly, calling very tight
            three_bet = ["JJ+", "AQs+", "AKo", "A5s", "A4s", "K9s"]
        elif opener == "BTN":
            call = ["77+", "ATs+", "AJo+", "KJs+", "KQo", "QJs", "JTs"]
            three_bet = ["99+", "AJs+", "AQo+", "A5s", "A4s", "A3s", "K9s", "QTs"]
    elif defender == "BTN":
        if opener in ["LJ", "HJ"]:
            call = ["66+", "ATs+", "AJo+", "KTs+", "KQo", "QTs+", "JTs", "T9s", "98s", "87s"]
            three_bet = ["JJ+", "AQs+", "AKo", "A5s", "A4s"]
        elif opener == "CO":
            call = ["44+", "A9s+", "ATo+", "K9s+", "KJo+", "Q9s+", "J9s+", "T9s", "98s", "87s", "76s", "65s"]
            three_bet = ["TT+", "AJs+", "AQo+", "A5s", "A4s", "A3s", "K9s"]
    elif defender == "CO":
        if opener in ["LJ", "HJ"]:
            call = ["77+", "AJs+", "AQo", "KQs", "QJs", "JTs", "T9s"]
            three_bet = ["JJ+", "AQs+", "AKo", "A5s", "A4s"]
    elif defender == "HJ":
        if opener == "LJ":
            call = ["88+", "AJs+", "AQo", "KQs", "JTs"]
            three_bet = ["QQ+", "AKs", "AKo", "A5s"]
            
    return call, three_bet

def apply_stack_modifiers(hand, default_action, stack_depth):
    """Adjusts action based on stack depth specifically for short/deep quirks."""
    # Under 25bb, speculative hands fold instead of call
    if stack_depth == "<=25bb":
        speculative = parse_pokerstove(["22+", "A2s", "A3s", "A4s", "A5s", "54s", "65s", "76s", "87s", "98s", "T9s", "JTs", "QJs", "KQs"])
        if hand in speculative and default_action == "call":
            # Very short stack, pairs below 77 might shove or fold instead of call, but keeping it simple
            if hand in parse_pokerstove(["22", "33", "44", "55", "66"]):
                return "fold"
            if hand in parse_pokerstove(["A2s", "A3s", "A4s", "A5s"]):
                return "raise_all_in" # Bluff shoves
    return default_action

def generate_defense_jsons():
    out_dir = 'ranges'
    os.makedirs(out_dir, exist_ok=True)

    matchups = [
        ("HJ", "LJ"), ("CO", "LJ"), ("BTN", "LJ"), ("SB", "LJ"), ("BB", "LJ"),
        ("CO", "HJ"), ("BTN", "HJ"), ("SB", "HJ"), ("BB", "HJ"),
        ("BTN", "CO"), ("SB", "CO"), ("BB", "CO"),
        ("SB", "BTN"), ("BB", "BTN"),
        ("BB", "SB")
    ]

    stack_depths = [
        ("<=25bb", "raise_all_in"),
        ("25-50bb", "raise_2.5x"),
        ("50-80bb", "raise_3x"),
        ("80-120bb", "raise_3.5x"),
        (">120bb", "raise_4x")
    ]

    all_hands = get_all_169_hands()

    for defender, opener in matchups:
        file_data = {
            "metadata": {
                "defender": defender,
                "opener": opener,
                "note": "Refined GTO-approximated defense / 3-bet ranges."
            },
            "strategy": {}
        }
        
        call_list, three_b_list = get_ranges_for_matchup(defender, opener)
        call_set = parse_pokerstove(call_list)
        three_b_set = parse_pokerstove(three_b_list)
        
        for depth_name, main_raise_size in stack_depths:
            stack_strategy = {}
            for hand in all_hands:
                probs = {
                    "fold": 0.0, "call": 0.0, "raise_2x": 0.0, "raise_2.5x": 0.0, 
                    "raise_3x": 0.0, "raise_3.5x": 0.0, "raise_4x": 0.0, "raise_4.5x": 0.0, "raise_all_in": 0.0
                }
                
                # Determine baseline action
                baseline = "fold"
                if hand in three_b_set:
                    baseline = "raise"
                elif hand in call_set:
                    baseline = "call"
                    
                # Apply stack depth modifiers to action
                final_action = apply_stack_modifiers(hand, baseline, depth_name)
                
                # Assign size based on OOP/IP rules if action is raise
                if final_action == "raise":
                    is_oop = (defender in ["SB", "BB"]) and not (defender == "BB" and opener == "SB")
                    chosen_raise_size = main_raise_size
                    if depth_name == "80-120bb" and is_oop:
                        chosen_raise_size = "raise_4x"
                    elif depth_name == "80-120bb" and not is_oop:
                        chosen_raise_size = "raise_3x"
                    elif depth_name == ">120bb" and is_oop:
                        chosen_raise_size = "raise_4.5x"
                    elif depth_name == ">120bb" and not is_oop:
                        chosen_raise_size = "raise_3.5x"
                        
                    probs[chosen_raise_size] = 1.0
                elif final_action == "raise_all_in":
                    probs["raise_all_in"] = 1.0
                elif final_action == "call":
                    probs["call"] = 1.0
                else:
                    probs["fold"] = 1.0
                    
                stack_strategy[hand] = probs
            file_data["strategy"][depth_name] = stack_strategy

        file_path = os.path.join(out_dir, f"defense_{defender.lower()}_vs_{opener.lower()}.json")
        with open(file_path, 'w') as f:
            json.dump(file_data, f, indent=2)
        print(f"Generated {file_path} with refined ranges.")

if __name__ == '__main__':
    generate_defense_jsons()
