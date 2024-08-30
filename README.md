Voici une description structurée des étapes nécessaires pour calculer l'angle de déviation d'un pénis à partir d'une simple photo prise par un smartphone :
1. Interface utilisateur avec Tkinter (Interface.py)
•	But : Fournir une interface graphique pour sélectionner une image, choisir la direction du pénis et lancer le traitement.
•	Fonctionnalités :
o	Sélectionner une image via une boîte de dialogue.
o	Choisir la direction du pénis (haut, bas, gauche, droite).
o	Lancer le traitement de l'image en cliquant sur un bouton.
o	Afficher des touches de commande pour ajuster les positions et visualiser les résultats.
o	Gérer les événements clavier pour ajuster les positions de points d'intérêt (P1 et P3) sur l'image.
2. Traitement de l'image et segmentation (Interface.py)
•	Traitement initial :
o	Charger l'image sélectionnée.
o	Convertir l'image en niveaux de gris.
o	Appliquer des filtres (médian, gaussien) pour améliorer la qualité.
o	Générer un squelette binaire de l'image pour simplifier la structure à des lignes fines.
•	Calcul des intersections :
o	Identifier les points d'intersection du squelette avec les bordures supérieure et inférieure (pour P1 et P3).
o	Calculer les points où les lignes verticales (ou horizontales) traversent le squelette.
3. Calculs géométriques (Calcul.py)
•	Détection des tangentes :
o	Utiliser la transformation de Hough pour détecter des lignes autour des points d'intérêt (P1 et P3) sur le squelette.
o	Calculer les vecteurs moyens des tangentes autour de ces points.
•	Calcul de l'angle de déviation :
o	Calculer l'angle entre les vecteurs tangents en utilisant le produit scalaire et les normes des vecteurs.
o	Déterminer l'angle entre les deux vecteurs tangents obtenus des points P1 et P3 après ajustement.
4. Visualisation et génération de résultats (Calcul.py)
•	Affichage des résultats :
o	Dessiner les lignes prolongées des vecteurs sur l'image.
o	Trouver l'intersection de ces vecteurs prolongés.
o	Calculer et afficher l'angle de déviation sur l'image.
o	Générer un rapport textuel des résultats, incluant l'angle de déviation calculé.
5. Génération de rapport (Interface.py et Calcul.py)
•	Rapport textuel :
o	Un rapport est généré avec les détails sur la direction choisie, les positions des points d'intérêt (P1 et P3), et l'angle de déviation.
o	Le rapport est sauvegardé dans le répertoire d'origine de l'image.
Synthèse :
Ce programme, via une interface utilisateur simple, permet de charger une image, de la traiter pour extraire son squelette, d'identifier des points clés, et de calculer l'angle de déviation du pénis. L'utilisateur peut interagir pour ajuster les points d'intérêt et visualiser les résultats en temps réel. Un rapport final est généré pour documenter les résultats.

