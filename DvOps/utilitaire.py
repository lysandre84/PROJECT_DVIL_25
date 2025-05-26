#!/usr/bin/env python3



import subprocess
import sys

def run(cmd):
    """Run a shell command and print output live."""
    print(f"\n[CMD] {cmd}")
    result = subprocess.run(cmd, shell=True, text=True)
    if result.returncode != 0:
        print(f"\033[91m[Erreur] La commande a échoué : {cmd}\033[0m")
        sys.exit(result.returncode)

def main():
    print("=== PUSHEUR GIT Framagit & GitHub ===")
    print("État du dépôt actuel :")
    run("git status")

    files = input("\nEntrer le/les dossier(s) ou fichier(s) à ajouter (séparés par un espace) :\n> ").strip()
    if not files:
        print("Aucun fichier/dossier indiqué. Arrêt.")
        return

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
