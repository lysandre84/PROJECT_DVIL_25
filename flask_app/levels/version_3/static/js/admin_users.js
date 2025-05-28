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

document.addEventListener("DOMContentLoaded", function() {
  console.log("🛠 admin_users.js chargé.");

  // Éléments modale "Ajouter"
  const modalAdd = document.getElementById("modal-add");
  const btnAddUser = document.getElementById("btn-add-user");
  const btnAddSubmit = document.getElementById("btn-add-submit");
  const btnAddCancel = document.getElementById("btn-add-cancel");

  // Éléments modale "Modifier"
  const modalEdit = document.getElementById("modal-edit");
  const btnEditSubmit = document.getElementById("btn-edit-submit");
  const btnEditCancel = document.getElementById("btn-edit-cancel");

  // Ouvrir la modale Add
  btnAddUser.addEventListener("click", () => {
    modalAdd.style.display = "flex";
  });

  // Annuler Add
  btnAddCancel.addEventListener("click", () => {
    modalAdd.style.display = "none";
  });

  // Soumettre Add
  btnAddSubmit.addEventListener("click", async () => {
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
      window.location.reload(); // recharger la page pour voir le nouvel utilisateur
    } catch (err) {
      alert("Erreur: " + err);
    }
  });

  // Boutons “Modifier” dans la table
  document.querySelectorAll(".btn-edit").forEach(btn => {
    btn.addEventListener("click", () => {
      const userId = btn.getAttribute("data-id");
      const username = btn.getAttribute("data-username");
      const role = btn.getAttribute("data-role");

      // Remplit la modale
      document.getElementById("edit-user-id").value = userId;
      document.getElementById("edit-username").textContent = `Utilisateur: ${username} (ID: ${userId})`;
      document.getElementById("edit-password").value = "";
      document.getElementById("edit-role").value = ""; // par défaut

      // Ouvrir la modale
      modalEdit.style.display = "flex";
    });
  });

  // Annuler edit
  btnEditCancel.addEventListener("click", () => {
    modalEdit.style.display = "none";
  });

  // Soumettre edit
  btnEditSubmit.addEventListener("click", async () => {
    const user_id = document.getElementById("edit-user-id").value;
    const password = document.getElementById("edit-password").value;
    const role = document.getElementById("edit-role").value;

    // On envoie seulement si password ou role est renseigné
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

  // Boutons “Supprimer”
  document.querySelectorAll(".btn-delete").forEach(btn => {
    btn.addEventListener("click", async () => {
      const userId = btn.getAttribute("data-id");
      const userName = btn.getAttribute("data-username");

      // Demande confirmation
      if (!confirm(`Voulez-vous vraiment supprimer l'utilisateur "${userName}" ?`)) {
        return; // annule
      }

      try {
        const resp = await fetch("/admin/users/delete", {
          method: "DELETE",
          credentials: "include",  // envoie le cookie JWT
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: userId })
        });
        if (!resp.ok) {
          const err = await resp.text();
          throw new Error(err);
        }

        alert("Utilisateur supprimé avec succès !");
        window.location.reload(); // recharge la page
      } catch (err) {
        alert("Erreur suppression : " + err);
      }
    });
  });
});
document.querySelectorAll('td.editable').forEach(cell => {
  cell.addEventListener('blur', function () {
    const userId = this.dataset.userId;
    const field = this.dataset.field;
    const value = this.innerText.trim();

    fetch('/admin/update_user_field', {
      method: 'POST',
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, field: field, value: value })
    })
    .then(resp => resp.json())
    .then(data => {
      if (data.status !== "ok") {
        alert("Erreur lors de la mise à jour : " + (data.error || "inconnue"));
      }
    });
  });
});

document.addEventListener("DOMContentLoaded", function () {
    // Inline edition pour PIN, NFC, TAG
    document.querySelectorAll("td.editable").forEach(function(td) {
        td.addEventListener("blur", function() {
            const userId = td.dataset.userId;
            const field = td.dataset.field;
            const newValue = td.innerText.trim();

            fetch("/admin/update_field", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: JSON.stringify({
                    user_id: userId,
                    field: field,
                    value: newValue
                })
            }).then(resp => resp.json())
              .then(data => {
                  if(data.status === "ok") {
                      td.style.background = "#183c2d";
                      setTimeout(() => { td.style.background = ""; }, 700);
                  } else {
                      td.style.background = "#4f1818";
                      setTimeout(() => { td.style.background = ""; }, 1200);
                      alert(data.error || "Erreur de mise à jour.");
                  }
              });
        });
        // Optionnel: couleur d’indication quand on édite
        td.addEventListener("focus", () => td.style.background = "#262e38");
        td.addEventListener("blur", () => td.style.background = "");
    });
});

document.querySelectorAll('td.editable').forEach(cell => {
    cell.addEventListener('blur', function () {
        const userId = this.getAttribute('data-user-id');
        const field = this.getAttribute('data-field');
        const value = this.innerText.trim();

        fetch(`/api/users/${userId}/update_field`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ field, value })
        })
        .then(res => res.json())
        .then(data => {
            if (!data.success) {
                alert("Erreur lors de la sauvegarde : " + data.error);
            }
        });
    });
});
