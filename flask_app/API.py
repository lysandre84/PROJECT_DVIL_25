#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------------
#   
#    /$$$$$$$  /$$    /$$ /$$$$$$ /$$             /$$    /$$  /$$$$$$ 
#   | $$__  $$| $$   | $$|_  $$_/| $$            | $$   | $$ /$$$_  $$
#   | $$  \ $$| $$   | $$  | $$  | $$            | $$   | $$| $$$$\ $$
#   | $$  | $$|  $$ / $$/  | $$  | $$            |  $$ / $$/| $$ $$ $$
#   | $$  | $$ \  $$ $$/   | $$  | $$             \  $$ $$/ | $$\ $$$$
#   | $$  | $$  \  $$$/    | $$  | $$              \  $$$/  | $$ \ $$$
#   | $$$$$$$/   \  $/    /$$$$$$| $$$$$$$$         \  $/   |  $$$$$$/
#   |_______/     \_/    |______/|________/          \_/     \______/ 
#
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# DVIL Secure 1.0 - Version sécurisée de l'API (aucune vulnérabilité intentionnelle)
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

import os                   # Pour interagir avec le système d'exploitation et les variables d'environnement
import logging              # Pour la journalisation des événements
import datetime             # Pour manipuler les dates et gérer les expirations des tokens
import threading            # Pour exécuter des tâches en parallèle (MQTT loop, lecture des logs)
import time                 # Pour gérer les délais et temporisations
import jwt                  # Pour la création et la vérification de JSON Web Tokens (JWT)
import paho.mqtt.client as mqtt  # Pour la communication via MQTT
import redis                # Pour la connexion à Redis (limitation de requêtes)
from functools import wraps # Pour créer des décorateurs réutilisables

# Import des modules Flask et de ses extensions pour construire l'API web
from flask import Flask, request, jsonify, render_template, render_template_string, make_response, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy   # ORM pour interagir avec la base de données
from flask_migrate import Migrate           # Pour gérer les migrations du schéma de la BDD
from flask_bcrypt import Bcrypt             # Pour le hachage sécurisé des mots de passe
from flask_socketio import SocketIO         # Pour la communication en temps réel via WebSocket (logs)
from dotenv import load_dotenv              # Pour charger les variables d'environnement depuis un fichier .env
from flask_limiter import Limiter
from importlib import import_module
           # Pour limiter le nombre de requêtes (anti-DoS)
from flask_limiter.util import get_remote_address  # Pour identifier l'utilisateur par son IP
from flask_login import LoginManager, UserMixin   # Pour la gestion des sessions utilisateur
from flask_talisman import Talisman         # Pour ajouter des headers de sécurité (ex: CSP, HSTS)
from sqlalchemy import text                 # Pour exécuter des requêtes SQL en mode texte brut

# -------------------------------------------------------------------------------------
# CHARGEMENT DES VARIABLES D’ENVIRONNEMENT
# -------------------------------------------------------------------------------------
load_dotenv()  # Charge les variables définies dans le fichier .env

# -------------------------------------------------------------------------------------
# CONFIGURATION DU LOGGING
# -------------------------------------------------------------------------------------
logging.basicConfig(
    filename='serrure.log',                      # Fichier dans lequel seront stockées les entrées de log
    level=logging.INFO,                          # Niveau minimal des logs (INFO ici)
    format='%(asctime)s [%(levelname)s] %(message)s'  # Format des messages de log
)

# -------------------------------------------------------------------------------------
# CRÉATION DE L’APPLICATION FLASK
# -------------------------------------------------------------------------------------
app = Flask(__name__)  # Instanciation de l'application Flask
if os.getenv("FLASK_ENV") == "production":
    Talisman(app)  # Active les headers de sécurité en production via Flask-Talisman

SECRET_KEY = os.getenv("SECRET_KEY", "secretkey")  # Récupère la clé secrète (pour JWT et sessions)
app.config['SECRET_KEY'] = SECRET_KEY  # Stocke la clé secrète dans la configuration de l'application

# -------------------------------------------------------------------------------------
# CONFIGURATION DE LA BASE DE DONNÉES
# -------------------------------------------------------------------------------------
DB_HOST = os.getenv("DB_HOST", "localhost")  # Adresse de la BDD
DB_USER = os.getenv("DB_USER", "Ad_@min")         # Nom d'utilisateur de la BDD
DB_PASSWORD = os.getenv("DB_PASSWORD", "Admin")# Mot de passe de la BDD
DB_NAME = os.getenv("DB_NAME", "dvil_db")        # Nom de la base de données

# Configure la connexion à la BDD via SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optimisation

db = SQLAlchemy(app)         # Initialisation de l'ORM SQLAlchemy
migrate = Migrate(app, db)     # Activation des migrations de schéma
bcrypt = Bcrypt(app)         # Hachage sécurisé des mots de passe

# -------------------------------------------------------------------------------------
# Import Dynamique [LEVELS]
# -------------------------------------------------------------------------------------
level = os.environ.get('LEVEL', '0')
# on importe le module API.py de la version choisie
module = import_module(f'levels.version_{level}.API')
app = module.app
# -------------------------------------------------------------------------------------
# VARIABLE GLOBALE (pour le mode challenge, non utilisée ici)
# -------------------------------------------------------------------------------------
OVERRIDE_TOKEN = None  # Variable globale destinée aux challenges (non utilisée ici)

# -------------------------------------------------------------------------------------
# DÉFINITION DES MODÈLES DE DONNÉES
# -------------------------------------------------------------------------------------
class User(UserMixin, db.Model):
    __tablename__ = 'users'  # Nom de la table
    id       = db.Column(db.Integer, primary_key=True)  # Clé primaire
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)  # Nom d'utilisateur
    password = db.Column(db.String(255), nullable=False)  # Mot de passe haché
    role     = db.Column(db.String(20), default="user")  # Rôle (user/admin)

class SerrureState(db.Model):
    __tablename__ = 'serrure_state'  # Table pour l'état de la serrure
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(10), nullable=False)  # "lock" ou "unlock"

with app.app_context():
    db.create_all()  # Crée les tables si elles n'existent pas

# -------------------------------------------------------------------------------------
# SOCKET.IO (pour les logs en temps réel)
# -------------------------------------------------------------------------------------
socketio = SocketIO(app, cors_allowed_origins="*")

# -------------------------------------------------------------------------------------
# CONFIGURATION DU LIMITATEUR DE REQUÊTES (FLASK-LIMITER)
# -------------------------------------------------------------------------------------
try:
    redis_client = redis.StrictRedis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0)
    redis_client.ping()  # Vérifie la connexion à Redis
    limiter_storage = "redis://localhost:6379"
except redis.ConnectionError:
    logging.warning("⚠️ Redis non accessible, fallback mémoire.")
    redis_client = None
    limiter_storage = "memory://"

limiter = Limiter(
    key_func=get_remote_address,  # Identifie l'utilisateur par son IP
    app=app,
    storage_uri=limiter_storage,
    default_limits=["1000 per hour"]
)

# -------------------------------------------------------------------------------------
# CONFIGURATION DE FLASK-LOGIN
# -------------------------------------------------------------------------------------
login_manager = LoginManager(app)
login_manager.login_view = "login_page"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------------------------------------------------------------------------------------
# DÉFINITION DES DÉCORATEURS JWT
# -------------------------------------------------------------------------------------
def verify_token_cookie():
    """
    Récupère et vérifie le token JWT stocké dans le cookie 'jwt_token'.
    Retourne le payload décodé en cas de succès, sinon None.
    """
    token = request.cookies.get("jwt_token")
    if not token:
        return None
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def require_auth(f):
    """
    Décorateur pour exiger l'authentification via JWT.
    Redirige l'utilisateur vers la page de login si le token est invalide ou absent.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        payload = verify_token_cookie()
        if not payload:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated

def require_admin(f):
    """
    Décorateur pour restreindre l'accès aux utilisateurs administrateurs.
    """
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
    """
    Décorateur pour exiger que l'utilisateur soit authentifié et possède le rôle 'user' ou 'admin'.
    """
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

def login_required(f):
    """
    Décorateur alternatif qui vérifie la présence d'une session authentifiée.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# -------------------------------------------------------------------------------------
# CONFIGURATION DU PROTOCOLE MQTT
# -------------------------------------------------------------------------------------
# Tous les topics MQTT sont désormais définis comme "DVIL/Serrure"
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT   = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC_LOCK   = "DVIL/Serrure"    # Topic pour verrouiller la serrure
MQTT_TOPIC_UNLOCK = "DVIL/Serrure"    # Topic pour déverrouiller la serrure
MQTT_TOPIC_STATUS = "DVIL/Serrure"    # Topic pour le statut de la serrure

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set("PentesterLab", "LysandreLecreateurdelAPI")

def on_connect(client, userdata, flags, rc):
    """
    Callback appelé lors de la connexion au broker MQTT.
    S'abonne au topic de statut.
    """
    if rc == 0:
        logging.info("[MQTT] Connecté au broker")
        client.subscribe(MQTT_TOPIC_STATUS)
    else:
        logging.error(f"[MQTT] Échec de connexion, code={rc}")

def on_message(client, userdata, msg):
    """
    Callback appelé lors de la réception d'un message du broker MQTT.
    Met à jour l'état de la serrure en fonction du message reçu.
    """
    global lock_state
    if msg.topic == MQTT_TOPIC_STATUS:
        lock_state["locked"] = (msg.payload.decode() == "locked")
        logging.info(f"[MQTT] Serrure => locked={lock_state['locked']}")

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def mqtt_loop():
    """
    Se connecte au broker MQTT et démarre la boucle de réception des messages.
    """
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_forever()

threading.Thread(target=mqtt_loop, daemon=True).start()

lock_state = {"locked": True}  # État initial de la serrure : verrouillée

# -------------------------------------------------------------------------------------
# DÉFINITION DES ROUTES DE L'APPLICATION
# -------------------------------------------------------------------------------------
@app.route("/")
def home():
    """
    Affiche la page d'accueil (index.html).
    """
    return render_template("index.html")

@app.route("/accueil")
@require_auth
def accueil():
    """
    Affiche la page d'accueil pour l'utilisateur authentifié.
    Passe le nom d'utilisateur extrait du token JWT.
    """
    payload = verify_token_cookie()
    if not payload:
        return redirect(url_for("login_page"))
    return render_template("accueil.html", username=payload["username"])

# ----------------
# ROUTES POUR L'AUTHENTIFICATION
# ----------------
@app.route("/login", methods=["GET"])
def login_page():
    """
    Affiche la page de connexion (login.html).
    """
    return render_template("login.html")

@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    """
    Authentifie l'utilisateur.
    Vérifie le username et le password, génère un token JWT valable 2 heures,
    et le stocke dans un cookie HTTPOnly.
    """
    auth = request.json if request.is_json else request.form
    username = auth.get("username")
    password = auth.get("password")
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        logging.info(f"[API] Connexion de {username}")
        exp = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        token = jwt.encode({"username": username, "exp": int(exp.timestamp())+ 7200}, SECRET_KEY, algorithm="HS256")
        response = jsonify({"redirect": "/accueil"})
        response.set_cookie("jwt_token", token, httponly=True, secure=False, samesite="Lax")
        return response
    else:
        return jsonify({"error": "Identifiants incorrects."}), 401

@app.route("/logout", methods=["POST"])
def logout():
    """
    Déconnecte l'utilisateur en effaçant le cookie JWT.
    """
    resp = make_response(redirect(url_for("login_page")))
    resp.set_cookie("jwt_token", "", expires=0)
    return resp

@app.route("/user/status", methods=["GET"])
@require_auth
def user_status():
    """
    Retourne les informations de l'utilisateur (username, role).
    """
    payload = verify_token_cookie()
    if not payload:
        return jsonify({"error": "Token invalide"}), 401
    user = User.query.filter_by(username=payload["username"]).first()
    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404
    return jsonify({"username": user.username, "role": user.role}), 200

# ----------------
# ROUTE POUR OBTENIR L'ÉTAT DE LA SERRURE
# ----------------
@app.route("/status", methods=["GET"])
@require_auth
def get_status():
    """
    Retourne l'état actuel de la serrure ("verrouillée" ou "déverrouillée").
    """
    return jsonify({"status": "verrouillée" if lock_state["locked"] else "déverrouillée"})

# ----------------
# ENDPOINTS NORMAUX POUR CONTRÔLER LA SERRURE
# ----------------
@app.route("/unlock", methods=["POST"])
@require_auth
@require_user_or_admin
def unlock():
    """
    Envoie une commande MQTT pour déverrouiller la serrure.
    Met à jour l'état local de la serrure.
    """
    mqtt_client.publish(MQTT_TOPIC_UNLOCK, "deverouillage")
    lock_state["locked"] = False
    return jsonify({"status": "success", "message": "Serrure déverrouillée."})

@app.route("/lock", methods=["POST"])
@require_auth
@require_user_or_admin
def lock():
    """
    Envoie une commande MQTT pour verrouiller la serrure.
    Met à jour l'état local de la serrure.
    """
    mqtt_client.publish(MQTT_TOPIC_LOCK, "fermeture")
    lock_state["locked"] = True
    return jsonify({"status": "success", "message": "Serrure verrouillée."})

# ----------------
# ENDPOINTS ADMIN (Accès réservé aux administrateurs)
# ----------------
@app.route("/admin")
@require_auth
@require_admin
def admin_panel():
    """
    Affiche le tableau de bord administrateur (admin.html).
    """
    return render_template("admin.html")

@app.route("/admin/users")
@require_auth
@require_admin
def admin_users():
    """
    Affiche la liste de tous les utilisateurs.
    """
    users = User.query.all()
    return render_template("admin_users.html", users=users)

@app.route("/admin/logs")
@require_auth
@require_admin
def admin_logs():
    """
    Affiche la page des logs pour l'administrateur (admin_logs.html).
    """
    return render_template("admin_logs.html")

@app.route("/admin/users/add", methods=["POST"])
@require_auth
@require_admin
def add_user():
    """
    Ajoute un nouvel utilisateur via une requête POST JSON.
    Hache le mot de passe avant de le stocker.
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')
    if not username or not password:
        return jsonify({"error": "username et password requis"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Utilisateur déjà existant"}), 409
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed, role=role)
    db.session.add(new_user)
    db.session.commit()
    logging.info(f"[ADMIN] Ajout user={username} role={role}")
    return jsonify({"message": "OK"}), 201

@app.route("/admin/users/update", methods=["PUT"])
@require_auth
@require_admin
def update_user():
    """
    Met à jour les informations (role et/ou mot de passe) d'un utilisateur existant.
    """
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
    logging.info(f"[ADMIN] Update user_id={user_id}")
    return jsonify({"message": "Mise à jour OK"}), 200

@app.route("/admin/users/delete", methods=["DELETE"])
@require_auth
@require_admin
def delete_user():
    """
    Supprime un utilisateur existant via son ID.
    """
    data = request.json
    user_id = data.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Inexistant"}), 404
    db.session.delete(user)
    db.session.commit()
    logging.info(f"[ADMIN] Delete user_id={user_id}")
    return jsonify({"message": "Utilisateur supprimé"}), 200

@app.route("/admin/reset_challenge", methods=["POST"])
@require_auth
@require_admin
def admin_reset_challenge():
    """
    Réinitialise l'état de la serrure à "locked".
    Cet endpoint réinitialise uniquement la serrure.
    """
    try:
        mqtt_client.publish(MQTT_TOPIC_LOCK, "1")
        lock_state["locked"] = True
        logging.info("[ADMIN] Reset Challenge => Serrure locked.")
        return jsonify({"message": "Challenge reset => serrure verrouillée."}), 200
    except Exception as e:
        logging.error(f"[ADMIN] Erreur reset challenge : {e}")
        return jsonify({"error": str(e)}), 500

# -------------------------------------------------------------------------------------
# (Note : L'endpoint vulnérable /v1/unlock_public a été retiré pour sécuriser l'API)
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# GESTION DES LOGS EN TEMPS RÉEL VIA SOCKET.IO
# -------------------------------------------------------------------------------------
log_file_path = "serrure.log"  # Chemin vers le fichier de logs

def tail_logs():
    """
    Lit le fichier de logs en temps réel et émet chaque ligne via SocketIO
    pour permettre la visualisation en direct des logs dans l'interface web.
    """
    if not os.path.exists(log_file_path):
        open(log_file_path, "w").close()
    try:
        with open(log_file_path, "r") as f:
            f.seek(0, os.SEEK_END)
            while True:
                line = f.readline()
                if line:
                    socketio.emit("log_update", {"log": line.strip()})
                else:
                    time.sleep(0.2)
    except Exception as e:
        logging.error(f"Erreur logs : {e}")

threading.Thread(target=tail_logs, daemon=True).start()

# -------------------------------------------------------------------------------------
# AJOUT DE HEADERS DE SÉCURITÉ AUX RÉPONSES HTTP
# -------------------------------------------------------------------------------------
@app.after_request
def security_headers(response):
    """
    Ajoute des headers de sécurité aux réponses HTTP pour prévenir certaines attaques.
    - X-Frame-Options: Empêche le clickjacking.
    - X-Content-Type-Options: Empêche la déduction automatique du type MIME.
    """
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

# -------------------------------------------------------------------------------------
# LANCEMENT DE L'APPLICATION FLASK (MODE DÉVELOPPEMENT)
# -------------------------------------------------------------------------------------
if __name__ == "__main__":
    # Démarre l'application Flask sur toutes les interfaces (0.0.0.0) au port 5000, en mode debug
    app.run(host="0.0.0.0", port=5000, debug=True)
