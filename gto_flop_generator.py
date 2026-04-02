import json
import os

def create_base_actions():
    return {
        "check": 0.0,
        "bet_10": 0.0,
        "bet_25": 0.0,
        "bet_33": 0.0,
        "bet_50": 0.0,
        "bet_75": 0.0,
        "bet_100": 0.0,
        "bet_125": 0.0,
        "bet_200": 0.0
    }

def get_strategy(role, texture, strength):
    actions = create_base_actions()
    
    # --- AGRESSOR IP ---
    if role == "aggressor_ip":
        if texture in ["dry_static", "paired"]:
            if strength == "made_premium": actions["bet_33"] = 1.0
            elif strength == "made_marginal": actions["bet_25"] = 0.5; actions["check"] = 0.5
            elif strength == "strong_draw": actions["bet_33"] = 1.0
            elif strength == "weak_draw": actions["bet_25"] = 1.0
            elif strength == "total_miss": actions["bet_25"] = 0.6; actions["check"] = 0.4
        elif texture == "wet_dynamic":
            if strength == "made_premium": actions["bet_75"] = 1.0
            elif strength == "made_marginal": actions["check"] = 1.0
            elif strength == "strong_draw": actions["bet_75"] = 0.8; actions["check"] = 0.2
            elif strength == "weak_draw": actions["check"] = 1.0
            elif strength == "total_miss": actions["check"] = 1.0
        elif texture == "monotone":
            if strength == "made_premium": actions["bet_25"] = 1.0
            elif strength == "made_marginal": actions["check"] = 1.0
            elif strength == "strong_draw": actions["bet_25"] = 0.7; actions["check"] = 0.3
            elif strength == "weak_draw": actions["check"] = 1.0
            elif strength == "total_miss": actions["bet_10"] = 0.5; actions["check"] = 0.5

    # --- AGRESSOR OOP ---
    elif role == "aggressor_oop":
        if texture in ["dry_static", "paired"]:
            if strength == "made_premium": actions["bet_50"] = 0.6; actions["check"] = 0.4
            elif strength == "made_marginal": actions["check"] = 1.0
            elif strength == "strong_draw": actions["bet_50"] = 0.5; actions["check"] = 0.5
            elif strength == "weak_draw": actions["check"] = 1.0
            elif strength == "total_miss": actions["check"] = 0.8; actions["bet_33"] = 0.2
        elif texture == "wet_dynamic":
            if strength == "made_premium": actions["bet_75"] = 0.8; actions["check"] = 0.2
            elif strength == "made_marginal": actions["check"] = 1.0
            elif strength == "strong_draw": actions["bet_75"] = 0.5; actions["check"] = 0.5
            elif strength == "weak_draw": actions["check"] = 1.0
            elif strength == "total_miss": actions["check"] = 1.0
        elif texture == "monotone":
            actions["check"] = 1.0 # Very defensive OOP on monotone

    # --- CALLER OOP ---
    elif role == "caller_oop":
        # Usually checking 100% to the preflop aggressor (standard GTO play).
        # We add some donk bets on dynamic boards when holding nuts/strong draws to protect equity.
        if texture in ["wet_dynamic", "monotone"]:
            if strength == "made_premium": actions["check"] = 0.8; actions["bet_25"] = 0.2
            elif strength == "strong_draw": actions["check"] = 0.7; actions["bet_25"] = 0.3
            else: actions["check"] = 1.0
        else:
            actions["check"] = 1.0

    # --- CALLER IP ---
    elif role == "caller_ip":
        # IP caller facing a check (since we only evaluate if it's our turn to bet)
        if texture in ["dry_static", "paired"]:
            if strength == "made_premium": actions["bet_50"] = 0.8; actions["check"] = 0.2
            elif strength == "made_marginal": actions["check"] = 0.8; actions["bet_33"] = 0.2
            elif strength == "strong_draw": actions["bet_50"] = 0.7; actions["check"] = 0.3
            elif strength == "weak_draw": actions["bet_33"] = 0.5; actions["check"] = 0.5
            elif strength == "total_miss": actions["check"] = 1.0
        elif texture == "wet_dynamic":
            if strength == "made_premium": actions["bet_75"] = 1.0
            elif strength == "made_marginal": actions["check"] = 1.0
            elif strength == "strong_draw": actions["bet_50"] = 1.0
            elif strength == "weak_draw": actions["check"] = 1.0
            elif strength == "total_miss": actions["check"] = 0.7; actions["bet_125"] = 0.3 # Some overbet bluffs
        elif texture == "monotone":
            if strength == "made_premium": actions["bet_33"] = 0.8; actions["check"] = 0.2
            elif strength == "strong_draw": actions["bet_33"] = 0.6; actions["check"] = 0.4
            else: actions["check"] = 1.0
            
    # Fallback to check if empty
    if sum(actions.values()) == 0:
        actions["check"] = 1.0
        
    return actions

def generate_flop_jsons():
    out_dir = os.path.join('ranges', 'flop')
    os.makedirs(out_dir, exist_ok=True)

    roles = ["aggressor_ip", "aggressor_oop", "caller_ip", "caller_oop"]
    textures = {
        "dry_static": "Boards desconectados (ej. K-7-2 rainbow). Poca equity para el rival.",
        "wet_dynamic": "Boards muy conectados (ej. J-T-9 con colores).",
        "monotone": "Boards con tres cartas del mismo palo.",
        "paired": "Boards doblados (ej. J-J-4)."
    }
    strengths = ["made_premium", "made_marginal", "strong_draw", "weak_draw", "total_miss"]

    for role in roles:
        file_data = {
            "metadata": {
                "role": role,
                "description": f"Flop strategy for {role.replace('_', ' ').title()}",
                "note": "Probabilities for first actions (check vs bet sizing)."
            },
            "board_texture": {}
        }
        
        for texture, desc in textures.items():
            texture_data = {
                "description": desc,
                "hand_categories": {}
            }
            
            for strength in strengths:
                texture_data["hand_categories"][strength] = get_strategy(role, texture, strength)
                
            file_data["board_texture"][texture] = texture_data

        file_path = os.path.join(out_dir, f"flop_{role}.json")
        with open(file_path, 'w') as f:
            json.dump(file_data, f, indent=2)
        print(f"Generated {file_path}")

if __name__ == '__main__':
    generate_flop_jsons()
