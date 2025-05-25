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

// Animation binaire en fond style "hacker matrix" BLEU CYAN
document.addEventListener("DOMContentLoaded", function () {
    // Récupère le canvas
    var canvas = document.getElementById("binaryCanvas");
    if (!canvas) return; // Arrête si pas de canvas

    var ctx = canvas.getContext("2d");

    // Adapte la taille
    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener("resize", resize);

    // Chars binaires (0 et 1)
    var chars = "01";
    chars = chars.split("");

    var fontSize = 18;
    var columns = canvas.width / fontSize;

    // Un tableau pour chaque goutte de la matrice
    var drops = [];
    for (var x = 0; x < columns; x++)
        drops[x] = 1;

    // Dessine l'écran de code binaire façon matrix
    function draw() {
        // Fond semi-transparent pour l'effet de traînée
        ctx.fillStyle = "rgba(0, 50, 100, 0.14)"; // Bleu très sombre, trainée bleutée
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = "#00cfff"; // BLEU néon/cyan
        ctx.font = fontSize + "px monospace";

        for (var i = 0; i < drops.length; i++) {
            var text = chars[Math.floor(Math.random() * chars.length)];
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);

            // Si la goutte atteint le bas, chance de recommencer en haut
            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975)
                drops[i] = 0;
            drops[i]++;
        }
    }

    setInterval(draw, 45);
});
