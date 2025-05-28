/*
=================================================================================
 FICHIER       : admin_users.js
 DESCRIPTION   : Script JS gestion des utilisateurs .
 AUTEUR        : Lysandre / Lysius
 DATE          : 14/02/25
 VERSION       : 3.0.0
 LICENCE       : Autre
=================================================================================

 HISTORIQUE :
 - 14/02/25 : [Lysius] Création du script.
 - 12/05/25 : [Lysius] Ajout Button.
 - 25/05/25 : [Lysius] Modification de fonction.
 - 25/05/25 : [Lysius] Version commentée.

 USAGE :
 - À inclure via <script src="/static/js/admin_users.js"></script>

 CONTACT :
 - Email :    lysandrepro@gmail.com
 - GitHub :   https://github.com/lysandre84
 - Framagit : https://framagit.org/vialette

=================================================================================
*/


// static/js/admin_users.js

document.addEventListener("DOMContentLoaded", function () {
    console.log("🛠 admin_users.js chargé.");

    // ----------- MODALE AJOUT UTILISATEUR -----------
    const modalAdd = document.getElementById("modal-add");
    const btnAddUser = document.getElementById("btn-add-user");
    const btnAddSubmit = document.getElementById("btn-add-submit");
    const btnAddCancel = document.getElementById("btn-add-cancel");

    btnAddUser?.addEventListener("click", () => { modalAdd.style.display = "flex"; });
    btnAddCancel?.addEventListener("click", () => { modalAdd.style.display = "none"; });

    btnAddSubmit?.addEventListener("click", async () => {
        const username = document.getElementById("add-username").value;
        const password = document.getElementById("add-password").value;
        const role = document.getElementById("add-role").value;
        try {
            const resp = await fetch("/admin/users/add", {
                method: "POST",
                credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password, role })
            });
            if (!resp.ok) {
                const err = await resp.json();
                throw new Error(err.error || "Erreur ajout user");
            }
            alert("Utilisateur ajouté avec succès !");
            window.location.reload();
        } catch (err) {
            alert("Erreur: " + err);
        }
    });

    // ----------- MODALE MODIF UTILISATEUR -----------
    const modalEdit = document.getElementById("modal-edit");
    const btnEditSubmit = document.getElementById("btn-edit-submit");
    const btnEditCancel = document.getElementById("btn-edit-cancel");

    btnEditCancel?.addEventListener("click", () => { modalEdit.style.display = "none"; });

    document.querySelectorAll(".btn-edit").forEach(btn => {
        btn.addEventListener("click", () => {
            const userId = btn.getAttribute("data-id");
            const username = btn.getAttribute("data-username");
            const role = btn.getAttribute("data-role");

            document.getElementById("edit-user-id").value = userId;
            document.getElementById("edit-username").textContent = `Utilisateur: ${username} (ID: ${userId})`;
            document.getElementById("edit-password").value = "";
            document.getElementById("edit-role").value = ""; // Pas de préselection

            modalEdit.style.display = "flex";
        });
    });

    btnEditSubmit?.addEventListener("click", async () => {
        const user_id = document.getElementById("edit-user-id").value;
        const password = document.getElementById("edit-password").value;
        const role = document.getElementById("edit-role").value;

        const bodyData = { user_id };
        if (password) bodyData.password = password;
        if (role) bodyData.role = role;

        try {
            const resp = await fetch("/admin/users/update", {
                method: "PUT",
                credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(bodyData)
            });
            if (!resp.ok) {
                const err = await resp.json();
                throw new Error(err.error || "Erreur update user");
            }
            alert("Utilisateur mis à jour !");
            window.location.reload();
        } catch (err) {
            alert("Erreur: " + err);
        }
    });

    // ----------- SUPPRESSION UTILISATEUR -----------
    document.querySelectorAll(".btn-delete").forEach(btn => {
        btn.addEventListener("click", async () => {
            const userId = btn.getAttribute("data-id");
            const userName = btn.getAttribute("data-username");

            if (!confirm(`Voulez-vous vraiment supprimer l'utilisateur "${userName}" ?`)) return;

            try {
                const resp = await fetch("/admin/users/delete", {
                    method: "DELETE",
                    credentials: "include",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ user_id: userId })
                });
                if (!resp.ok) {
                    const err = await resp.text();
                    throw new Error(err);
                }
                alert("Utilisateur supprimé avec succès !");
                window.location.reload();
            } catch (err) {
                alert("Erreur suppression : " + err);
            }
        });
    });

    // ----------- EDITION INLINE (PIN/NFC/tag) -----------
    document.querySelectorAll("td.editable").forEach(function(td) {
        td.addEventListener("focus", () => td.style.background = "#262e38");
        td.addEventListener("blur", function() {
            const userId = td.getAttribute("data-user-id");
            const field = td.getAttribute("data-field");
            const newValue = td.innerText.trim();

            // On évite de faire l'appel s'il n'y a pas de changement ou champs vides
            if (!userId || !field) return;

            fetch("/admin/update_field", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    user_id: userId,
                    field: field,
                    value: newValue
                })
            })
            .then(resp => resp.json())
            .then(data => {
                if (data.status === "ok") {
                    td.style.background = "#183c2d";
                    setTimeout(() => { td.style.background = ""; }, 700);
                } else {
                    td.style.background = "#4f1818";
                    setTimeout(() => { td.style.background = ""; }, 1200);
                    alert(data.error || "Erreur de mise à jour.");
                }
            })
            .catch(() => {
                td.style.background = "#4f1818";
                setTimeout(() => { td.style.background = ""; }, 1200);
                alert("Erreur lors de la requête !");
            });
        });
    });
});
