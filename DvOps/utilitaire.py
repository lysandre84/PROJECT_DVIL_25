#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import shlex
import os

def print_color(msg, color=""):
    colors = {
        "red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m",
        "blue": "\033[94m", "cyan": "\033[96m", "reset": "\033[0m"
    }
    if color and color in colors:
        print(colors[color] + msg + colors["reset"])
    else:
        print(msg)

def run(cmd):
    """Run a shell command and print output live."""
    print_color(f"\n[CMD] {cmd}", "blue")
    result = subprocess.run(cmd, shell=True, text=True)
    if result.returncode != 0:
        print_color(f"[Erreur] La commande a échoué : {cmd}", "red")
        sys.exit(result.returncode)

def get_repo_root():
    result = subprocess.run("git rev-parse --show-toplevel", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print_color("Impossible de trouver la racine du dépôt git.", "red")
        sys.exit(1)
    return result.stdout.strip()

def get_modified_files():
    """Liste tous les fichiers modifiés ou non suivis (robuste, même .gitignore)."""
    result = subprocess.run("git status --porcelain -z", shell=True, capture_output=True, text=True)
    items = result.stdout.split('\0')
    files = []
    for item in items:
        if not item.strip():
            continue
        path = item[3:]
        files.append(path)
    return files

def main():
    # Se placer dans la racine du dépôt
    repo_root = get_repo_root()
    os.chdir(repo_root)

    print_color("=== 🚀 PUSHEUR GIT Framagit & GitHub ===", "cyan")
    print_color("État du dépôt actuel :", "yellow")
    run("git status")

    files = get_modified_files()
    if not files:
        print_color("Aucun fichier modifié ou non suivi à ajouter. Rien à faire !", "yellow")
        return

    print_color("\nFichiers modifiés / non suivis à ajouter :", "cyan")
    for i, f in enumerate(files, 1):
        print(f"  {i:>2}. {f}")

    print_color("\nTout ajouter ? (o/N) ou liste les fichiers séparés par espace ou numéros pour n’en ajouter qu’une partie", "yellow")
    choix = input("> ").strip().lower()
    if choix in ["o", "oui", "y", "yes"]:
        files_to_add = files
    elif choix == "" or choix == "n" or choix == "non":
        print_color("Annulé. Aucun fichier n’a été ajouté.", "red")
        return
    else:
        choix_indices = [x.strip() for x in choix.split()]
        files_to_add = []
        for ch in choix_indices:
            if ch.isdigit() and 1 <= int(ch) <= len(files):
                files_to_add.append(files[int(ch)-1])
            elif ch in files:
                files_to_add.append(ch)
            else:
                print_color(f"⚠️  Fichier ou numéro inconnu : {ch}", "red")
        if not files_to_add:
            print_color("Aucun fichier reconnu. Arrêt.", "red")
            return

    print_color("\nFichiers qui vont être ajoutés :", "green")
    print(" ".join(f'"{f}"' for f in files_to_add))
    print_color("\nConfirmer l’ajout ? (O/n) :", "yellow")
    conf = input("> ").strip().lower()
    if conf not in ["", "o", "oui", "y", "yes"]:
        print_color("Annulé. Rien n’est ajouté.", "red")
        return

    files_str = " ".join(shlex.quote(f) for f in files_to_add)
    run(f"git add {files_str}")

    print_color("\nVérification : voici les fichiers prêts à être commités :", "cyan")
    run("git status")

    msg = input("\nMessage de commit (laisse vide pour 'MAJ auto admin') :\n> ").strip()
    if not msg:
        msg = "MAJ auto admin"
    run(f'git commit -m "{msg}"')

    print_color("\nPUSH vers Framagit...", "yellow")
    run("git pull --rebase frama main")
    run("git push frama main")

    print_color("\nPUSH vers GitHub...", "yellow")
    run("git pull --rebase origin main")
    run("git push origin main")

    print_color("\n✅ Terminé ! Vérifie sur Framagit ET GitHub.", "green")

    print_color("\nQuelques commandes utiles pour l'admin :", "cyan")
    print("  git status     # Voir les fichiers modifiés/non suivis")
    print("  git log -n 5   # Voir les 5 derniers commits")
    print("  git remote -v  # Voir les remotes configurés")
    print("  git diff       # Voir les changements non commités")

if __name__ == "__main__":
    main()
