#!/usr/bin/env python3

import subprocess
import sys

def run(cmd, capture_output=False):
    """Run a shell command and print output live or return output."""
    print(f"\n[CMD] {cmd}")
    if capture_output:
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        return result.stdout.strip()
    else:
        result = subprocess.run(cmd, shell=True, text=True)
        if result.returncode != 0:
            print(f"\033[91m[Erreur] La commande a échoué : {cmd}\033[0m")
            sys.exit(result.returncode)

def main():
    print("=== PUSHEUR GIT Framagit & GitHub ===")
    print("État du dépôt actuel :")
    run("git status")

    files = input("\nEntrer le/les dossier(s) ou fichier(s) à ajouter (séparés par un espace)\n(tape * pour tout ajouter) :\n> ").strip()

    if files == "*" or files == "":
        # 1. Affiche la liste des fichiers qui vont être ajoutés (modifs + nouveaux)
        print("\nFichiers modifiés/supprimés :")
        modifs = run("git ls-files -m -d", capture_output=True)
        print(modifs if modifs else "[Aucun]")

        print("\nNouveaux fichiers non suivis :")
        news = run("git ls-files --others --exclude-standard", capture_output=True)
        print(news if news else "[Aucun]")

        # 2. Demande confirmation avant d’ajouter tout
        choix = input("\nAjouter TOUS ces fichiers ? (o/n) : ").lower()
        if choix != "o":
            print("Ajout annulé.")
            sys.exit(0)

        run("git add -u")
        run("git add .")
    else:
        run(f"git add {files}")

    print("\nVérification : voici les fichiers prêts à être commités :")
    run("git status")

    msg = input("\nMessage de commit (laisse vide pour 'MAJ auto admin') :\n> ").strip()
    if not msg:
        msg = "MAJ auto admin"

    run(f'git commit -m "{msg}"')

    print("\nPUSH vers Framagit...")
    run("git push frama main")

    print("\nPUSH vers GitHub...")
    run("git push origin main")

    print("\n✅ Terminé ! Vérifie sur Framagit ET GitHub.")

    print("\nQuelques commandes utiles pour l'admin :")
    print("  git status     # Voir les fichiers modifiés/non suivis")
    print("  git log -n 5   # Voir les 5 derniers commits")
    print("  git remote -v  # Voir les remotes configurés")
    print("  git diff       # Voir les changements non commités")

if __name__ == "__main__":
    main()
