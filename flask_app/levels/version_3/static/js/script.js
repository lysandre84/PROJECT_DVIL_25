/*
=================================================================================
 FICHIER       : script.js
 DESCRIPTION   : Animation texte tapé "enigme" sur page d'accueil (v3, rouge).
 AUTEUR        : Lysandre / Lysius
 DATE          : 14/02/25
 VERSION       : 3.0.0
 LICENCE       : Autre
=================================================================================

 HISTORIQUE :
 - 14/02/25 : [Lysius] Création du script.
 - 25/05/25 : [Lysius] Version commentée v3.

 USAGE :
 - À inclure via <script src="/static/js/script.js"></script>

 CONTACT :
 - Email :    lysandrepro@gmail.com
 - GitHub :   https://github.com/lysandre84
 - Framagit : https://framagit.org/vialette

=================================================================================
*/

// Animation effet "texte tapé" pour l'énigme
document.addEventListener("DOMContentLoaded", function () {
    var enigme = document.getElementById("enigme");
    if (!enigme) return;

    // Texte de l'énigme (modifiable selon challenge)
    var texte = "Je peux t’enfermer ou te libérer. On me manipule, parfois avec un code, parfois avec une clé. Qui suis-je ?";
    var i = 0;

    function typeWriter() {
        if (i < texte.length) {
            enigme.textContent += texte.charAt(i);
            i++;
            setTimeout(typeWriter, 40);
        }
    }

    typeWriter();
});
