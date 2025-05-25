/*
=================================================================================
 FICHIER       : admin_logs.js
 DESCRIPTION   : Script d'affichage temps réel des logs dans l'admin.
 AUTEUR        : Lysandre / Lysius
 DATE          : 14/02/25
 VERSION       : 3.0.0
 LICENCE       : Autre
=================================================================================

 HISTORIQUE :
 - 14/02/25 : [Lysius] Création du script.
 - 25/05/25 : [Lysius] Version commentée.

 USAGE :
 - À inclure via <script src="/static/js/admin_logs.js"></script>

 CONTACT :
 - Email :    lysandrepro@gmail.com
 - GitHub :   https://github.com/lysandre84
 - Framagit : https://framagit.org/vialette

=================================================================================
*/

// Affiche les logs en couleur selon la catégorie
function refreshLogs() {
    fetch("/admin/log_raw")
        .then(r => r.json())
        .then(data => {
            let html = "";
            data.logs.forEach(function(row){
                let cat = row[0] || "";
                let line = row[1] || "";
                let css = "log-entry ";
                if(cat === "SERVEUR") css += "cat-serv";
                else if(cat === "Clavier-I²C") css += "cat-clav";
                else if(cat === "INFO-CLAVIER") css += "cat-info";
                else if(cat === "NFC") css += "cat-nfc";
                else if(cat === "API") css += "cat-api";
                if(line.includes("ERROR")) css += " log-error";
                else if(line.includes("WARNING")) css += " log-warning";
                html += `<div class="${css}">[${cat}] ${line}</div>`;
            });
            document.getElementById('log-container').innerHTML = html || "Aucune log disponible";
        })
        .catch((err) => {
            document.getElementById('log-container').innerHTML = "Erreur lors du chargement des logs";
            console.error("[JS] Erreur lors du chargement des logs :", err);
        });
}

// Rafraîchit les logs toutes les 0.5 secondes
setInterval(refreshLogs, 500);
refreshLogs();

// Bouton reset logs
document.getElementById("reset-logs-btn").addEventListener("click", async function () {
    if (confirm("⚠️ Es-tu sûr de vouloir effacer tous les logs ?")) {
        try {
            const response = await fetch("/admin/reset_logs", {
                method: "POST",
                credentials: "include"
            });
            if (response.ok) {
                alert("✅ Logs réinitialisés !");
                window.location.reload(); // Recharge la page pour afficher les logs vides
            } else {
                alert("❌ Échec de la réinitialisation !");
            }
        } catch (err) {
            alert("❌ Erreur lors de la requête !");
        }
    }
});
