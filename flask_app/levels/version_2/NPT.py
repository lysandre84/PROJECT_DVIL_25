#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------------
#   DVIL SYSTEM - Plateforme d’apprentissage, API RESTful
#   Version fusionnée : configuration sécurisée + challenges vulnérables
#   Auteur : Lysius [VIALETTE Lysandre]
#   Description : API de serrure connectée, incluant routes sécurisées ET routes vulnérables XSS/Path Traversal
# -------------------------------------------------------------------------------------

# =============================================================================
#                                API DVIL
#        Version Challenge / Sécurité – Flask, MQTT, SocketIO, Auth, Logs
# =============================================================================

# -------------------------------------------------------------------------------------
# Imports des bibliothèques nécessaires
# -------------------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
#   DVIL SYSTEM - Plateforme d’apprentissage, API RESTful
#   Version fusionnée : configuration sécurisée + challenges vulnérables
#   Auteur : Lysius [VIALETTE Lysandre]
#   Description : API de serrure connectée, incluant routes sécurisées ET routes vulnérables XSS/Path Traversal
# =============================================================================
import os
import logging
import json
import datetime
import threading
import time
import jwt
import paho.mqtt.client as mqtt
import redis
import secrets
from functools import wraps

from flask import (
    Flask, request, jsonify, render_template,
    render_template_string, make_response, redirect,
    url_for, session
)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager, UserMixin, current_user
from flask_talisman import Talisman
from sqlalchemy import text

# -------------------- Initialisation des dossiers de logs --------------------
load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

LOG_FILES = {
    "SERVEUR":    "serveur.log",
    "Clavier-I²C": "clavier.log",
    "INFO-CLAVIER": "keypad_raw.log",
    "NFC":        "nfc.log",
    "API":        "api.log",
    "API-challenge": os.path.join(LOGS_DIR, "challenge.log")

}

os.makedirs(LOGS_DIR, exist_ok=True)
# ------------------------- LOGGERS MULTI-SOURCES ----------------------------

def create_logger(name, file, level=logging.INFO, fmt=None):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        fhandler = logging.FileHandler(file)
        formatter = logging.Formatter(fmt or '%(asctime)s [%(levelname)s] %(message)s')
        fhandler.setFormatter(formatter)
        logger.addHandler(fhandler)
        logger.setLevel(level)
    return logger

serveur_logger    = create_logger("serveur",      os.path.join(LOGS_DIR, "serveur.log"),    fmt='%(asctime)s [SERVEUR] %(message)s')
clavier_logger    = create_logger("clavier",      os.path.join(LOGS_DIR, "clavier.log"),    fmt='%(asctime)s [Clavier-I²C] %(message)s')
info_clavier_logger = create_logger("info_clavier",os.path.join(LOGS_DIR, "keypad_raw.log"),fmt='%(asctime)s [INFO-CLAVIER] %(message)s')
nfc_logger        = create_logger("nfc",          os.path.join(LOGS_DIR, "nfc.log"),        fmt='%(asctime)s [NFC] %(message)s')
api_logger        = create_logger("api",          os.path.join(LOGS_DIR, "api.log"),        fmt='%(asctime)s [API] %(message)s')
main_logger       = create_logger("main",         os.path.join(BASE_DIR,  "serrure.log"))


challenge_logger = logging.getLogger("challenge")
challenge_file = os.path.join(LOGS_DIR, "challenge.log")
challenge_handler = logging.FileHandler(challenge_file)
challenge_handler.setFormatter(logging.Formatter('%(asctime)s [API-CHALLENGE] %(message)s'))
challenge_logger.setLevel(logging.INFO)
challenge_logger.addHandler(challenge_handler)











def ensure_logs_exist():
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR, exist_ok=True)
    for fname in LOG_FILES.values():
        fpath = os.path.join(LOGS_DIR, fname)
        if not os.path.exists(fpath):
            open(fpath, "a", encoding="utf-8").close()

def ensure_log_file(log_path):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    if not os.path.exists(log_path):
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("")

# -------------------------------------------------------
def log_all(message, logger_list):
    for lg in logger_list:
        lg.info(message)

# -------------------- Flask & Extensions ----------------
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
if os.getenv("FLASK_ENV") == "production":
    Talisman(app)
SECRET_KEY = os.getenv("SECRET_KEY", "secretkey")
app.config['SECRET_KEY'] = SECRET_KEY
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_USER     = os.getenv("DB_USER", "Ad_@min")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Admin")
DB_NAME     = os.getenv("DB_NAME", "dvil_db")
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# -------------------- Limiter -----------------
try:
    redis_client = redis.StrictRedis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0)
    redis_client.ping()
    limiter_storage = "redis://localhost:6379"
except redis.ConnectionError:
    serveur_logger.warning("⚠️ Redis non accessible, fallback mémoire.")
    redis_client = None
    limiter_storage = "memory://"

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
    return User.query.get(int(user_id))

# -------------------- Modèles DB --------------
class User(UserMixin, db.Model):
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
    __tablename__ = 'serrure_state'
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(10), nullable=False)

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

with app.app_context():
    db.create_all()

# -------------- Auth et décorateurs --------------
def verify_token_cookie():
    token = request.cookies.get("jwt_token")
    if not token:
        return None
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        payload = verify_token_cookie()
        if not payload:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated

def require_admin(f):
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
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.headers.get("X-Api-Key") != API_KEY:
            return jsonify({"error": "Clé API invalide"}), 401
        return f(*args, **kwargs)
    return decorated

# ---------------------- MQTT config ---------------------
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC_LOCK = "DVIL/Serrure"
MQTT_TOPIC_UNLOCK = "DVIL/Serrure"
MQTT_TOPIC_STATUS = "DVIL/Status"
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set("admin", "admin")
lock_state = {"locked": True}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        serveur_logger.info("[MQTT] Connecté au broker")
        client.subscribe(MQTT_TOPIC_UNLOCK)
    else:
        serveur_logger.error(f"[MQTT] Échec de connexion, code={rc}")

def on_message(client, userdata, msg):
    global lock_state
    if msg.topic == MQTT_TOPIC_UNLOCK:
        payload_str = msg.payload.decode()
        if payload_str == "deverouillage":
            lock_state["locked"] = False
        elif payload_str == "fermeture":
            lock_state["locked"] = True
        serveur_logger.info(f"[MQTT] Serrure => locked={lock_state['locked']}")

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
def mqtt_loop():
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_forever()
threading.Thread(target=mqtt_loop, daemon=True).start()

# ------------------ Socket.IO logs en temps réel -----------------
def tail_logs():
    try:
        with open(os.path.join(BASE_DIR, "serrure.log"), "r") as f:
            f.seek(0, 2)
            while True:
                line = f.readline()
                if line:
                    socketio.emit("log_update", {"log": line.strip()})
                else:
                    time.sleep(0.5)
    except Exception as e:
        print(f"[TAIL_LOGS] ERREUR: {e}")

threading.Thread(target=tail_logs, daemon=True).start()

@app.after_request
def security_headers(response):
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

# ========== ROUTES PRINCIPALES (Accueil, login, logout, etc.) ==========
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/accueil")
@require_auth
def accueil():
    payload = verify_token_cookie()
    return render_template("accueil.html", username=payload["username"])

@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
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
    resp = make_response(redirect(url_for("login_page")))
    resp.set_cookie("jwt_token", "", expires=0)
    return resp

@app.route("/verify_pin", methods=["POST"])
def verify_pin():
    data = request.get_json(force=True)
    pin = data.get("pin_code", "")
    user = User.query.filter_by(pin_code=pin).first()

    info_clavier_logger.info(f"[KEYPAD_RAW] {pin}")

    if user:
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
    payload = verify_token_cookie()
    user = User.query.filter_by(username=payload["username"]).first()
    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404
    return jsonify({"username": user.username, "role": user.role}), 200

@app.route("/status", methods=["GET"])
@require_auth
def get_status():
    status = "verrouillée" if lock_state["locked"] else "déverrouillée"
    serveur_logger.info(f"Status consulté ({status})")
    return jsonify({"status": status})

@app.route("/unlock", methods=["POST"])
@require_auth
@require_user_or_admin
def unlock():
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
    return render_template("admin.html")



@app.route("/admin/users")
@require_auth
@require_admin
def admin_users():
    users = User.query.all()
    return render_template("admin_users.html", users=users)

@app.route("/admin/logs")
@require_auth
@require_admin
def admin_ulogs():
    import os

    LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(LOGS_DIR, exist_ok=True)  # Crée le dossier logs si absent

    log_files = {
        "SERVEUR":         os.path.join(LOGS_DIR, "serveur.log"),
        "Clavier-I²C":     os.path.join(LOGS_DIR, "clavier.log"),
        "INFO-CLAVIER":    os.path.join(LOGS_DIR, "keypad_raw.log"),
        "NFC":             os.path.join(LOGS_DIR, "nfc.log"),
        "API":             os.path.join(LOGS_DIR, "api.log"),
        "API-challenge":   os.path.join(LOGS_DIR, "challenge.log"),  # fichier exemple supplémentaire
    }
    logs_by_type = {}
    for logtype, path in log_files.items():
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                pass  # Fichier vide
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()[-300:]  # Affiche les 300 dernières
                logs_by_type[logtype] = lines
        except Exception as e:
            logs_by_type[logtype] = [f"[ERROR] Impossible de lire ce log : {e}\n"]
    return render_template("admin_logs.html", logs_by_type=logs_by_type)

@app.route("/admin/log_raw")
@require_auth
@require_admin
def admin_log_raw():
    import os
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


@app.route("/admin/users/add", methods=["POST"])
@require_auth
@require_admin
def add_user():
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
    data = request.get_json(force=True)
    code = data.get("raw", "")
    info_clavier_logger.info(f"{code}")
    return jsonify({"status": "ok"})

@app.route("/api/log_event", methods=["POST"])
@require_api_key
def log_event():
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

# -------------------------------------------------------------------------------------
# ******* CHALLENGE NIVEAU 2 : ENDPOINTS VULNÉRABLES (XSS, Path Traversal) ************
# -------------------------------------------------------------------------------------
@app.route("/api/mqtt_challenge", methods=["POST"])
def mqtt_challenge():
    client_id = request.json.get("client_id")
    topic = request.json.get("topic")
    payload = request.json.get("payload")

    challenge_logger.info(f"Client {client_id} a tenté de publier sur le topic {topic} avec payload {payload}")

    return jsonify({"status": "ok"})

@app.route("/v2/unlock_challenge", methods=["POST"])
def unlock_challenge():
    """
    Endpoint vulnérable : Déverrouille la serrure si XSS et Traversal réalisés.
    Accessible sans auth si les failles ont été exploitées (sessions xss_done & path_done).
    """
    if not (session.get("xss_done") and session.get("path_done")):
        return jsonify({
            "status": "fail",
            "message": "Vous devez d'abord exploiter la faille XSS et la faille Path Traversal."
        }), 403

    try:
        mqtt_client.publish(MQTT_TOPIC_UNLOCK, "deverouillage")
	
        lock_state["locked"] = False
        return jsonify({"status": "success", "message": "Serrure déverrouillée (via challenge)."})
        api_logger.info(f"CHALLENGE XSS+PATH TRAVERSAL REUSSI")


    except Exception as e:
        logging.error(f"Erreur lors de la publication MQTT (unlock_challenge): {e}")
        return jsonify({"status": "fail", "message": "Erreur lors de l'envoi de la commande MQTT."}), 500

@app.route("/v2/xss", methods=["GET", "POST"])
def vuln_xss():
    """
    Faille XSS : GET affiche le formulaire, POST enregistre le commentaire sans filtre (XSS possible).
    Active le flag de session xss_done.
    """
    if request.method == "POST":
        user_comment = request.form.get("comment", "")
        new_c = Comment(content=user_comment)
        db.session.add(new_c)
        db.session.commit()
        session["xss_done"] = True  # Flag : faille XSS exploitée
        return render_template_string(f"""
        <h2>Votre commentaire :</h2>
        <div style="color:blue;">
            {user_comment}
        </div>
        <p><a href="/v2/xss">Retour</a></p>
        """)
    return """
    <h1>Faille XSS</h1>
    <form method="POST" action="/v2/xss">
      <label>Entrez un commentaire :</label><br/>
      <textarea name="comment" rows="4" cols="50"></textarea><br/><br/>
      <button type="submit">Envoyer</button>
    </form>
    <p>(Les commentaires s’afficheront sans protection… XSS possible)</p>
    """

@app.route("/v2/traversal")
def vuln_traversal():
    """
    Faille Path Traversal : lit un fichier du dossier uploads sans contrôle du chemin.
    Nécessite que la faille XSS ait été exploitée (flag session).
    Active le flag path_done si exploit réussi.
    """
    if not session.get("xss_done"):
        return "⚠️ Vous devez d'abord exploiter la faille XSS avant d'accéder à celle-ci.", 403

    filename = request.args.get("file", "")
    base_folder = os.path.join(BASE_DIR, "uploads")
    filepath = os.path.join(base_folder, filename)

    try:
        with open(filepath, "r") as f:
            content = f.read()
        session["path_done"] = True  # Flag : faille Path Traversal exploitée
        return f"<pre>{content}</pre>"
    except Exception as e:
        return f"Erreur: {str(e)}", 404

def reset_challenge_niveau2():
    """
    Fonction utilitaire : supprime tous les commentaires et fichiers uploadés (reset du challenge).
    """
    time.sleep(5)
    db.session.execute(text("DELETE FROM comment"))
    db.session.commit()
    folder = os.path.join(BASE_DIR, "uploads")
    if os.path.isdir(folder):
        for f in os.listdir(folder):
            path_f = os.path.join(folder, f)
            if os.path.isfile(path_f):
                os.remove(path_f)
    session["xss_done"]  = False
    session["path_done"] = False
    logging.info("Niveau 2 => reset_challenge terminé.")

@app.route("/v2/trigger_reset", methods=["POST"])
def trigger_reset():
    """Déclenche un reset asynchrone du challenge niveau 2."""
    threading.Thread(target=reset_challenge_niveau2, daemon=True).start()
    return "Reset challenge niveau 2 en cours...", 200

# -------------------------------------------------------------------------------------
# Lancement de l’application (uniquement en mode debug ; avec Gunicorn/WSGI pour prod)
# -------------------------------------------------------------------------------------
#if __name__ == "__main__":
#    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
