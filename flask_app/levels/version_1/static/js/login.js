/*
=================================================================================
 FICHIER       : login.js
 DESCRIPTION   : Script pour la page de login utilisateur/admin (v3, rouge).
 AUTEUR        : Lysandre / Lysius
 DATE          : 14/02/25
 VERSION       : 3.0.0
 LICENCE       : Autre
=================================================================================

 HISTORIQUE :
 - 14/02/25 : [Lysius] Création du script.
 - 25/05/25 : [Lysius] Version commentée v3.

 USAGE :
 - À inclure via <script src="/static/js/login.js"></script>

 CONTACT :
 - Email :    lysandrepro@gmail.com
 - GitHub :   https://github.com/lysandre84
 - Framagit : https://framagit.org/vialette

=================================================================================
*/

// Gestion de la soumission du formulaire de login (exemple à adapter à ton backend)
document.addEventListener("DOMContentLoaded", function () {
    // Sélectionne le formulaire login
    var form = document.getElementById("login-form");
    if (!form) return;

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        var username = document.getElementById("username").value;
        var password = document.getElementById("password").value;

        try {
            const response = await fetch("/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),
                credentials: "include"
            });

            if (response.ok) {
                window.location.href = "/accueil";
            } else {
                document.getElementById("error-message").textContent = "Erreur d'authentification !";
                document.getElementById("error-message").style.display = "block";
            }
        } catch (err) {
            document.getElementById("error-message").textContent = "Erreur serveur !";
            document.getElementById("error-message").style.display = "block";
        }
    });
});
