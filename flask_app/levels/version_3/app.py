#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================
#    
#   $$$$$$$\  $$\    $$\ $$$$$$\ $$\             $$\    $$\  $$$$$$\  
#   $$  __$$\ $$ |   $$ |\_$$  _|$$ |            $$ |   $$ |$$ ___$$\ 
#   $$ |  $$ |$$ |   $$ |  $$ |  $$ |            $$ |   $$ |\_/   $$ |
#   $$ |  $$ |\$$\  $$  |  $$ |  $$ |            \$$\  $$  |  $$$$$ / 
#   $$ |  $$ | \$$\$$  /   $$ |  $$ |             \$$\$$  /   \___$$\ 
#   $$ |  $$ |  \$$$  /    $$ |  $$ |              \$$$  /  $$\   $$ |
#   $$$$$$$  |   \$  /   $$$$$$\ $$$$$$$$\          \$  /   \$$$$$$  |
#   \_______/     \_/    \______|\________|          \_/     \______/ 
#
# ================================================================================
__version__ = "1.0.0"  # DVIL Secure // Version sécurisée (Trois vulnérabilitées).
# Auteur   : Lysius [VIALETTE Lysandre]
# Date     : 15/03/2025
# Description : API RESTful sécurisée destinée à l'apprentissage.
#               Les endpoints sensibles (authentification, contrôle de la serrure,
#               gestion des utilisateurs, etc.) sont protégés par des décorateurs et
#               des vérifications rigoureuses. L'endpoint vulnérable de déverrouillage
#               public a été supprimé.
#
# "Hack the planet, secure the future!"
# -------------------------------------------------------------------------------------
#   DVIL SYSTEM - Plateforme d’apprentissage, API RESTful
#   Version sécurisée SANS challenge vulnérable
#   Auteur : Lysius [VIALETTE Lysandre]
# -------------------------------------------------------------------------------------

# Import des bibliothèques système et tierces nécessaires
import os                # Gestion des chemins, dossiers et variables d'environnement
import logging           # Gestion des logs et fichiers de logs
import json              # Encodage/décodage JSON
import datetime          # Gestion des dates et heures
import threading         # Exécution simultanée (logs, MQTT)
import time              # Fonctions temporelles (sleep, pause)
import jwt               # Gestion des tokens JWT (authentification)
import paho.mqtt.client as mqtt   # Client MQTT pour messages IoT
import redis             # Client Redis (stockage temporaire)
import secrets           # Génération sécurisée de secrets (PIN, etc)
from functools import wraps   # Pour créer des décorateurs

# Import des modules Flask et extensions
from flask import (
    Flask, request, jsonify, render_template,
    render_template_string, make_response, redirect,
    url_for, session
)
from flask_sqlalchemy import SQLAlchemy     # ORM SQL pour les modèles BDD
from flask_migrate import Migrate           # Migration BDD
from flask_bcrypt import Bcrypt             # Hash sécurisé des mots de passe
from flask_socketio import SocketIO         # WebSocket pour logs temps réel
from dotenv import load_dotenv              # Variables d'environnement .env
from flask_limiter import Limiter           # Limitation du débit API (rate limit)
from flask_limiter.util import get_remote_address
from flask_login import LoginManager, UserMixin, current_user    # Auth utilisateur
from flask_talisman import Talisman         # Sécurité HTTP (headers CSP, ...)
from sqlalchemy import text                 # Requêtes SQL brutes

# -------------------- Initialisation des dossiers de logs --------------------
load_dotenv()  # Charge les variables d'environnement depuis .env

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Chemin de base du projet
LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")  # Dossier logs

# Crée le dossier logs s'il n'existe pas
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Dictionnaire des fichiers de logs utilisés dans l'appli
LOG_FILES = {
    "SERVEUR":    "serveur.log",
    "Clavier-I²C": "clavier.log",
    "INFO-CLAVIER": "keypad_raw.log",
    "NFC":        "nfc.log",
    "API":        "api.log",
    "API-challenge": os.path.join(LOGS_DIR, "challenge.log")
}

os.makedirs(LOGS_DIR, exist_ok=True)  # Crée (ou recrée) le dossier logs si jamais absent

def create_logger(name, file, level=logging.INFO, fmt=None):
    # Crée un logger dédié à un fichier spécifique avec un format personnalisé
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        fhandler = logging.FileHandler(file)
        formatter = logging.Formatter(fmt or '%(asctime)s [%(levelname)s] %(message)s')
        fhandler.setFormatter(formatter)
        logger.addHandler(fhandler)
        logger.setLevel(level)
    return logger

# Instancie tous les loggers nécessaires avec leurs formats
serveur_logger    = create_logger("serveur",      os.path.join(LOGS_DIR, "serveur.log"),    fmt='%(asctime)s [SERVEUR] %(message)s')
clavier_logger    = create_logger("clavier",      os.path.join(LOGS_DIR, "clavier.log"),    fmt='%(asctime)s [Clavier-I²C] %(message)s')
info_clavier_logger = create_logger("info_clavier",os.path.join(LOGS_DIR, "keypad_raw.log"),fmt='%(asctime)s [INFO-CLAVIER] %(message)s')
nfc_logger        = create_logger("nfc",          os.path.join(LOGS_DIR, "nfc.log"),        fmt='%(asctime)s [NFC] %(message)s')
api_logger        = create_logger("api",          os.path.join(LOGS_DIR, "api.log"),        fmt='%(asctime)s [API] %(message)s')
main_logger       = create_logger("main",         os.path.join(BASE_DIR,  "serrure.log"))

def ensure_logs_exist():
    # Vérifie et crée les fichiers de logs s'ils sont absents
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR, exist_ok=True)
    for fname in LOG_FILES.values():
        fpath = os.path.join(LOGS_DIR, fname)
        if not os.path.exists(fpath):
            open(fpath, "a", encoding="utf-8").close()

def ensure_log_file(log_path):
    # Créé le fichier de log si absent (chemin complet)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    if not os.path.exists(log_path):
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("")

def log_all(message, logger_list):
    # Logge un message dans tous les loggers fournis
    for lg in logger_list:
        lg.info(message)

# -------------------- Flask & Extensions ----------------
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

# Active les protections HTTP en production
if os.getenv("FLASK_ENV") == "production":
    Talisman(app)

# Configuration des clés et de la BDD
SECRET_KEY = os.getenv("SECRET_KEY", "secretkey")
app.config['SECRET_KEY'] = SECRET_KEY

DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_USER     = os.getenv("DB_USER", "Ad_@min")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Admin")
DB_NAME     = os.getenv("DB_NAME", "dvil_db")
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation des modules Flask extensions
db = SQLAlchemy(app)         # ORM SQLAlchemy
migrate = Migrate(app, db)   # Outil de migration de schéma
bcrypt = Bcrypt(app)         # Pour hash des mots de passe
socketio = SocketIO(app, cors_allowed_origins="*")  # Websocket pour logs temps réel

# -------------------- Limiter -----------------
try:
    redis_client = redis.StrictRedis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0)
    redis_client.ping()
    limiter_storage = "redis://localhost:6379"
except redis.ConnectionError:
    serveur_logger.warning("⚠️ Redis non accessible, fallback mémoire.")
    redis_client = None
    limiter_storage = "memory://"

# Limiteur d'accès API (rate limit)
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    storage_uri=limiter_storage,
    default_limits=["10000 per hour"]
)

# ------------------- Flask-Login ---------------
login_manager = LoginManager(app)
login_manager.login_view = "login_page"

@login_manager.user_loader
def load_user(user_id):
    # Charge un utilisateur depuis la BDD (par id) pour la session Flask-Login
    return User.query.get(int(user_id))

# -------------------- Modèles DB --------------
class User(UserMixin, db.Model):
    # Table des utilisateurs, héritée de Flask-Login UserMixin pour la gestion de session
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    pin_code = db.Column(db.String(10), nullable=True)
    nfc_code = db.Column(db.String(32), nullable=True)
    tag = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    role = db.Column(db.String(20), default="user")
    mfa_secret = db.Column(db.String(16), unique=True, nullable=True)

class SerrureState(db.Model):
    # Table qui enregistre l'état de la serrure (verrouillée/déverrouillée)
    __tablename__ = 'serrure_state'
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(10), nullable=False)

class Comment(db.Model):
    # Table des commentaires utilisateurs (non utilisée ici mais structure prête)
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

with app.app_context():
    db.create_all()  # Créé les tables si besoin (développement)

# -------------- Authentification et décorateurs de protection --------------
def verify_token_cookie():
    # Vérifie et décode le token JWT stocké dans le cookie utilisateur
    token = request.cookies.get("jwt_token")
    if not token:
        return None
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def require_auth(f):
    # Décorateur : oblige l’utilisateur à être authentifié (JWT valide)
    @wraps(f)
    def decorated(*args, **kwargs):
        payload = verify_token_cookie()
        if not payload:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated

def require_admin(f):
    # Décorateur : oblige à être admin (vérifie le rôle dans le token puis la BDD)
    @wraps(f)
    def decorated(*args, **kwargs):
        payload = verify_token_cookie()
        if not payload:
            return redirect(url_for('login_page'))
        user = User.query.filter_by(username=payload.get("username")).first()
        if not user or user.role != "admin":
            return jsonify({"error": "Accès refusé (admin seulement)."}), 403
        return f(*args, **kwargs)
    return decorated

def require_user_or_admin(f):
    # Décorateur : accès à tout utilisateur authentifié OU admin
    @wraps(f)
    def decorated(*args, **kwargs):
        payload = verify_token_cookie()
        if not payload:
            return redirect(url_for('login_page'))
        user = User.query.filter_by(username=payload.get("username")).first()
        if not user:
            return jsonify({"error": "Utilisateur introuvable"}), 404
        if user.role not in ["user", "admin"]:
            return jsonify({"error": "Accès refusé (user ou admin uniquement)."}), 403
        return f(*args, **kwargs)
    return decorated

API_KEY = os.getenv("API_KEY", "secret")
def require_api_key(f):
    # Décorateur : accès restreint via clé API dans l'en-tête HTTP (sécurité inter-app)
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.headers.get("X-Api-Key") != API_KEY:
            return jsonify({"error": "Clé API invalide"}), 401
        return f(*args, **kwargs)
    return decorated

# ---------------------- Configuration MQTT ---------------------
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC_LOCK = "DVIL/Serrure"   # Topic pour verrouillage
MQTT_TOPIC_UNLOCK = "DVIL/Serrure" # Topic pour déverrouillage
MQTT_TOPIC_STATUS = "DVIL/Status"  # Topic statut de la serrure

mqtt_client = mqtt.Client()  # Création du client MQTT
mqtt_client.username_pw_set("admin", "admin")  # Authentification broker (ici valeurs par défaut)
lock_state = {"locked": True}  # Dictionnaire qui maintient l’état actuel de la serrure
last_status_logged = None      # Pour logger les changements de statut uniquement

def on_connect(client, userdata, flags, rc):
    # Callback lors de la connexion au broker MQTT
    if rc == 0:
        serveur_logger.info("[MQTT] Connecté au broker")
        client.subscribe(MQTT_TOPIC_UNLOCK)
    else:
        serveur_logger.error(f"[MQTT] Échec de connexion, code={rc}")

def on_message(client, userdata, msg):
    # Callback lors de la réception d’un message sur les topics MQTT suivis
    global lock_state
    if msg.topic == MQTT_TOPIC_UNLOCK:
        payload_str = msg.payload.decode()
        if payload_str == "deverouillage":
            lock_state["locked"] = False
        elif payload_str == "fermeture":
            lock_state["locked"] = True
        serveur_logger.info(f"[MQTT] Serrure => locked={lock_state['locked']}")

# Association des callbacks à l’instance du client MQTT
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def mqtt_loop():
    # Lance la boucle MQTT dans un thread séparé pour écouter en permanence
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_forever()

# Démarre le thread MQTT (daemon = fond)
threading.Thread(target=mqtt_loop, daemon=True).start()

# ------------------ Socket.IO logs en temps réel -----------------
def tail_logs():
    # Stream les logs serrure.log en temps réel via WebSocket pour affichage dynamique
    try:
        with open(os.path.join(BASE_DIR, "serrure.log"), "r") as f:
            f.seek(0, 2)  # Va à la fin du fichier
            while True:
                line = f.readline()
                if line:
                    socketio.emit("log_update", {"log": line.strip()})
                else:
                    time.sleep(0.5)
    except Exception as e:
        print(f"[TAIL_LOGS] ERREUR: {e}")

# Lance le thread pour le streaming de logs en temps réel (daemon)
threading.Thread(target=tail_logs, daemon=True).start()

@app.after_request
def security_headers(response):
    # Ajoute des headers HTTP de sécurité à chaque réponse (anti XSS et sniffing)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

# ========== ROUTES PRINCIPALES (Accueil, login, logout, etc.) ==========

@app.route("/")
def home():
    # Affiche la page d'accueil (index.html)
    return render_template("index.html")

@app.route("/accueil")
@require_auth
def accueil():
    # Page d'accueil utilisateur après connexion (protégée)
    payload = verify_token_cookie()
    return render_template("accueil.html", username=payload["username"])

@app.route("/login", methods=["GET"])
def login_page():
    # Affiche la page de connexion
    return render_template("login.html")

@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")  # Limite les tentatives à 5 par minute (protection brute force)
def login():
    # Authentifie l'utilisateur (JSON ou formulaire)
    auth = request.json if request.is_json else request.form
    username = auth.get("username")
    password = auth.get("password")
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        api_logger.info(f"LOGIN de {username} réussi")
        exp = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        token = jwt.encode({"username": username, "exp": int(exp.timestamp()) + 7200}, SECRET_KEY, algorithm="HS256")
        response = jsonify({"redirect": "/accueil"})
        response.set_cookie("jwt_token", token, httponly=True, secure=False, samesite="Lax")
        return response
    else:
        api_logger.warning(f"Tentative login échouée pour {username}")
        return jsonify({"error": "Identifiants incorrects."}), 401

@app.route("/logout", methods=["POST"])
def logout():
    # Déconnecte l'utilisateur (supprime le cookie JWT)
    resp = make_response(redirect(url_for("login_page")))
    resp.set_cookie("jwt_token", "", expires=0)
    return resp

@app.route("/verify_pin", methods=["POST"])
def verify_pin():
    # Vérifie le code PIN du clavier pour déverrouiller la serrure
    data = request.get_json(force=True)
    pin = data.get("pin_code", "")
    user = User.query.filter_by(pin_code=pin).first()

    info_clavier_logger.info(f"[KEYPAD_RAW] {pin}")

    if user:
        # Si le code PIN est correct, publie l'événement MQTT pour déverrouiller
        mqtt_client.publish("DVIL/Serrure", "deverouillage")
        mqtt_client.publish("DVIL/Clavier", "deverouillage")
        clavier_logger.info(f"[OUVERTURE] par {user.username} (id={user.id}, pin_code={pin})")
        api_logger.info(f"[API] UNLOCK par {user.username} (id={user.id}, role={user.role}) : Déverrouillage par clavier")
        return jsonify({
            "authorized": True,
            "username": user.username,
            "user_id": user.id,
            "role": user.role
        })
    else:
        info_clavier_logger.warning(f"[KEYPAD_RAW] PIN incorrect : {pin}")
        api_logger.warning(f"[API] Echec ouverture clavier avec code: {pin}")
        return jsonify({"authorized": False})

@app.route("/verify_nfc", methods=["POST"])
def verify_nfc():
    # Vérifie le badge NFC pour déverrouiller la serrure
    data = request.get_json(force=True)
    nfc_uid = data.get("nfc_code", "").strip()
    user = User.query.filter_by(nfc_code=nfc_uid).first()
    nfc_logger.info(f"{nfc_uid}")
    if user:
        nfc_logger.info(f"Déverrouillage badge par {user.username} (id={user.id}, nfc_code={nfc_uid})")
        mqtt_client.publish("DVIL/Serrure", "deverouillage")
        return jsonify({
            "authorized": True,
            "username": user.username,
            "user_id": user.id,
            "role": user.role
        })
    else:
        nfc_logger.warning(f"Echec badge inconnu : {nfc_uid}")
        return jsonify({"authorized": False})

@app.route("/user/status", methods=["GET"])
@require_auth
def user_status():
    # Renvoie le statut de l'utilisateur connecté (nom et rôle)
    payload = verify_token_cookie()
    user = User.query.filter_by(username=payload["username"]).first()
    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404
    return jsonify({"username": user.username, "role": user.role}), 200

@app.route("/status", methods=["GET"])
@require_auth
def get_status():
    # Renvoie l'état actuel de la serrure (verrouillée/déverrouillée)
    global last_status_logged
    status = "verrouillée" if lock_state["locked"] else "déverrouillée"

    if last_status_logged != status:
        serveur_logger.info(f"Status consulté ({status})")
        last_status_logged = status

    return jsonify({"status": status})

@app.route("/unlock", methods=["POST"])
@require_auth
@require_user_or_admin
def unlock():
    # Déverrouille la serrure via API, MQTT et met à jour l'état global
    try:
        mqtt_client.publish(MQTT_TOPIC_UNLOCK, "deverouillage")
        lock_state["locked"] = False
        serveur_logger.info("Déverrouillage par API")
        return jsonify({"status": "success", "message": "Serrure déverrouillée."})
    except Exception as e:
        serveur_logger.error(f"Erreur lors de la publication MQTT (unlock): {e}")
        return jsonify({"status": "fail", "message": "Erreur lors de l'envoi de la commande MQTT."}), 500

@app.route("/lock", methods=["POST"])
@require_auth
@require_user_or_admin
def lock():
    # Verrouille la serrure via API, MQTT et met à jour l'état global
    try:
        mqtt_client.publish(MQTT_TOPIC_LOCK, "fermeture")
        lock_state["locked"] = True
        serveur_logger.info("Verrouillage par API")
        return jsonify({"status": "success", "message": "Serrure verrouillée."})
    except Exception as e:
        serveur_logger.error(f"Erreur lors de la publication MQTT (lock): {e}")
        return jsonify({"status": "fail", "message": "Erreur lors de l'envoi de la commande MQTT."}), 500

# --- ADMIN PANEL et LOGS ---

@app.route("/admin")
@require_auth
@require_admin
def admin_panel():
    # Affiche le panneau d'administration principal
    return render_template("admin.html")

@app.route("/admin/users")
@require_auth
@require_admin
def admin_users():
    # Affiche la gestion des utilisateurs pour l'admin
    users = User.query.all()
    return render_template("admin_users.html", users=users)

@app.route("/admin/logs")
@require_auth
@require_admin
def admin_ulogs():
    # Affiche les logs principaux dans le panneau d'admin
    
    LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(LOGS_DIR, exist_ok=True)

    log_files = {
        "SERVEUR":         os.path.join(LOGS_DIR, "serveur.log"),
        "Clavier-I²C":     os.path.join(LOGS_DIR, "clavier.log"),
        "INFO-CLAVIER":    os.path.join(LOGS_DIR, "keypad_raw.log"),
        "NFC":             os.path.join(LOGS_DIR, "nfc.log"),
        "API":             os.path.join(LOGS_DIR, "api.log"),
        "API-challenge":   os.path.join(LOGS_DIR, "challenge.log"),
    }
    logs_by_type = {}
    for logtype, path in log_files.items():
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                pass
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()[-300:]
                logs_by_type[logtype] = lines
        except Exception as e:
            logs_by_type[logtype] = [f"[ERROR] Impossible de lire ce log : {e}\n"]
    return render_template("admin_logs.html", logs_by_type=logs_by_type)

@app.route("/admin/log_raw")
@require_auth
@require_admin
def admin_log_raw():
    # Renvoie les logs bruts sous forme de liste pour affichage dynamique
    
    LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")
    log_files = [
        ("SERVEUR",     os.path.join(LOGS_DIR, "serveur.log")),
        ("Clavier-I²C", os.path.join(LOGS_DIR, "clavier.log")),
        ("INFO-CLAVIER",os.path.join(LOGS_DIR, "keypad_raw.log")),
        ("NFC",         os.path.join(LOGS_DIR, "nfc.log")),
        ("API",         os.path.join(LOGS_DIR, "api.log")),
    ]
    logs = []
    for cat, path in log_files:
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                pass
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()[-200:]
                logs += [[cat, l.strip()] for l in lines]
        except Exception as e:
            logs.append([cat, f"[ERROR] Erreur lecture log: {e}"])
    return {"logs": logs}

@app.route("/admin/logs/filter")
@require_auth
@require_admin
def filter_logs():
    log_type = request.args.get("type")
    log_files = {
        "SERVEUR":      os.path.join(LOGS_DIR, "serveur.log"),
        "Clavier-I²C":  os.path.join(LOGS_DIR, "clavier.log"),
        "INFO-CLAVIER": os.path.join(LOGS_DIR, "keypad_raw.log"),
        "NFC":          os.path.join(LOGS_DIR, "nfc.log"),
        "API":          os.path.join(LOGS_DIR, "api.log"),
        "API-challenge":os.path.join(LOGS_DIR, "challenge.log"),
    }
    path = log_files.get(log_type)
    if not path or not os.path.exists(path):
        return {"lines": [], "error": f"Erreur lecture log : [Errno 2] No such file or directory: '{path}'"}
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()[-200:]
        return {"lines": [l.strip() for l in lines]}
    except Exception as e:
        return {"lines": [], "error": f"Erreur lecture log : {e}"}


@app.route("/admin/reset_logs", methods=["POST"])
@require_auth
@require_admin
def admin_reset_logs():
    # Vide tous les fichiers de logs depuis l’admin
    import os
    LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")
    log_files = [
        "serveur.log",
        "clavier.log",
        "keypad_raw.log",
        "nfc.log",
        "api.log",
        "challenge.log",
    ]
    errors = []
    for fname in log_files:
        path = os.path.join(LOGS_DIR, fname)
        try:
            with open(path, "w", encoding="utf-8"):
                pass  # Vide le fichier
        except Exception as e:
            errors.append(f"{fname}: {e}")
    if errors:
        return {"success": False, "errors": errors}, 500
    return {"success": True, "message": "Tous les logs ont été réinitialisés."}

@app.route("/admin/users/add", methods=["POST"])
@require_auth
@require_admin
def add_user():
    # Ajoute un nouvel utilisateur (génère pin et nfc par défaut)
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')
    if not username or not password:
        return jsonify({"error": "username et password requis"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Utilisateur déjà existant"}), 409
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    default_pin = "{:04d}".format(secrets.randbelow(10000))
    default_nfc = secrets.token_hex(8)
    new_user = User(
        username=username,
        password=hashed,
        role=role,
        pin_code=default_pin,
        nfc_code=default_nfc
    )
    db.session.add(new_user)
    db.session.commit()
    serveur_logger.info(f"[ADMIN] Ajout user={username} role={role} pin={default_pin} nfc={default_nfc}")
    return jsonify({
        "message": "OK",
        "pin_code": default_pin,
        "nfc_code": default_nfc
    }), 201

@app.route("/admin/users/update", methods=["PUT"])
@require_auth
@require_admin
def update_user():
    # Met à jour le rôle ou le mot de passe d’un utilisateur existant
    data = request.json
    user_id = data.get('user_id')
    new_role = data.get('role')
    new_password = data.get('password')
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Inexistant"}), 404
    if new_role:
        user.role = new_role
    if new_password:
        user.password = bcrypt.generate_password_hash(new_password).decode("utf-8")
    db.session.commit()
    serveur_logger.info(f"[ADMIN] Update user_id={user_id}")
    return jsonify({"message": "Mise à jour OK"}), 200

@app.route("/admin/users/delete", methods=["DELETE"])
@require_auth
@require_admin
def delete_user():
    # Supprime un utilisateur de la base
    data = request.json
    user_id = data.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Inexistant"}), 404
    db.session.delete(user)
    db.session.commit()
    serveur_logger.info(f"[ADMIN] Delete user_id={user_id}")
    return jsonify({"message": "Utilisateur supprimé"}), 200

@app.route("/admin/update_field", methods=["POST"])
def admin_update_field():
    # Permet de modifier en direct un champ utilisateur (PIN, NFC ou tag)
    if not request.is_json:
        return jsonify({"status": "error", "error": "Requête invalide"}), 400
    data = request.get_json()
    user_id = data.get("user_id")
    field = data.get("field")
    value = data.get("value")
    if not user_id or field not in ("pin_code", "nfc_code", "tag"):
        return jsonify({"status": "error", "error": "Champs non valides"}), 400
    user = User.query.get(user_id)
    if not user:
        return jsonify({"status": "error", "error": "Utilisateur introuvable"}), 404
    setattr(user, field, value)
    try:
        db.session.commit()
        serveur_logger.info(f"[ADMIN] Modification {field} pour user_id={user_id} : {value}")
        return jsonify({"status": "ok"})
    except Exception as e:
        db.session.rollback()
        serveur_logger.error(f"[ADMIN] Erreur modification {field} pour user_id={user_id} : {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

# --- LOGS RAW CLAVIER ET NFC (pour apps embarquées) ---

@app.route("/api/log_keypad_raw", methods=["POST"])
def log_keypad_raw():
    # Ajoute une entrée brute dans le log clavier (pour monitoring)
    data = request.get_json(force=True)
    code = data.get("raw", "")
    info_clavier_logger.info(f"{code}")
    return jsonify({"status": "ok"})

@app.route("/api/log_event", methods=["POST"])
@require_api_key
def log_event():
    # Journalise un évènement spécifique côté API avec tous les détails
    data = request.get_json(force=True)
    event = data.get("event")
    pin_code = data.get("pin_code")
    details = data.get("details", "")
    username = "anonyme"
    user_id = None
    user_role = None
    status = "fail"
    if event == "KEYPAD_UNLOCK" and pin_code and len(pin_code) == 4 and pin_code.isdigit():
        user = User.query.filter_by(pin_code=pin_code).first()
        if user:
            username = user.username
            user_id = user.id
            user_role = user.role
            details = f"Déverrouillage via clavier (PIN: {pin_code})"
            status = "success"
        else:
            details = f"Échec déverrouillage clavier : PIN inconnu ({pin_code})"
        log_all(
            f"{event} par {username} (id={user_id}, role={user_role}) : {details}",
            [api_logger, clavier_logger, main_logger]
        )
    return jsonify({
        "status": status,
        "user": username,
        "user_id": user_id,
        "role": user_role,
        "details": details
    }), 200 if status == "success" else 401

# ---------------------------
# CHALLENGE PEDAGOGIQUE
# ---------------------------

@app.route("/admin/reset_challenge", methods=["POST"])
@require_auth
@require_admin
def reset_challenge_10s():
    # Réinitialise l'environnement CTF/challenge après 10 secondes
    logging.info("=== Début de reset_challenge_10s() ===")
    time.sleep(10)
    global OVERRIDE_TOKEN
    OVERRIDE_TOKEN = None
    with app.app_context():
        db.session.execute(text("UPDATE serrure_state SET state = 'lock' WHERE id = 1"))
        db.session.commit()
    lock_state["locked"] = True
    logging.info("Environnement challenge réinitialisé (10s) pour le prochain étudiant.")
    return {"message": "Challenge réinitialisé !"}, 200

# Endpoint volontairement vulnérable SSTI pour la pédagogie
@app.route("/vuln/template")
def vuln_template():
    # Démontre la vulnérabilité Server Side Template Injection
    user_input = request.args.get("q", "")
    return render_template_string(user_input, open=open)

# Endpoint volontairement vulnérable (injection pickle)
@app.route("/vuln/deserialize", methods=["POST"])
def vuln_deserialize():
    import pickle
    global OVERRIDE_TOKEN
    try:
        obj = pickle.loads(request.data)
        if isinstance(obj, dict) and "set_token" in obj:
            OVERRIDE_TOKEN = obj["set_token"]
        return "Objet désérialisé: " + str(obj)
    except Exception as e:
        return str(e), 400

# Endpoint vulnérable SQLi pour CTF
@app.route("/vuln/serrure", methods=["POST"])
def vuln_serrure():
    token = request.args.get("token")
    update_value = request.args.get("update")
    correct_token = app.config.get("SECRET_KEY")
    if OVERRIDE_TOKEN:
        correct_token = OVERRIDE_TOKEN

    if token != correct_token:
        return "Accès non autorisé", 403

    # INJECTION SQL VOLONTAIRE (danger : ne pas faire en prod réelle)
    query = f"UPDATE serrure_state SET state = '{update_value}' WHERE id = 1"

    try:
        state_entry = SerrureState.query.get(1)
        if not state_entry:
            state_entry = SerrureState(id=1, state="lock")
            db.session.add(state_entry)
            db.session.commit()
        db.session.execute(text(query))
        db.session.commit()
        clean_value = update_value.split("'")[0]
        # Action MQTT
        if "unlock" in clean_value.lower():
            mqtt_client.publish(MQTT_TOPIC_UNLOCK, "deverouillage")
        elif "lock" in clean_value.lower():
            mqtt_client.publish(MQTT_TOPIC_LOCK, "Mauvaise manipe")
        # Thread reset
        logging.info("Lancement du thread de reset dans 10s...")
        threading.Thread(target=reset_challenge_10s, daemon=True).start()
        return f"Serrure mise à jour avec: {update_value}"
    except Exception as e:
        return str(e), 500

# -------------------------------------------------------------------------------------
# Lancement de l’application (uniquement en mode debug ; avec Gunicorn/WSGI pour prod)
# -------------------------------------------------------------------------------------
# if __name__ == "__main__":
#     socketio.run(app, host="0.0.0.0", port=5000, debug=True)
