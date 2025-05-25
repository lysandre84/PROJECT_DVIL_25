/*
=================================================================================
 FICHIER       : accueil.js
 DESCRIPTION   : Script principal pour la page d'accueil utilisateur.
 AUTEUR        : Lysandre / Lysius
 DATE          : 14/02/25
 VERSION       : 3.0.0
 LICENCE       : Autre
=================================================================================

 HISTORIQUE :
 - 14/02/25 : [Lysius] Création du script.
 - 25/05/25 : [Lysius] Ajout fonction.
 - 25/05/25 : [Lysius] Version commentée.

 USAGE :
 - À inclure dans la page accueil via <script src="/static/js/accueil.js"></script>

 CONTACT :
 - Email :    lysandrepro@gmail.com
 - GitHub :   https://github.com/lysandre84
 - Framagit : https://framagit.org/vialette

=================================================================================
*/

document.addEventListener("DOMContentLoaded", async function() {
    console.log(" Script `accueil.js` chargé !");

    // Vérifie si l'utilisateur est authentifié et affiche le nom + bouton admin si admin
    async function checkSession() {
        try {
            const response = await fetch("/user/status", {
                method: "GET",
                credentials: "include"
            });

            if (!response.ok) {
                throw new Error(" Session invalide !");
            }

            const data = await response.json();
            console.log(" Utilisateur connecté :", data.username, "Role:", data.role);

            // Affiche le nom de l'utilisateur
            document.getElementById("username").textContent = data.username;

            // Affiche le bouton admin panel si rôle = admin
            if (data.role === "admin") {
                document.getElementById("admin-panel").style.display = "inline-block";
            }

            return data;
        } catch (error) {
            console.error(" Erreur de session :", error);
            alert(" Vous devez être connecté !");
            window.location.href = "/login";
        }
    }

    // Vérifie la session dès le chargement
    await checkSession();

    // Envoie une commande POST à /unlock ou /lock
    async function sendCommand(url) {
        try {
            const response = await fetch(url, {
                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json"
                }
            });

            // Parse la réponse en JSON
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || `Échec : ${response.status}`);
            }

            alert(data.message);

        } catch (error) {
            console.error(" Erreur :", error);
            alert(" Erreur lors de l'envoi de la commande : " + error.message);
        }
    }

    // Bouton ouvrir la serrure
    document.getElementById("unlock-door").addEventListener("click", function() {
        console.log("🔓 Bouton 'Ouvrir la serrure' cliqué !");
        sendCommand("/unlock");
    });

    // Bouton fermer la serrure
    document.getElementById("lock-door").addEventListener("click", function() {
        console.log("🔒 Bouton 'Fermer la serrure' cliqué !");
        sendCommand("/lock");
    });

    // Bouton logout
    document.getElementById("logout").addEventListener("click", async function() {
        try {
            console.log(" Tentative de déconnexion...");
            const response = await fetch("/logout", {
                method: "POST",
                credentials: "include"
            });

            if (response.ok) {
                console.log(" Déconnexion réussie. Redirection vers /login.");
                window.location.href = "/login";
            } else {
                console.error(" Erreur lors de la déconnexion.");
                alert(" Impossible de se déconnecter !");
            }
        } catch (error) {
            console.error(" Erreur de requête logout :", error);
            alert(" Erreur serveur lors de la déconnexion !");
        }
    });

    // Rafraîchit le statut de la serrure toutes les 0.5s
    function refreshStatus() {
        fetch('/status', { credentials: 'include' })
            .then(response => response.json())
            .then(data => {
                // Met à jour le statut
                document.getElementById('serrure-status').innerHTML = "<b>Statut de la serrure :</b> " + data.status;
            })
            .catch(() => {
                document.getElementById('serrure-status').innerHTML = "<b>Statut de la serrure :</b> Erreur de statut";
            });
    }

    refreshStatus();
    setInterval(refreshStatus, 500);
    console.log(" Événements attachés aux boutons !");
});
