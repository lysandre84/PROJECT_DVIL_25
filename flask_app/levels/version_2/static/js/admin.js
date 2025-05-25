/*
=================================================================================
 FICHIER       : admin.js
 DESCRIPTION   : Contrôle principal de la page d’administration.
 AUTEUR        : Lysandre / Lysius
 DATE          : 14/02/25
 VERSION       : 3.0.0
 LICENCE       : Autre
=================================================================================

 HISTORIQUE :
 - 14/02/25 : [Lysius] Création du script.
 - 25/05/25 : [Lysius] Version commenté.

 USAGE :
 - À inclure via <script src="/static/js/admin.js"></script>

 CONTACT :
 - Email :    lysandrepro@gmail.com
 - GitHub :   https://github.com/lysandre84
 - Framagit : https://framagit.org/vialette

=================================================================================
*/

document.addEventListener("DOMContentLoaded", function() {
    console.log("🔐 Admin panel JS chargé !");

    // Bouton Unlock
    document.getElementById("admin-unlock").addEventListener("click", async () => {
      try {
        const resp = await fetch("/unlock", {
          method: "POST",
          credentials: "include"
        });
        if (!resp.ok) {
          const txt = await resp.text();
          throw new Error(txt);
        }
        alert("Serrure déverrouillée !");
      } catch (err) {
        alert("Erreur unlock: " + err);
      }
    });

    // Bouton Lock
    document.getElementById("admin-lock").addEventListener("click", async () => {
      try {
        const resp = await fetch("/lock", {
          method: "POST",
          credentials: "include"
        });
        if (!resp.ok) {
          const txt = await resp.text();
          throw new Error(txt);
        }
        alert("Serrure verrouillée !");
      } catch (err) {
        alert("Erreur lock: " + err);
      }
    });

    // Bouton Se déconnecter
    document.getElementById("admin-logout").addEventListener("click", async () => {
      try {
        const resp = await fetch("/logout", {
          method: "POST",
          credentials: "include"
        });
        if (resp.ok) {
          window.location.href = "/login";
        } else {
          alert("Impossible de se déconnecter");
        }
      } catch (err) {
        alert("Erreur logout: " + err);
      }
    });
 
     // Bouton Reset Challenge
    const resetBtn = document.getElementById("reset-challenge-btn");
    resetBtn.addEventListener("click", async () => {
      try {
        const response = await fetch("/admin/reset_challenge", {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" }
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(errorText || "Erreur lors du reset");
        }

        const data = await response.json();
        alert("✅ " + data.message);
      } catch (error) {
        alert("❌ Échec du reset : " + error.message);
      }
    });



});
