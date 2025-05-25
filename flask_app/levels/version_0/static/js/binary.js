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

// === Animation binaire style Matrix violet électrique ===
document.addEventListener("DOMContentLoaded", function () {
    // Sélectionne le canvas où dessiner les chiffres
    var canvas = document.getElementById("binaryCanvas");
    if (!canvas) return; // Si pas de canvas, on ne fait rien

    var ctx = canvas.getContext("2d");

    // Redimensionne automatiquement le canvas à la taille de la fenêtre
    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener("resize", resize);

    // Caractères à afficher (0 et 1)
    var chars = "01".split("");
    var fontSize = 18; // Taille de chaque caractère
    var columns = Math.floor(canvas.width / fontSize);

    // Initialisation de la "pluie" binaire
    var drops = [];
    for (var x = 0; x < columns; x++)
        drops[x] = 1;

    // Fonction qui dessine l'effet binaire à chaque frame
    function draw() {
        // Fond semi-transparent pour l'effet de trainée (violet très sombre)
        ctx.fillStyle = "rgba(88, 0, 110, 0.14)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Couleur des chiffres : violet électrique
        ctx.fillStyle = "#b800ff";
        ctx.font = fontSize + "px monospace";

        // Boucle sur chaque colonne/goutte
        for (var i = 0; i < drops.length; i++) {
            // Affiche un 0 ou 1 à une position donnée
            var text = chars[Math.floor(Math.random() * chars.length)];
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);

            // Remonte la goutte aléatoirement une fois en bas de l'écran
            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975)
                drops[i] = 0;
            drops[i]++;
        }
    }
    setInterval(draw, 45); // Rafraîchit toutes les 45 ms (~22 fps)
});
