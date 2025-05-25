/*
=================================================================================
 FICHIER       : accueil.js
 DESCRIPTION   : Gère la logique de la page d'accueil (authentification, actions sur la serrure).
 AUTEUR        : Lysandre / Lysius
 DATE          : 14/02/25
 VERSION       : 1.1.1
 LICENCE       : Autre
=================================================================================

 HISTORIQUE :
 - 14/02/25 : [Lysius] Création de la page.

USAGE :
 - À inclure dans accueil.html via : <script src="accueil.js"></script>
 - Compatible avec : Chrome, Firefox, Safari, Edge
 - Technologies utilisées : JavaScript ES6+, Fetch API

 SECURITÉ :
 - Points sensibles : Récupération du statut, envoi de commandes MQTT
 - Mesures mises en place : Vérification d'authentification

 CONTACT :
 - Email :    lysandrepro@gmail.com
 - GitHub :   https://github.com/lysandre84
 - Framagit : https://framagit.org/vialette

=================================================================================
*/

document.addEventListener("DOMContentLoaded", async function() {
    console.log("📢 Script `accueil.js` chargé !");

    // ---- SESSION & ADMIN ----
    async function checkSession() {
        try {
            const response = await fetch("/user/status", {
                method: "GET",
                credentials: "include"
            });

            if (!response.ok) throw new Error("⚠️ Session invalide !");

            const data = await response.json();
            console.log("✅ Utilisateur connecté :", data.username, "Role:", data.role);

            // Affiche le nom de l'utilisateur
            document.getElementById("username").textContent = data.username;

            // Si admin : affiche le bouton admin
            if (data.role === "admin") {
                document.getElementById("admin-panel").style.display = "inline-block";
            }

            return data;
        } catch (error) {
            console.error("❌ Erreur de session :", error);
            alert("⚠️ Vous devez être connecté !");
            window.location.href = "/login";
        }
    }

    await checkSession();

    // ---- STATUT SERRURE ----
    async function refreshStatus() {
        try {
            const response = await fetch('/status', { credentials: 'include' });
            if (!response.ok) throw new Error("Non autorisé");
            const data = await response.json();
            document.getElementById('serrure-status').textContent = data.status;
        } catch {
            document.getElementById('serrure-status').textContent = "Erreur de statut";
        }
    }

    refreshStatus();
    setInterval(refreshStatus, 500); // toutes les 0.5 secondes

    // ---- COMMANDES ----
    async function sendCommand(url) {
        try {
            const response = await fetch(url, {
                method: "POST",
                credentials: "include",
                headers: { "Content-Type": "application/json" }
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || `Échec : ${response.status}`);
            }
            alert(data.message);

        } catch (error) {
            console.error("❌ Erreur :", error);
            alert("⚠️ Erreur lors de l'envoi de la commande : " + error.message);
        }
    }

    // ---- EVENEMENTS BOUTONS ----
    document.getElementById("unlock-door").addEventListener("click", function() {
        console.log("🔓 Bouton 'Ouvrir la serrure' cliqué !");
        sendCommand("/unlock");
    });

    document.getElementById("lock-door").addEventListener("click", function() {
        console.log("🔒 Bouton 'Fermer la serrure' cliqué !");
        sendCommand("/lock");
    });

    document.getElementById("logout").addEventListener("click", async function() {
        try {
            console.log("🚪 Tentative de déconnexion...");
            const response = await fetch("/logout", {
                method: "POST",
                credentials: "include"
            });

            if (response.ok) {
                console.log("✅ Déconnexion réussie. Redirection vers /login.");
                window.location.href = "/login";
            } else {
                console.error("❌ Erreur lors de la déconnexion.");
                alert("⚠️ Impossible de se déconnecter !");
            }
        } catch (error) {
            console.error("❌ Erreur de requête logout :", error);
            alert("⚠️ Erreur serveur lors de la déconnexion !");
        }
    });

    console.log("✅ Événements attachés aux boutons !");
});
