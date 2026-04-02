import json
import os

RANKS = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
RANK_TO_INT = {r: 14 - i for i, r in enumerate(RANKS)}

def get_all_169_hands():
    hands = []
    # Pairs
    for r in RANKS:
        hands.append(f"{r}{r}")
    # Suited and Offsuit
    for i in range(len(RANKS)):
        for j in range(i + 1, len(RANKS)):
            r1 = RANKS[i]
            r2 = RANKS[j]
            hands.append(f"{r1}{r2}s")
            hands.append(f"{r1}{r2}o")
    return hands

def parse_pokerstove_range(range_list):
    """Parses a pokerstove list of strings like ['66+', 'A3s+', 'KJo+'] to a set of specific hand strings."""
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
                # The '+' means the second card moves up until it hits the card just below the first card
                for i in range(r2_idx, r1_idx, -1):
                    hands.add(f"{r1_chr}{RANKS[i]}{suit}")
        else: # Specific hand like 'T9s' or '87o' or 'AA'
            hands.add(item)
    return hands

def generate_jsons():
    with open('preflop_6max_100bb_nl10.json', 'r') as f:
        data = json.load(f)
    
    rfi = data['open_raise_first_in']
    
    all_hands = get_all_169_hands()
    
    out_dir = 'ranges'
    os.makedirs(out_dir, exist_ok=True)
    
    positions = ['LJ', 'HJ', 'CO', 'BTN', 'SB']
    
    for pos in positions:
        pos_range_list = rfi[pos]['range']
        active_hands = parse_pokerstove_range(pos_range_list)
        
        # SB is typically 3bb, others 2.5bb for modern defaults, or we can just stick to 2.5bb as user requested
        raise_key = "raise_3bb" if pos == "SB" else "raise_2.5bb"
        
        strategy = {}
        for hand in all_hands:
            if hand in active_hands:
                probs = {
                    "fold": 0.0,
                    "call": 0.0,
                    "raise_2bb": 0.0,
                    "raise_2.25bb": 0.0,
                    "raise_2.5bb": 1.0 if raise_key == "raise_2.5bb" else 0.0,
                    "raise_3bb": 1.0 if raise_key == "raise_3bb" else 0.0,
                    "raise_3.5bb": 0.0
                }
            else:
                probs = {
                    "fold": 1.0,
                    "call": 0.0,
                    "raise_2bb": 0.0,
                    "raise_2.25bb": 0.0,
                    "raise_2.5bb": 0.0,
                    "raise_3bb": 0.0,
                    "raise_3.5bb": 0.0
                }
            strategy[hand] = probs
            
        output = {
            "metadata": {
                "position": pos,
                "situation": "Open Raise First In",
                "note": "Extracted from preflop_6max_100bb_nl10.json"
            },
            "strategy": strategy
        }
        
        file_path = os.path.join(out_dir, f"open_raise_{pos.lower()}.json")
        with open(file_path, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"Generated {file_path}")

if __name__ == '__main__':
    generate_jsons()
