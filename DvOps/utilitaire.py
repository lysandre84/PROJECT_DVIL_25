#!/usr/bin/env python3

import subprocess
import sys
import os

def run(cmd, check=True):
    """Run a shell command and print output live. Return completed process."""
    print(f"\n[CMD] {cmd}")
    result = subprocess.run(cmd, shell=True, text=True)
    if check and result.returncode != 0:
        print(f"\033[91m[Erreur] La commande a échoué : {cmd}\033[0m")
        sys.exit(result.returncode)
    return result

def get_git_paths():
    """Retourne la liste des fichiers modifiés ou non suivis, adaptés au cwd."""
    result = subprocess.run(
        "git status --porcelain",
        shell=True, capture_output=True, text=True
    )
    all_paths = []
    cwd = os.getcwd()
    git_root = subprocess.run(
        "git rev-parse --show-toplevel",
        shell=True, capture_output=True, text=True
    ).stdout.strip()
    rel_cwd = os.path.relpath(cwd, git_root)
    for line in result.stdout.splitlines():
        code = line[:2]
        path = line[3:].strip().strip('"').replace("\\", "/")
        # Si on n'est pas à la racine du dépôt, adapte le chemin proposé
        if rel_cwd != "." and path.startswith(rel_cwd + "/"):
            path = path[len(rel_cwd)+1:]
        if path:
            all_paths.append(path)
    return all_paths

def main():
    print("===  PUSHEUR GIT Framagit & GitHub ===")
    print("État du dépôt actuel :")
    run("git status")

    # Afficher les fichiers modifiés / non suivis
    print("\nFichiers modifiés / non suivis à ajouter :")
    all_paths = get_git_paths()
    if not all_paths:
        print("\nAucun fichier modifié ou non suivi à ajouter.\n")
        run("git add")  # Affiche l'aide git add
        print("\nVérification : voici les fichiers prêts à être commités :")
        run("git status")
        msg = input("\nMessage de commit (laisse vide pour 'MAJ auto admin') :\n> ").strip() or "MAJ auto admin"
        run(f'git commit -m "{msg}"')
        sys.exit(0)

    for i, path in enumerate(all_paths, 1):
        print(f"  {i}. {path}")

    print("\nTout ajouter ? (o/N) ou liste les fichiers séparés par espace ou numéros pour n’en ajouter qu’une partie")
    choix = input("> ").strip()
    to_add = []
    if choix.lower() == "o":
        to_add = all_paths
    elif choix.strip() == "":
        print("Aucun fichier/dossier indiqué. Arrêt.")
        return
    else:
        # Accepte soit les chemins, soit les numéros séparés par espace
        parts = choix.split()
        for part in parts:
            if part.isdigit():
                idx = int(part) - 1
                if 0 <= idx < len(all_paths):
                    to_add.append(all_paths[idx])
            else:
                to_add.append(part)

    print("\nFichiers qui vont être ajoutés :")
    print(" ".join(f'"{x}"' for x in to_add))
    confirm = input("\nConfirmer l’ajout ? (O/n) : ").strip().lower()
    if confirm not in ("o", ""):
        print("Ajout annulé.")
        return

    run("git add " + " ".join(f'"{x}"' for x in to_add))

    print("\nVérification : voici les fichiers prêts à être commités :")
    run("git status")

    msg = input("\nMessage de commit (laisse vide pour 'MAJ auto admin') :\n> ").strip()
    if not msg:
        msg = "MAJ auto admin"
    run(f'git commit -m "{msg}"')

    # Option TAG
    tag = input("\nAjouter un tag à ce commit ? (nom du tag, vide pour ignorer) :\n> ").strip()
    if tag:
        # Tag name must not contain brackets, spaces, etc.
        import re
        safe_tag = re.sub(r"[^\w.-]", "_", tag)
        if safe_tag != tag:
            print(f"Nom du tag modifié pour conformité : {safe_tag}")
        run(f"git tag {safe_tag}")

    print("\nPUSH vers Framagit (frama)...")
    # Astuce : pour éviter les rejects, faire un pull --rebase avant push
    run("git pull --rebase frama main", check=False)
    run("git push frama main", check=False)

    print("\nPUSH vers GitHub (origin)...")
    run("git push origin main", check=False)

    print("\n Terminé ! Vérifie sur Framagit ET GitHub.")

    print("\nQuelques commandes utiles pour l'admin :")
    print("  git status     # Voir les fichiers modifiés/non suivis")
    print("  git log -n 5   # Voir les 5 derniers commits")
    print("  git remote -v  # Voir les remotes configurés")
    print("  git diff       # Voir les changements non commités")

if __name__ == "__main__":
    main()
