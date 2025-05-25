/*
=================================================================================
 FICHIER       : binary.js
 DESCRIPTION   : Animation fond binaire style "Matrix" pour v3 (rouge).
 AUTEUR        : Lysandre / Lysius
 DATE          : 14/02/25
 VERSION       : 3.0.0
 LICENCE       : Autre
=================================================================================

 HISTORIQUE :
 - 14/02/25 : [Lysius] Création du script.
 - 25/05/25 : [Lysius] Version commentée v3.

 USAGE :
 - À inclure dans le HTML via <script src="/static/js/binary.js"></script>

 CONTACT :
 - Email :    lysandrepro@gmail.com
 - GitHub :   https://github.com/lysandre84
 - Framagit : https://framagit.org/vialette

=================================================================================
*/

// Animation binaire Matrix vert pour fond de page
document.addEventListener("DOMContentLoaded", function () {
    // Récupère le canvas
    var canvas = document.getElementById("binaryCanvas");
    if (!canvas) return; // Arrête si pas de canvas

    var ctx = canvas.getContext("2d");

    // Fonction pour adapter la taille du canvas à la fenêtre
    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener("resize", resize);

    // Chiffres binaires à afficher
    var chars = "01";
    chars = chars.split("");

    var fontSize = 18;
    var columns = Math.floor(canvas.width / fontSize);

    // Tableau pour chaque goutte binaire
    var drops = [];
    for (var x = 0; x < columns; x++)
        drops[x] = 1;

    // Fonction pour dessiner la pluie binaire
    function draw() {
        // Fond semi-transparent vert/noir pour l'effet de trainée
        ctx.fillStyle = "rgba(20, 30, 5, 0.14)"; // Vert très sombre (ombre Matrix)
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = "#39ff14"; // Vert Matrix néon
        ctx.font = fontSize + "px monospace";

        for (var i = 0; i < drops.length; i++) {
            var text = chars[Math.floor(Math.random() * chars.length)];
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);

            // Remet la goutte tout en haut avec une proba
            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975)
                drops[i] = 0;
            drops[i]++;
        }
    }

    setInterval(draw, 45);
});
