import os
from importlib import import_module

# Affiche le niveau en cours de démarrage (variable d'environnement LEVEL)
print(">> Démarrage avec LEVEL =", os.environ.get("LEVEL"))
level = os.environ.get("LEVEL", "0")

try:
    # Importe dynamiquement le module app.py correspondant au niveau choisi
    module = import_module(f"levels.version_{level}.app")
    app = module.app       # L'application Flask principale
    socketio = module.socketio  # Pour Flask-SocketIO si besoin (eventlet/gunicorn)
except (ImportError, AttributeError) as e:
    raise RuntimeError(f"Niveau {level} invalide : {e}")
