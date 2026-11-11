# Cartographie interactive des accidents de vélo en France

Application de bureau développée en Python dans le cadre d'un projet universitaire en deuxième année de Science des Données, entre janvier et avril 2026.

L'objectif du projet est de **visualiser et gérer des données géolocalisées d'accidents de vélo en France**, à travers une interface graphique associant cartographie interactive et gestion de données.

## Fonctionnalités principales

- Visualisation des accidents sur une carte interactive avec **Folium**, avec des marqueurs différenciés selon la gravité.
- Consultation des informations détaillées des accidents à l'aide de fenêtres contextuelles (_popups_).
- Chargement et exploitation de données depuis des fichiers **CSV** ou une base **PostgreSQL**.
- Création d'une table et importation de données dans PostgreSQL.
- Saisie de nouveaux accidents à travers un formulaire graphique.

## Technologies utilisées

**Python** · Tkinter · Folium · pandas · PostgreSQL · psycopg2 · tkcalendar · CEF Python

## Aperçu de l'application

_Captures d'écran à ajouter prochainement._

- Interface principale et carte interactive
- Consultation des détails d'un accident
- Formulaire de saisie
- Gestion des données PostgreSQL

## Remarques

## Données et limites

Les données utilisées dans ce projet proviennent du jeu de données [Accidents de vélo — Koumoul](https://opendata.koumoul.com/datasets/accidents-velos), construit à partir des données d'accidents corporels de la circulation de l'ONISR (Fichier BAAC).

Le dossier `data/` n'est pas inclus dans le dépôt GitHub. Les fichiers CSV doivent être préparés selon la structure attendue par le programme.

Cette application a été réalisée dans un cadre universitaire et présente encore certaines limites techniques, notamment en matière de performances, de gestion des chemins de fichiers et de compatibilité de l'environnement d'exécution.
