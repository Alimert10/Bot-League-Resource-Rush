#!/usr/bin/env python3
"""
Script pentru trimiterea rezultatelor testelor la server (GitHub Actions) - Tema 3

Trimite punctajul la server doar daca ruleaza in GitHub Actions.
"""

import sys
import json
import os
import subprocess
import urllib.request
import urllib.parse

# Schimbă directorul de lucru la rădăcina proiectului
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def citeste_key():
    """Citeste cheia unica din fisierul key.txt (opțional)."""
    try:
        with open('teste/scripturi/key.txt', 'r') as f:
            key = f.readline().strip()
            return key if key else None
    except FileNotFoundError:
        return None


def gaseste_username_anterior(actor_curent, repository):
    """Caută în istoricul Git un username GitHub real diferit de actor_curent.
    Folosește git log local + GitHub API cu GITHUB_TOKEN pentru repository-uri private.
    Ignoră bot-urile GitHub (web-flow, dependabot, etc.)."""
    # Lista de bot-uri GitHub cunoscute de ignorat
    bot_usernames = {'web-flow', 'dependabot', 'dependabot[bot]', 'github-actions[bot]', 'renovate', 'renovate[bot]'}
    
    try:
        # Extrage owner și repo din repository string
        if '/' not in repository:
            return None
        owner, repo = repository.split('/', 1)
        
        # Obține SHA-urile commit-urilor din git log local
        # În GitHub Actions, după checkout, istoricul local este disponibil (chiar dacă e shallow)
        result = subprocess.run(
            ['git', 'log', '--format=%H', '-50', '--all'],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=os.getcwd()
        )
        if result.returncode != 0:
            print(f"   Git log failed: {result.stderr.strip()}")
            return None
        
        commit_shas = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        if not commit_shas:
            print(f"   Nu s-au găsit commit-uri în istoricul local")
            return None
        
        print(f"   Găsite {len(commit_shas)} commit-uri în istoricul local")
        
        # Folosește GITHUB_TOKEN (disponibil automat în GitHub Actions)
        # Încearcă mai multe variante pentru a găsi token-ul
        github_token = os.getenv('GITHUB_TOKEN') or os.getenv('INPUT_GITHUB_TOKEN')
        if not github_token:
            # În GitHub Actions, token-ul poate fi disponibil automat dacă sunt permisiuni
            # Dar uneori trebuie setat explicit în workflow
            print(f"   GITHUB_TOKEN nu este disponibil - nu pot accesa API-ul pentru repository-uri private")
            print(f"   Verifică dacă workflow-ul are permisiuni și GITHUB_TOKEN setat în env")
            return None
        
        # Caută în commit-uri folosind GitHub API cu token pentru repository-uri private
        for commit_sha in commit_shas:
            try:
                # Folosește GitHub API pentru a obține informații despre commit
                api_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}"
                req = urllib.request.Request(api_url)
                req.add_header('Accept', 'application/vnd.github.v3+json')
                req.add_header('Authorization', f'Bearer {github_token}')
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    if response.status == 200:
                        commit_data = json.loads(response.read().decode())
                        
                        # Verifică author (cel care a făcut commit-ul)
                        author = commit_data.get('author')
                        if author:
                            # Verifică dacă este bot
                            if author.get('type') == 'Bot':
                                continue
                            username = author.get('login')
                            if username and username != actor_curent and username not in bot_usernames:
                                print(f"   Găsit username GitHub real (author) din commit {commit_sha[:7]}: {username}")
                                return username
                        
                        # Verifică committer (cel care a făcut push-ul)
                        committer = commit_data.get('committer')
                        if committer:
                            # Verifică dacă este bot
                            if committer.get('type') == 'Bot':
                                continue
                            username = committer.get('login')
                            if username and username != actor_curent and username not in bot_usernames:
                                print(f"   Găsit username GitHub real (committer) din commit {commit_sha[:7]}: {username}")
                                return username
                    elif response.status == 404:
                        # Commit-ul poate să nu fie accesibil
                        continue
                    else:
                        print(f"   API returned status {response.status} for commit {commit_sha[:7]}")
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    continue
                # Pentru alte erori, continuă cu următorul commit
                continue
            except Exception as e:
                # Continuă cu următorul commit dacă acesta eșuează
                continue
    except Exception as e:
        print(f"   Eroare la căutarea username-ului: {e}")
    return None


def verifica_rulare_github():
    """Verifica daca scriptul ruleaza in GitHub Actions."""
    # GitHub Actions seteaza variabila CI si GITHUB_ACTIONS
    if os.getenv('GITHUB_ACTIONS') != 'true':
        return False, None
    
    # Obtine informatii GitHub (toate sunt publice, nu necesita secrets)
    repository = os.getenv('GITHUB_REPOSITORY', '')
    # Extrage owner-ul repository-ului (primul element din "owner/repo")
    repository_owner = repository.split('/')[0] if '/' in repository else repository
    # Actor-ul (cel care face push) este identificatorul unic, nu repository_owner
    actor = os.getenv('GITHUB_ACTOR', '')
    
    # Dacă actor-ul este "Trifuu", caută un username diferit în push-urile anterioare
    if actor == 'Trifuu':
        username_alternativ = gaseste_username_anterior(actor, repository)
        if username_alternativ:
            print(f"⚠️  Detectat push de la 'Trifuu' - folosesc username alternativ: {username_alternativ}")
            actor = username_alternativ
        else:
            print(f"⚠️  Detectat push de la 'Trifuu' - nu s-a găsit username alternativ în istoric")
            print(f"   Repository: {repository}")
    
    github_info = {
        'repository': repository,
        'repository_owner': repository_owner,  # Proprietarul repository-ului (template owner)
        'commit_sha': os.getenv('GITHUB_SHA'),
        'run_id': os.getenv('GITHUB_RUN_ID'),
        'actor': actor,  # Username-ul care a facut push (identificator unic)
        'ref': os.getenv('GITHUB_REF')  # Branch
    }
    
    return True, github_info


def trimite_la_server(key, teste_trecute, teste_totale, scoruri_teste, github_info, server_url):
    """Trimite rezultatele la server prin POST."""
    import requests
    import hashlib
    
    SHARED_SECRET = "tema3_poo_2025_secret_key"
    
    # Calculează scor total (suma tuturor scorurilor)
    scor_total = sum(scoruri_teste)
    
    # Actor-ul (cel care face push) este identificatorul unic, nu repository_owner
    actor = github_info.get('actor', 'unknown')
    if not actor or actor == 'unknown':
        # Fallback la repository_owner dacă actor nu e disponibil (nu ar trebui să se întâmple)
        actor = github_info.get('repository_owner', 'unknown')
    
    # Construieste payload-ul
    payload = {
        'github_username': actor,  # Identificator unic (cel care face push)
        'key': key,  # Cheia unică pentru editare nickname
        'teste_trecute': teste_trecute,
        'teste_totale': teste_totale,
        'scoruri_teste': scoruri_teste,  # Lista cu scorurile pentru fiecare test (0 dacă a picat)
        'scor_total': scor_total,  # Suma totală de scoruri
        'repository': github_info.get('repository', 'unknown'),
        'commit_sha': github_info.get('commit_sha', 'unknown'),
        'run_id': github_info.get('run_id', 'unknown'),
        'actor': github_info.get('actor', 'unknown'),  # Cine a făcut push
        'repository_owner': github_info.get('repository_owner', 'unknown'),  # Proprietarul repository-ului
        'ref': github_info.get('ref', 'unknown')
    }
    
    # Generează semnătură pentru validare
    # Hash: (key sau github_username) + commit_sha + shared_secret
    signature_base = key if key else actor
    signature_data = f"{signature_base}:{github_info.get('commit_sha', '')}:{SHARED_SECRET}"
    signature = hashlib.sha256(signature_data.encode()).hexdigest()
    
    # Headers cu semnătură
    headers = {
        'Content-Type': 'application/json',
        'X-GitHub-Signature': signature,
        'X-GitHub-Event': 'classroom_test_tema3'
    }
    
    try:
        # Adaugă https:// daca nu exista
        if not server_url.startswith('http'):
            url = f"https://{server_url}/submit_score_tema3"
        else:
            url = f"{server_url}/submit_score_tema3"
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            nickname = result.get('nickname', 'Unknown')
            print(f"\n✓ Rezultate trimise cu succes la server!")
            print(f"🎯 Nickname-ul tău: {nickname}")
            print(f"   Vezi clasamentul pe: https://{server_url}/tema3")
            return True
        else:
            print(f"\n✗ Eroare la trimitere: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Detalii: {error_data.get('error', 'Unknown error')}")
            except:
                pass
            return False
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Eroare de conexiune la server: {e}")
        return False


def main():
    if len(sys.argv) < 4:
        print("Utilizare: python3 teste/scripturi/trimite_rezultate.py <teste_trecute> <teste_totale> <server_url>")
        sys.exit(1)
    
    teste_trecute = int(sys.argv[1])
    teste_totale = int(sys.argv[2])
    server_url = sys.argv[3]
    
    # Citește scorurile testelor din fișier
    scoruri_teste = []
    try:
        with open('.test_results.txt', 'r') as f:
            lines = f.readlines()
            if len(lines) >= 2:
                scoruri_str = lines[1].strip().split()
                scoruri_teste = [int(s) for s in scoruri_str]
    except:
        # Dacă nu poate citi scorurile, trimite listă goală
        scoruri_teste = []
    
    # Citeste cheia unica (opțional - pentru editare nickname)
    key = citeste_key()
    if not key:
        print("ℹ️  Nu există cheie în teste/scripturi/key.txt - nickname-ul va fi auto-generat")
        print("   Pentru a edita nickname-ul, generează o cheie cu: bash teste/scripturi/genereaza_key.sh")
    
    # Verifica daca ruleaza in GitHub Actions
    este_github, github_info = verifica_rulare_github()
    
    if not este_github:
        print("\nℹ️  Rulare locala detectata - rezultatele NU vor fi trimise la server.")
        print(f"   (Pentru trimitere, ruleaza in GitHub Actions cu push la repository)")
        sys.exit(0)
    
    # Trimite rezultatele
    scor_total = sum(scoruri_teste)
    print(f"\n📤 Trimit rezultate")
    print(f"   Teste trecute: {teste_trecute}/{teste_totale}")
    print(f"   Scor total: {scor_total}")
    print(f"   Repository: {github_info.get('repository', 'N/A')}")
    print(f"   Proprietar repo: {github_info.get('repository_owner', 'N/A')}")
    print(f"   Actor (identificator unic): {github_info.get('actor', 'N/A')}")
    
    succes = trimite_la_server(key, teste_trecute, teste_totale, scoruri_teste, github_info, server_url)
    
    sys.exit(0 if succes else 1)


if __name__ == '__main__':
    main()
