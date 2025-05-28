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



// static/js/admin_logs.js

document.addEventListener("DOMContentLoaded", function () {
    // Sélecteurs
    const select = document.getElementById("log-type-select");
    const container = document.getElementById("logs-container");
    let autoScroll = true;
    let userScrollTimeout = null;
    let currentType = select.value;

    // 🟢 Laisse ce block unique, tu peux le modifier/adapter facilement
    container.addEventListener('scroll', function () {
        if (container.scrollTop > 10) {
            autoScroll = false;
            clearTimeout(userScrollTimeout);
            userScrollTimeout = setTimeout(() => { autoScroll = true; }, 5000);
        } else {
            autoScroll = true;
        }
    });

    function getLogClass(line, type) {
        // Ici tu ajoutes/modifies facilement tes couleurs ou règles !
        if (/error|erreur|fail|échec/i.test(line)) return "log-entry log-error";
        if (/warn|attention|warning/i.test(line)) return "log-entry log-warning";
        if (type === "API" || /\[API\]/.test(line)) return "log-entry api-log";
        if (type === "SERVEUR" || /\[SERVEUR\]/.test(line)) return "log-entry cat-serv";
        if (type === "Clavier-I²C" || /\[Clavier-I²C\]/.test(line)) return "log-entry cat-clav";
        if (type === "INFO-CLAVIER" || /\[INFO-CLAVIER\]/.test(line)) return "log-entry cat-info";
        if (type === "NFC" || /\[NFC\]/.test(line)) return "log-entry cat-nfc";
        if (type === "API-challenge" || /\[API-challenge\]/.test(line)) return "log-entry cat-api";
        return "log-entry";
    }

    function filterRepeatedLines(lines) {
        // Compacte les logs identiques à la suite
        let filtered = [];
        let lastLine = null, count = 1;
        for (let i = 0; i < lines.length; i++) {
            if (lines[i] === lastLine) {
                count++;
            } else {
                if (lastLine !== null) {
                    filtered.push(
                        lastLine +
                        (count > 1 ? ` <span class="log-repeat">(x${count})</span>` : "")
                    );
                }
                lastLine = lines[i];
                count = 1;
            }
        }
        if (lastLine !== null) {
            filtered.push(
                lastLine +
                (count > 1 ? ` <span class="log-repeat">(x${count})</span>` : "")
            );
        }
        return filtered;
    }

    function loadLogs(type) {
        fetch(`/admin/logs/filter?type=${encodeURIComponent(type)}`)
            .then(res => res.json())
            .then(data => {
                if (data.lines) {
                    const lines = data.lines.reverse(); // Plus récents en haut
                    const filtered = filterRepeatedLines(lines);
                    container.innerHTML = filtered.map((l) =>
                        `<div class="${getLogClass(l, type)}">${l.replace(/</g, "&lt;")}</div>`
                    ).join('');
                    if (autoScroll) container.scrollTop = 0;
                } else if (data.error) {
                    container.innerHTML = `<div class="log-entry log-error">${data.error}</div>`;
                }
            });
    }

    function refreshLogs() {
        loadLogs(currentType);
    }

    setInterval(refreshLogs, 500);
    refreshLogs();

    select.addEventListener("change", function () {
        currentType = this.value;
        refreshLogs();
    });

    document.getElementById("reset-logs-btn").addEventListener("click", async function () {
        if (confirm("Es-tu sûr de vouloir effacer tous les logs ?")) {
            try {
                const response = await fetch("/admin/reset_logs", {
                    method: "POST",
                    credentials: "include"
                });
                if (response.ok) {
                    alert("Logs réinitialisés !");
                    window.location.reload();
                } else {
                    alert("Échec de la réinitialisation !");
                }
            } catch (err) {
                alert("Erreur lors de la requête !");
            }
        }
    });
});
