#!/usr/bin/env python3
"""
Transformă output-ul unui student (linii PLAYER ...) în format REF pentru input.
Folosit pentru dueluri: output student A → input student B
"""

import sys
import re

def transform_player_to_ref(line):
    """
    Transformă: PLAYER <tick> <action> <payload>
    În: REF <action> <payload> (sau REF TICK <tick> dacă e necesar)
    """
    line = line.strip()
    
    # Ignoră liniile goale sau SCOREBOARD
    if not line or line.startswith('SCOREBOARD') or line.startswith('ENERGY_COLLECTED') or \
       line.startswith('DAMAGE_DEALT') or line.startswith('STYLE_POINTS') or \
       line.startswith('PENALTIES') or line.startswith('TOTAL_SCORE') or line.startswith('WINNER'):
        return None
    
    # Parsează: PLAYER <tick> <action> <payload>
    match = re.match(r'PLAYER\s+(\d+)\s+(\w+)\s+(.*)', line)
    if not match:
        return None
    
    tick, action, payload = match.groups()
    
    # Transformă acțiunea în format REF
    # Exemple:
    # PLAYER 1 SPAWN Alpha Scout id=1 x=0 y=0 → REF SPAWN Alpha Scout 1 0 0
    # PLAYER 2 MOVE 1 N 1 → REF MOVE Alpha 1 N 1
    # PLAYER 3 ATTACK id=1 target=10 dmg=9 → REF ATTACK Alpha 1 10 9
    
    if action == 'SPAWN':
        # PLAYER 1 SPAWN Alpha Scout id=1 x=0 y=0
        # → REF SPAWN Alpha Scout 1 0 0
        match_payload = re.match(r'Alpha\s+(\w+)\s+id=(\d+)\s+x=(\d+)\s+y=(\d+)', payload)
        if match_payload:
            bot_name, bot_id, x, y = match_payload.groups()
            return f"REF SPAWN Alpha {bot_name} {bot_id} {x} {y}"
    
    elif action == 'MOVE':
        # PLAYER 2 MOVE 1 N 1
        # → REF MOVE Alpha 1 N 1
        match_payload = re.match(r'(\d+)\s+(\w+)\s+(\d+)', payload)
        if match_payload:
            bot_id, direction, steps = match_payload.groups()
            return f"REF MOVE Alpha {bot_id} {direction} {steps}"
    
    elif action == 'ATTACK':
        # PLAYER 3 ATTACK id=1 target=10 dmg=9
        # → REF ATTACK Alpha 1 10 9
        match_payload = re.match(r'id=(\d+)\s+target=(\d+)\s+dmg=(\d+)', payload)
        if match_payload:
            bot_id, target_id, dmg = match_payload.groups()
            return f"REF ATTACK Alpha {bot_id} {target_id} {dmg}"
    
    elif action == 'ABILITY':
        # PLAYER 4 ABILITY id=1 type=SCAN radius=2
        # → REF ABILITY Alpha 1 SCAN 2
        match_payload = re.match(r'id=(\d+)\s+type=(\w+)(?:\s+radius=(\d+))?', payload)
        if match_payload:
            bot_id, ability_type = match_payload.groups()[:2]
            radius = match_payload.group(3) if match_payload.group(3) else ""
            if radius:
                return f"REF ABILITY Alpha {bot_id} {ability_type} {radius}"
            else:
                return f"REF ABILITY Alpha {bot_id} {ability_type}"
    
    elif action in ['CHARGE', 'DEFEND', 'WAIT', 'UPGRADE']:
        # Acțiuni simple, păstrăm payload-ul
        return f"REF {action} Alpha {payload}"
    
    # Fallback: păstrăm structura dar transformăm în REF
    return f"REF {action} Alpha {payload}"

def main():
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        with open(input_file, 'r') as f:
            lines = f.readlines()
    else:
        lines = sys.stdin.readlines()
    
    current_tick = None
    
    for line in lines:
        line = line.strip()
        
        # Detectăm când se termină (SCOREBOARD)
        if line.startswith('SCOREBOARD'):
            print("END")
            break
        
        # Transformăm linia PLAYER în REF
        ref_line = transform_player_to_ref(line)
        if ref_line:
            # Dacă tick-ul s-a schimbat, adăugăm REF TICK
            match = re.match(r'PLAYER\s+(\d+)', line)
            if match:
                tick = match.group(1)
                if tick != current_tick:
                    print(f"REF TICK {tick}")
                    current_tick = tick
            print(ref_line)

if __name__ == '__main__':
    main()

