#!/usr/bin/env python3
import subprocess
import sys
import os

EXCLUDED_PATTERNS = ['myenv', 'venv', '__pycache__', '.egg-info', '.DS_Store']

def run(cmd):
    """Run a shell command and print output live."""
    print(f"\n[CMD] {cmd}")
    result = subprocess.run(cmd, shell=True, text=True)
    if result.returncode != 0:
        print(f"\033[91m[Erreur] La commande a échoué : {cmd}\033[0m")
        sys.exit(result.returncode)

def ask_git_identity():
    # Vérifie que git user.name et user.email sont bien configurés
    try:
        name = subprocess.check_output("git config user.name", shell=True, text=True).strip()
        email = subprocess.check_output("git config user.email", shell=True, text=True).strip()
        if name and email:
            return
    except subprocess.CalledProcessError:
        pass
    print("\n\033[93m⚠️ Git user.name et user.email ne sont pas configurés. On va les définir.\033[0m")
    name = input("Nom à utiliser pour Git (user.name) : ").strip()
    email = input("Email à utiliser pour Git (user.email) : ").strip()
    if name:
        run(f'git config --local user.name "{name}"')
    if email:
        run(f'git config --local user.email "{email}"')

def git_status_short():
    # Retourne [(status, path)]
    lines = subprocess.check_output("git status --short", shell=True, text=True).splitlines()
    res = []
    for line in lines:
        status, path = line[:2].strip(), line[2:].strip()
        # Filtrage basique pour ne pas afficher les dossiers virtuels
        if not any(x in path for x in EXCLUDED_PATTERNS):
            res.append((status, path))
    return res

def affiche_et_choisis_fichiers():
    files = git_status_short()
    if not files:
        print("\nAucun fichier modifié ou non suivi à ajouter.")
        return []

    print("\nFichiers modifiés / non suivis à ajouter :")
    for i, (statut, chemin) in enumerate(files, 1):
        print(f"  {i:2d}. [{statut}] {chemin}")

    print("\nTout ajouter ? (o/N) ou liste les fichiers séparés par espace ou numéros pour n’en ajouter qu’une partie")
    choix = input("> ").strip()
    if choix.lower() == 'o':
        selection = [chemin for _, chemin in files]
    elif choix == "":
        print("Aucune sélection. Arrêt.")
        sys.exit(0)
    else:
        indices = [s for s in choix.split() if s.isdigit()]
        chemins = [s for s in choix.split() if not s.isdigit()]
        selection = []
        if indices:
            selection += [files[int(idx)-1][1] for idx in indices if 0 < int(idx) <= len(files)]
        selection += chemins

    # Vérifier existence et filtrer
    selection = [chemin for chemin in selection if os.path.exists(chemin)]
    if not selection:
        print("\033[91mAucun fichier valide sélectionné. Arrêt.\033[0m")
        sys.exit(1)
    print("\nFichiers qui vont être ajoutés :")
    print(" ".join(f'"{f}"' for f in selection))
    confirm = input("Confirmer l’ajout ? (O/n) : ").strip().lower()
    if confirm not in ("", "o", "O"):
        print("Ajout annulé.")
        sys.exit(0)
    return selection

def main():
    print("=== 🚀 PUSHEUR GIT Framagit & GitHub ===")
    print("État du dépôt actuel :")
    run("git status")
    ask_git_identity()
    selection = affiche_et_choisis_fichiers()
    run("git add " + " ".join(f'"{f}"' for f in selection))
    print("\nVérification : voici les fichiers prêts à être commités :")
    run("git status")
    msg = input("\nMessage de commit (laisse vide pour 'MAJ auto admin') :\n> ").strip()
    if not msg:
        msg = "MAJ auto admin"
    run(f'git commit -m "{msg}"')

    # Proposer de tagger le commit
    tag = input("\nAjouter un tag à ce commit ? (nom du tag, vide pour ignorer) :\n> ").strip()
    if tag:
        run(f'git tag {tag}')

    print("\nPUSH vers Framagit...")
    run("git pull --rebase frama main")
    run("git push frama main")
    if tag:
        run(f"git push frama {tag}")

    print("\nPUSH vers GitHub...")
    run("git push origin main")
    if tag:
        run(f"git push origin {tag}")

    print("\n✅ Terminé ! Vérifie sur Framagit ET GitHub.")
    print("\nQuelques commandes utiles pour l'admin :")
    print("  git status     # Voir les fichiers modifiés/non suivis")
    print("  git log -n 5   # Voir les 5 derniers commits")
    print("  git remote -v  # Voir les remotes configurés")
    print("  git diff       # Voir les changements non commités")

if __name__ == "__main__":
    main()
