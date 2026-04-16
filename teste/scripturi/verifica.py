#!/usr/bin/env python3
"""
Script de verificare pentru Tema 3 - Liga Boților (Resource Rush)

Verifică logica jocului:
- Citește input linie cu linie și trimite la program
- Verifică mișcări invalide (perete, empty)
- Verifică colectarea resurselor
- Verifică multiplicatorii (D, T)
- Verifică superputerea Jump
- Verifică finalizare
- Salvează log în output/testX.out
"""

import sys
import os
import subprocess
import re

# Schimbă directorul de lucru la rădăcina proiectului
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Coduri culori ANSI
VERDE = '\033[92m'
ROSU = '\033[91m'
GALBEN = '\033[93m'
RESET = '\033[0m'

class GameState:
    def __init__(self, width, height, matrix, initial_pos, player2_pos, final_pos, max_ticks):
        self.width = width
        self.height = height
        self.matrix = matrix  # matrix[x][y] unde x=linie, y=coloană
        self.initial_pos = initial_pos  # [x, y]
        self.player2_pos = player2_pos
        self.player2_has_jump = False
        self.final_pos = final_pos
        self.max_ticks = max_ticks
        
        # Stare jucător
        self.player_x = initial_pos[0]
        self.player_y = initial_pos[1]
        self.score = 0
        self.multiplier = 1  # D=2, T=3, D+T=6
        self.has_jump = False
        self.current_tick = 0
        
        # Log pentru output
        self.log_lines = []
        
    def get_cell(self, x, y):
        """Returnează celula de la coordonatele (x, y) sau 'E' dacă în afara hărții."""
        if x < 0 or x >= self.height or y < 0 or y >= self.width:
            return 'E'
        return self.matrix[x][y] if self.matrix[x][y] else 'E'
    
    def is_valid_move(self, new_x, new_y):
        """Verifică dacă o mișcare este validă."""
        cell = self.get_cell(new_x, new_y)
        # Nu poți merge pe E, W, F (fără Jump)
        if cell in ['E', 'W', 'F']:
            return False
        return True
    
    def can_jump_over(self, x, y):
        """Verifică dacă poate sări peste celula (x, y) cu Jump."""
        cell = self.get_cell(x, y)
        return self.has_jump and cell in ['W', 'E']
    
    def move_player(self, new_x, new_y):
        """Mută jucătorul la coordonatele (new_x, new_y) și procesează celula."""
        if not self.is_valid_move(new_x, new_y):
            return False, "Mișcare invalidă: perete sau empty"
        
        # Verifică dacă trebuie să sară peste ceva
        dx = new_x - self.player_x
        dy = new_y - self.player_y
        
        # Verifică dacă mișcarea este de 2 casete (necesită Jump)
        if abs(dx) + abs(dy) == 2:
            if not self.has_jump:
                return False, "Mișcare de 2 casete necesită Jump"
            # Verifică dacă trebuie să sară peste ceva
            mid_x = self.player_x + (dx // 2)
            mid_y = self.player_y + (dy // 2)
            mid_cell = self.get_cell(mid_x, mid_y)
            if mid_cell == 'F':
                return False, "Nu poate sări peste celula intermediară"  # F este fatal
            if mid_cell in ['W', 'E']:
                if not self.can_jump_over(mid_x, mid_y):
                    return False, "Nu poate sări peste celula intermediară"
            else:
                # Pentru celule normale (0, resurse, J, D, T) se poate trece peste dacă destinația este validă
                if not self.is_valid_move(mid_x, mid_y):
                    return False, "Nu poate sări peste celula intermediară"
        
        # Verifică fire (fatal)
        cell = self.get_cell(new_x, new_y)
        if cell == 'F':
            return False, "Fire este fatal"
        
        # Mută jucătorul
        self.player_x = new_x
        self.player_y = new_y
        
        # Procesează celula
        if cell == 'J':
            self.has_jump = True
            # Celula devine 0 (Jump se colectează)
            self.matrix[new_x][new_y] = '0'
        elif cell == 'D':
            self.multiplier *= 2
            # Celula devine 0 (D se colectează)
            self.matrix[new_x][new_y] = '0'
        elif cell == 'T':
            self.multiplier *= 3
            # Celula devine 0 (T se colectează)
            self.matrix[new_x][new_y] = '0'
        elif cell.isdigit() and cell != '0':
            # Colectează resursă
            value = int(cell)
            self.score += value * self.multiplier
            # Celula devine 0
            self.matrix[new_x][new_y] = '0'
        
        # Jump rămâne activ permanent (nu se consumă)
        
        return True, None
    
    def check_victory(self):
        """Verifică dacă jucătorul a ajuns la punctul final."""
        return self.player_x == self.final_pos[0] and self.player_y == self.final_pos[1]
    
    def add_log(self, line):
        """Adaugă o linie în log."""
        self.log_lines.append(line)

    def apply_opponent_move(self, x, y):
        """Simulează mișcarea adversarului (elimină resurse/power-ups de pe celulă)."""
        if x < 0 or x >= self.height or y < 0 or y >= self.width:
            return
        cell = self.matrix[x][y]
        # Dacă adversarul ia un power-up sau resursă, celula devine 0
        if cell == 'J':
            self.player2_has_jump = True
            self.matrix[x][y] = '0'
        elif cell == 'D' or cell == 'T':
            self.matrix[x][y] = '0'
        elif cell.isdigit() and cell != '0':
            self.matrix[x][y] = '0'
        self.player2_pos = [x, y]

def parse_input(input_file):
    """Parsează fișierul de input."""
    with open(input_file, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    if len(lines) < 10:
        raise ValueError(f"Fișierul de input este prea scurt sau gol: {input_file}")
    
    # Parsează ARENA
    if not lines[0].startswith('ARENA'):
        raise ValueError(f"Lipsește linia ARENA în {input_file}")
    arena_line = lines[0]
    parts = arena_line.split()
    if len(parts) < 4:
        raise ValueError(f"Format invalid ARENA: {arena_line}")
    height = int(parts[1])
    width = int(parts[2])
    max_ticks = int(parts[3])
    
    # Parsează poziții
    if len(lines) < 4:
        raise ValueError(f"Lipsesc pozițiile în {input_file}")
    initial_pos = [int(x) for x in lines[1].split()]
    player2_pos = [int(x) for x in lines[2].split()]
    final_pos = [int(x) for x in lines[3].split()]
    
    # Parsează MAP
    if 'MAP' not in lines:
        raise ValueError(f"Lipsește MAP în {input_file}")
    if 'END_MAP' not in lines:
        raise ValueError(f"Lipsește END_MAP în {input_file}")
    
    map_start = lines.index('MAP') + 1
    map_end = lines.index('END_MAP')
    matrix = []
    for i in range(map_start, map_end):
        row = lines[i].split()
        matrix.append(row)
    
    # Parsează STREAM
    if 'STREAM' not in lines:
        raise ValueError(f"Lipsește STREAM în {input_file}")
    stream_start = lines.index('STREAM') + 1
    stream_lines = [line for line in lines[stream_start:] if line and line != 'END']
    
    return {
        'width': width,
        'height': height,
        'matrix': matrix,
        'initial_pos': initial_pos,
        'player2_pos': player2_pos,
        'final_pos': final_pos,
        'max_ticks': max_ticks,
        'stream_lines': stream_lines
    }

def run_test(test_id, executable='./arena', verbose=True):
    """Rulează un test și verifică logica. Returnează (result, score, error_reason)."""
    input_file = f"teste/input/{test_id}.txt"
    output_file = f"teste/output/{test_id}.out"
    
    if not os.path.exists(input_file):
        print(f"{ROSU}❌ Testul {test_id} nu există: {input_file}{RESET}")
        return False, 0
    
    if not os.path.exists(executable):
        print(f"{ROSU}❌ Executabilul nu există: {executable}{RESET}")
        print(f"   Rulează: make build")
        return False, 0
    
    # Parsează input
    error_reason = None
    try:
        game_data = parse_input(input_file)
    except Exception as e:
        print(f"{ROSU}❌ Eroare la parsare input: {e}{RESET}")
        return False, 0
    
    # Verifică dacă există linii în stream
    if not game_data['stream_lines']:
        print(f"{ROSU}❌ Test {test_id}: Nu există comenzi TICK în stream{RESET}")
        return False, 0
    
    # Creează starea jocului
    game = GameState(
        game_data['width'],
        game_data['height'],
        game_data['matrix'],
        game_data['initial_pos'],
        game_data['player2_pos'],
        game_data['final_pos'],
        game_data['max_ticks']
    )
    
    # Pregătește input pentru program (până la STREAM inclusiv)
    input_lines = []
    with open(input_file, 'r') as f:
        for line in f:
            input_lines.append(line)
            if line.strip() == 'STREAM':
                break
    
    # Adaugă log-ul inițial
    game.add_log('ARENA ' + ' '.join(str(x) for x in [game.height, game.width, game.max_ticks]))
    game.add_log(' '.join(str(x) for x in game.initial_pos))
    game.add_log(' '.join(str(x) for x in game.player2_pos))
    game.add_log(' '.join(str(x) for x in game.final_pos))
    game.add_log('MAP')
    for row in game.matrix:
        game.add_log(' '.join(row))
    game.add_log('END_MAP')
    game.add_log('STREAM')
    
    # Rulează programul
    try:
        proc = subprocess.Popen(
            [executable],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Trimite input-ul inițial (până la STREAM inclusiv)
        initial_input = ''.join(input_lines)
        proc.stdin.write(initial_input)
        proc.stdin.flush()
        
        # Procesează stream-ul linie cu linie
        victory = False
        for stream_line in game_data['stream_lines']:
            if not stream_line or stream_line == 'END':
                break
            
            # Adaugă linia TICK în log
            game.add_log(stream_line)

            # Procesează mișcarea adversarului dacă este MOVE
            parts = stream_line.split()
            if len(parts) >= 4 and parts[1].isdigit():
                action_op = parts[2]
                if action_op == 'MOVE' and len(parts) >= 5:
                    try:
                        op_x = int(parts[3])
                        op_y = int(parts[4])
                        game.apply_opponent_move(op_x, op_y)
                    except:
                        pass
            
            # Trimite linia la program
            proc.stdin.write(stream_line + '\n')
            proc.stdin.flush()
            
            # Citește răspunsul programului (linie cu linie până la PLAYER)
            player_response = None
            import time
            import select
            
            # Așteaptă răspunsul (cu timeout)
            start_time = time.time()
            timeout = 5.0
            
            while time.time() - start_time < timeout:
                # Verifică dacă procesul s-a terminat
                if proc.poll() is not None:
                    # Procesul s-a terminat
                    try:
                        # Încearcă să citească ultimele linii
                        remaining = proc.stdout.read()
                        if remaining:
                            for line in remaining.split('\n'):
                                line = line.strip()
                                if line and line.startswith('PLAYER'):
                                    player_response = line
                                    break
                    except:
                        pass
                    break
                
                # Verifică dacă există date disponibile (doar pe Linux/Mac)
                try:
                    if sys.platform != 'win32':
                        ready, _, _ = select.select([proc.stdout], [], [], 0.1)
                        if not ready:
                            time.sleep(0.05)
                            continue
                except:
                    pass
                
                # Citește o linie
                try:
                    line = proc.stdout.readline()
                    if line:
                        line = line.strip()
                        # Acceptă atât formatul vechi (PLAYER <tick> ...) cât și cel simplu (MOVE/WAIT)
                        if line and (line.startswith('PLAYER') or line.startswith('MOVE') or line.startswith('WAIT')):
                            player_response = line
                            break
                except:
                    break
                
                time.sleep(0.01)
            
            if not player_response:
                # Programul nu a răspuns
                error_msg = f"ERROR: Programul nu a răspuns la {stream_line}"
                game.add_log(error_msg)
                error_reason = error_reason or error_msg
                if verbose:
                    print(f"   {ROSU}{error_msg}{RESET}")
                    # Încearcă să citească stderr pentru debug
                    try:
                        stderr_data = proc.stderr.read()
                        if stderr_data:
                            stderr_str = stderr_data.decode('utf-8', errors='ignore') if isinstance(stderr_data, bytes) else str(stderr_data)
                            game.add_log(f"STDERR: {stderr_str[:500]}")
                            print(f"   {ROSU}STDERR: {stderr_str[:200]}{RESET}")
                    except Exception as e:
                        pass
                try:
                    proc.terminate()
                    proc.kill()
                except:
                    pass
                break
            
            # Parsează răspunsul
            # Formate acceptate:
            #   - PLAYER <tick> MOVE <x> <y> / PLAYER <tick> WAIT
            #   - MOVE <x> <y> / WAIT  (tick-ul este dedus incremental)
            match = re.match(r'PLAYER\s+(\d+)\s+(MOVE|WAIT)(?:\s+(\d+)\s+(\d+))?', player_response)
            if not match:
                # Încearcă formatul simplu fără prefix PLAYER
                simple_match = re.match(r'(MOVE|WAIT)(?:\s+(\d+)\s+(\d+))?$', player_response)
                if not simple_match:
                    err = f"ERROR: Format invalid: {player_response}"
                    game.add_log(err)
                    error_reason = error_reason or err
                    proc.terminate()
                    break
                action = simple_match.group(1)
                tick = game.current_tick + 1  # deduce tick-ul curent + 1
                new_x = int(simple_match.group(2)) if simple_match.group(2) else None
                new_y = int(simple_match.group(3)) if simple_match.group(3) else None
            else:
                tick = int(match.group(1))
                action = match.group(2)
                new_x = int(match.group(3)) if match.group(3) else None
                new_y = int(match.group(4)) if match.group(4) else None
            
            # Adaugă răspunsul în log
            game.add_log(player_response)
            
            if action == 'WAIT':
                game.current_tick = tick
            elif action == 'MOVE':
                # Verifică mișcarea
                success, error = game.move_player(new_x, new_y)
                if not success:
                    error_msg = f"ERROR: {error}"
                    game.add_log(error_msg)
                    error_reason = error_reason or error
                    if verbose:
                        print(f"   {ROSU}{error_msg}{RESET}")
                    try:
                        proc.terminate()
                        proc.kill()
                    except:
                        pass
                    break
                
                game.current_tick = tick
                
                # Verifică victorie
                if game.check_victory():
                    victory = True
                    break
        
        # Așteaptă terminarea procesului
        try:
            proc.wait(timeout=1)
        except:
            proc.terminate()
        
        # Verifică rezultatul
        if victory:
            result = True
        elif game.current_tick >= game.max_ticks:
            msg = f"Nu a ajuns la punctul final înainte de terminarea tick-urilor (tick {game.current_tick}/{game.max_ticks})"
            game.add_log(f"ERROR: {msg}")
            error_reason = error_reason or msg
            result = False
        else:
            msg = f"Jocul s-a terminat prematur (tick {game.current_tick}/{game.max_ticks})"
            game.add_log(f"ERROR: {msg}")
            error_reason = error_reason or msg
            result = False
        
        # Salvează log-ul
        os.makedirs('teste/output', exist_ok=True)
        with open(output_file, 'w') as f:
            f.write('\n'.join(game.log_lines))
        
        # Dacă testul a eșuat, afișează ultimele linii din log pentru debug
        if verbose and (not result) and len(game.log_lines) > 0:
            print(f"   Ultimele linii din log:")
            for line in game.log_lines[-5:]:
                print(f"     {line}")
        
        return result, game.score, error_reason
        
    except Exception as e:
        print(f"{ROSU}❌ Eroare la rulare: {e}{RESET}")
        return False, 0, str(e)

def verifica_test(test_id, verbose=True):
    """Verifică un test specific."""
    result, score, error_reason = run_test(test_id, verbose=verbose)
    
    # Verifică limita minimă
    limite_file = "teste/limite_minime.txt"
    min_score = None
    if os.path.exists(limite_file):
        with open(limite_file, 'r') as f:
            for line in f:
                # Normalizează test_id (test1 -> test01, test10 -> test10)
                normalized_test_id = test_id
                if test_id.startswith('test') and len(test_id) == 5:  # test1, test2, etc.
                    num = test_id[4:]
                    normalized_test_id = f"test{int(num):02d}"
                # Încearcă ambele formate
                match = re.match(rf'{test_id}\s+(\d+)', line.strip()) or re.match(rf'{normalized_test_id}\s+(\d+)', line.strip())
                if match:
                    min_score = int(match.group(1))
                    break
    
    if result:
        if min_score is not None:
            if score >= min_score:
                print(f"{VERDE}✓ Test {test_id}: {score} / {min_score} (min){RESET}")
                return True, score
            else:
                print(f"{ROSU}✗ Test {test_id}: {score} / {min_score} (min) - INSUFICIENT{RESET}")
                return False, score
        else:
            print(f"{GALBEN}⚠ Test {test_id}: {score} (fără limită minimă){RESET}")
            return True, score
    else:
        reason = error_reason or "FAILED"
        print(f"{ROSU}✗ Test {test_id}: {reason}{RESET}")
        if verbose:
            print(f"   Log complet: teste/output/{test_id}.out")
        return False, score

def verifica_toate():
    """Verifică toate testele (mod sumar)."""
    print("=" * 80)
    print("RULARE TESTE AUTOMATE - TEMA 3 LIGA BOȚILOR")
    print("=" * 80)
    print()
    
    # Găsește toate testele
    test_files = []
    if os.path.exists("teste/input"):
        for f in os.listdir("teste/input"):
            if f.endswith('.txt'):
                test_id = f.replace('.txt', '')
                test_files.append(test_id)
        
        # Sortează numeric (test1, test2, ..., test10, test11, ..., test20)
        def sort_key(test_id):
            # Extrage numărul din test_id (test1 -> 1, test10 -> 10, etc.)
            if test_id.startswith('test'):
                try:
                    num = int(test_id[4:])  # Extrage numărul după "test"
                    return num
                except:
                    return 999  # Dacă nu e număr valid, pune la sfârșit
            return 999
        
        test_files.sort(key=sort_key)
    
    if not test_files:
        print(f"{ROSU}❌ Nu există teste în teste/input/{RESET}")
        return
    
    trecute = 0
    esuate = 0
    total_scor = 0
    scoruri_teste = []
    
    for test_id in test_files:
        passed, score = verifica_test(test_id, verbose=False)
        # Dacă testul a picat, salvează scor 0
        if not passed:
            score = 0
        scoruri_teste.append(score)
        if passed:
            trecute += 1
            total_scor += score
        else:
            esuate += 1
    
    print("=" * 80)
    print("REZUMAT TESTE")
    print("=" * 80)
    print(f"{VERDE}✓ Trecute: {trecute}/{len(test_files)}{RESET}")
    print(f"{ROSU}✗ Eșuate:  {esuate}/{len(test_files)}{RESET}")
    print(f"Scor total: {total_scor}")
    print("=" * 80)
    
    # Salvează rezultatele pentru trimitere la server
    with open('.test_results.txt', 'w') as f:
        f.write(f"{trecute} {len(test_files)}\n")
        f.write(' '.join(str(s) for s in scoruri_teste))

def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == 'all':
            verifica_toate()
        else:
            # Test specific
            test_id = arg if arg.startswith('test') else f"test{int(arg):02d}"
            verifica_test(test_id)
    else:
        print("Usage: python3 verifica.py [test_id|all]")
        print("   Ex: python3 verifica.py test1")
        print("   Ex: python3 verifica.py all")

if __name__ == '__main__':
    main()
