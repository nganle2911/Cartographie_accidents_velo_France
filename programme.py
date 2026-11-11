# SAE4-VCOD-01 : Composant décisionnel Python leaflet
# Programme principal - 13/03/2026
########################################


## Importation des bibliothèques nécessaires
from datetime import datetime
import random
import os

# A MODIFIER : remplacer par le chemin du dossier qui contient le fichier programme.py sur votre PC
# os.chdir("")


# Tkinter
from tkinter import *
import tkinter as tk
from tkinter.filedialog import askopenfile,asksaveasfile
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox

# Calendrier pour saisir la date
import tkcalendar
from tkcalendar import DateEntry

# Données
import csv
import pandas as pd

# Connexion à la bdd
import psycopg2

# Folium
import folium
from folium.plugins import MarkerCluster

# Cef
from cefpython3 import cefpython as cef
import ctypes


## Déclaration des constantes
# Constantes pour la pallete de couleurs
CL_BLEU = "#125D98"
CL_NOIR = "#4A4947"
CL_VERT = "#729762"
CL_ROUGE = "#D75656"

# Constantes pour la police et la taille
TITRE = ("HelveticaI", 12, "bold")
TEXTE = "Helvetica 10"


## Création de la fenêtre Tkinter
maFenetre = Tk()
maFenetre.option_add("*Font", TEXTE) # ajouter la police pour toute l'application
maFenetre.title("Accidents de vélo en France")
maFenetre.geometry("1200x630")


## Déclaration des variables globales
# Pour la mode du chargement des données
mode_source = StringVar()
mode_source.set("csv") # mode par défault

# Pour la connexion à bdd
conn = None # connexion à PostgreSQL
df = None
nfichier = None


## Config pour la carte Folium : icône, marqueur
# Choix de l'icon en fonction de la gravité
def choixIcon(grv):
    if grv == 1 :
        icon = folium.CustomIcon(
            "image/icon_aucun_blesse.png",
            icon_size=(30, 30),
            icon_anchor=(15, 15),
            popup_anchor=(0, -12))
    elif grv == 2 :
        icon = folium.CustomIcon(
            "image/icon_blesse_grave.png",
            icon_size=(30, 30),
            icon_anchor=(15, 15),
            popup_anchor=(0, -12))
    elif grv == 3 :
        icon = folium.CustomIcon(
            "image/icon_blesse_hospitalise.png",
            icon_size=(30, 30),
            icon_anchor=(4, 29),
            popup_anchor=(12, -27))
    else :
        icon = folium.CustomIcon(
            "image/icon_blesse_leger.png",
            icon_size=(30, 30),
            icon_anchor=(4, 29),
            popup_anchor=(12, -27))

    return(icon)


# Fonction de création d'un marqueur
def creerMarqueur(acc):
    # Vérifier les champs lat et long
    if pd.isna(acc['lat']) or pd.isna(acc['long']):
        return

    dict_grv = {1: "Indemne", 2: "Tué", 3: "Blessé hospitalisé", 4: "Blessé léger"}
    grav = acc['grav']
    if pd.isna(grav):
        grav_texte = "Non renseigné"
    else:
        grav_texte = dict_grv.get(int(grav), "Non renseigné")


    dict_sexe = {1: "Masculin", 2: "Féminin"}
    # si sexe contient une valeur NaN , elle renvoie la valeur "non renseigné"
    sexe = acc['sexe']
    if pd.isna(sexe):
        sexe_texte = "Non renseigné"
    else:
        sexe_texte = dict_sexe.get(int(acc['sexe']), "Non renseigné")


    dict_col = {1: "Deux véhicules - frontale", 2: "Deux véhicules - par l'arrière", 3: "Deux véhiculs - par le côté", 4: "Trois véhicules et plus - en chaîne", 5: "Trois véhicules et plus - collisions multiples", 6: "Autre collision", 7: "Sans collision"}
    col = acc['col']
    if pd.isna(col):
        col_texte = "Non renseigné"
    else:
        col_texte = dict_col.get(int(acc['col']), "Non renseigné")

    dict_trajet = {1: "Domicile - Travail", 2: "Domicile  -école", 3: "Courses - achats", 4: "Utilisation professionnel", 5: "Promenade - Loisir", 9: "Autre"}
    trajet = acc['trajet']
    if pd.isna(trajet):
        trajet_texte = "Non renseigné"
    else:
        trajet_texte = dict_trajet.get(int(acc['trajet']), "Non renseigné")

    dict_lum = {1: "Plein jour", 2: "Crépuscule ou aube", 3: "Nuit sans éclairage", 4: "Nuit avec éclairage public non allumé", 5: "Nuit avec éclairage public allumé"}
    lum = acc['lum']
    if pd.isna(lum):
        lum_texte = "Non renseigné"
    else:
        lum_texte = dict_lum.get(int(acc['lum']), "Non renseigné")

    dict_atm = {1: "Normal", 2: "Pluie légère", 3: "Plui forte", 4: "Neige - grêle", 5: "Brouillard - fumée", 6: "Vent fort - tempête", 7: "Temps éblouissant", 8: "Temps couvert", 9: "Autre"}
    atm = acc['atm']
    if pd.isna(atm):
        atm_texte = "Non renseigné"
    else:
         atm_texte = dict_atm.get(int(acc['atm']), "Non renseigné")

    # Conversion des coordonnées en float en remplaçant la virgule par un point
    lat = float(str(acc['lat']).replace(',', '.'))
    long = float(str(acc['long']).replace(',', '.'))

    folium.Marker(
        location=[lat, long],
        icon=choixIcon(acc['grav']),
        popup=folium.Popup(
            "Date de l'accident : " + str(acc['date']) +
            "<br/>Heure de l'accident : " + str(acc['hrmn']) +
            "<br/>Age : " + str(acc['age']) +
            "<br/>Sexe : " + sexe_texte +
            "<br/>Gravité : " + grav_texte +
            "<br/>Type de collision : " + col_texte +
            "<br/>Motif de déplacement : " + trajet_texte +
            "<br/>Luminosité : " + lum_texte +
            "<br/>Conditions atmosphériques : " + atm_texte,
            max_width=1000
        )
    ).add_to(marker_cluster)


## Fonction qui agit lorqu'on ouvre un fichier csv
def ouvrir():
    listeextensions=[("Fichiers csv", "*.csv") ]
    chemin=filedialog.askopenfilename(filetypes=listeextensions,defaultextension=listeextensions)

    if chemin :
        global nfichier

        nfichier = chemin.split("/")[-1]
        nom_f.config(text = nfichier, fg="blue")

        global df
        df = pd.read_csv("data/"+nfichier, low_memory=False)

        # Supprimer les lignes où lat ou long ayant des valeurs manquantes
        df_filtrage = df.dropna(subset=["lat", "long"])
        df_filtrage = df_filtrage.reset_index(drop=True)

        for i, row in df_filtrage.iterrows():
            creerMarqueur(row)

        map.save("carte.html")
        browser_frame.browser.Reload()


## Fonction qui affiche le bloc de la connexion de bdd si la mode bdd est choisie
def afficher_config_bdd():
    if mode_source.get() == "bdd":
        label_bdd.place(x=5, y=130, width=530, height=350)
        label_csv.place_forget()
    else:
        label_bdd.place_forget() # cacher le bloc de config bdd si la mode_source="bdd" n'est pas choisie
        label_csv.place(x=5, y=130, width=530, height=100)


## Fonction pour se connecter à la base de données
def seconnecter():
    le_host = e_adresse.get()
    le_user = e_nom.get()
    le_password = e_mdp.get()
    le_bddname = e_nombdd.get()

    global conn,cursor

    try:
        conn = psycopg2.connect(user=le_user, password=le_password, host=le_host, port="5432", database=le_bddname)
        cursor = conn.cursor()

        if cursor:
            l_etat_conn.config(text="Connexion réussie",fg=CL_VERT)
            # cursor = None

    except Exception as e:
        l_etat_conn.config(text="Connexion échouée, erreur dans les paramètres",fg=CL_ROUGE)
        print(e)
        cursor = None

## Fonction pour se déconnecter de la base de données
def sedeconnecter():
    global conn, cursor

    try:
        if conn:
            cursor.close()
            conn.close()
            conn = None
            cursor = None
            l_etat_conn.config(text="Déconnexion réussie", fg=CL_VERT)
        else:
            l_etat_conn.config(text="Pas de connexion active", fg=CL_ROUGE)

    except Exception as e:
        print("Erreur lors de la déconnexion :", e)
        l_etat_conn.config(text="Erreur lors de la déconnexion", fg=CL_ROUGE)

## Fonction pour créer une table vierge au format Postgres
# Drop table if exists accidents =>  Si la table existe déjà elle sera détruite auparavant.
def creer_table_bdd():
    try:
        cursor.execute("""
            DROP TABLE IF EXISTS accidents;
            CREATE TABLE accidents (
                Num_Acc VARCHAR(50),
                date VARCHAR(50),
                an INTEGER,
                mois VARCHAR(20),
                jour VARCHAR(20),
                hrmn VARCHAR(20),
                dep VARCHAR(5),
                com VARCHAR(10),
                lat FLOAT,
                long FLOAT,
                agg INTEGER,
                int INTEGER,
                col INTEGER,
                lum INTEGER,
                atm INTEGER,
                catr INTEGER,
                circ INTEGER,
                nbv INTEGER,
                prof INTEGER,
                plan INTEGER,
                lartpc INTEGER,
                larrout INTEGER,
                surf INTEGER,
                infra INTEGER,
                situ INTEGER,
                grav INTEGER,
                sexe INTEGER,
                age INTEGER,
                trajet INTEGER,
                secuexist INTEGER,
                equipement INTEGER,
                obs INTEGER,
                obsm INTEGER,
                choc INTEGER,
                manv INTEGER,
                vehiculeid VARCHAR(50),
                typevehicules INTEGER,
                manoeuvehicules VARCHAR(20),
                numVehicules INTEGER
            );
        """)
        conn.commit() # sauvegarder dans la bdd

        l_etat_table.config(text="Table créée avec succès. Veuillez voir la table dans Postgres!", fg=CL_VERT)
    except Exception as e:
        print("Erreur dans la création de la table :", e)
        l_etat_table.config(text="Erreur dans la création de la table", fg=CL_ROUGE)

## Fonction pour déverser des données d'un fichier CSV dans la base de données
def deverser_csv_bdd():
    listeextensions=[("Fichiers csv", "*.csv")]
    chemin=filedialog.askopenfilename(filetypes=listeextensions, defaultextension=listeextensions)

    if chemin:
        try:
            df_importe = pd.read_csv(chemin, low_memory=False)

            # Parcourir df_importe pour ajouter ligne par ligne dans bdd
            for i, ligne in df_importe.iterrows():

                # Vérifier et convertir chaque valeur de la ligne
                valeurs_de_ligne = []
                for val in ligne:
                    # vérifier si la valeur (val) est vide => on ajoute None dans Postgres
                    if pd.isna(val):
                        valeurs_de_ligne.append(None)
                    else:
                        if type(val) == str:
                            val = val.strip()
                            if val.startswith('#'):
                                # erreur Excel comme #VALEURMULT => None
                                valeurs_de_ligne.append(None)
                            elif val.isdigit():
                                valeurs_de_ligne.append(int(val))
                            elif '/' in val:
                                valeurs_de_ligne.append(int(val.split('/')[0].strip()))
                            elif ',' in val:
                                valeurs_de_ligne.append(float(val.replace(',', '.')))
                            elif '.' in val:
                                valeurs_de_ligne.append(float(val))
                            else:
                                valeurs_de_ligne.append(val)
                        elif 'int' in str(type(val)):
                            # numpy int => convertir en int Python normal
                            valeurs_de_ligne.append(int(val))
                        elif 'float' in str(type(val)):
                            # numpy float => convertir en int si sans décimale
                            v = float(val)
                            if v == int(v):
                                valeurs_de_ligne.append(int(v))
                            else:
                                valeurs_de_ligne.append(v)
                        else:
                            valeurs_de_ligne.append(val)

                cursor.execute("""
                    INSERT INTO accidents VALUES(
                        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s,%s,%s,%s
                    )
                """, valeurs_de_ligne)

            conn.commit()
            l_etat_deverser.config(text="Importation réussie! Veuillez voir dans Posgres!", fg=CL_VERT)

        except Exception as e:
            l_etat_deverser.config(text="Erreur dans l'importation: " + str(e), fg=CL_ROUGE)

## Fonction qui charge des données depuis la base de données Postgres
def charger_depuis_bdd():
    try:
        # Requête pour la récupération toutes les lignes de la table accidents
        cursor.execute("SELECT * FROM accidents")
        lignes = cursor.fetchall()

        # Parcourir lignes en créant un marqueur sur la carte
        for lig in lignes:
            acc = {
                'lat': lig[8],
                'long': lig[9],
                'grav': lig[25],
                'date': lig[1],
                'hrmn': lig[5],
                'age' : lig[27],
                'sexe': lig[26],
                'col': lig[12],
                'lum': lig[13],
                'atm': lig[14],
                'trajet': lig[28]
            }
            creerMarqueur(acc)

        # Sauvegarder la carte et recharger
        map.save("carte.html")
        browser_frame.browser.Reload()

    except Exception as e:
        print("Erreur chargement BDD: ", e)


## Fonction qui permet d'ouvrir le formulaire (un fenêtre séparé) pour ajouter un nouvel accident
def ouvrir_formulaire():
    formulaire = Toplevel(maFenetre)
    formulaire.title("Ajouter un nouvel accident")
    formulaire.geometry("1100x600")
    formulaire.grab_set() # empêche l'utilisateur d'interagir avec la fenêtre parent

    # Titre
    Label(formulaire, text="NOUVEL ACCIDENT DE VELO", fg=CL_BLEU, font=TITRE, bg="#f0f0f0").pack(pady=10)

    # Frame qui contient canvas + scrollbar
    frame = Frame(formulaire)
    frame.pack(fill="both", expand=True)
    frame.config(bg="#f0f0f0")

    # Canvas et scrollbar dans frame
    canvas = Canvas(frame)
    scrollbar = Scrollbar(frame, orient=VERTICAL, command=canvas.yview, width=25)
    canvas.config(yscrollcommand=scrollbar.set, scrollregion=(0,0,500,1500))
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Frame intérieur dans le canvas
    frame_interieur = Frame(canvas)
    canvas.create_window((0,0), window=frame_interieur, anchor="nw")

    ### Date de l'accident
    # Le titre
    Label(frame_interieur, text="Temps", fg=CL_NOIR, font=TITRE).pack(anchor="w", padx=10, pady=(10,0))
    # La ligne séparateur
    Frame(frame_interieur, bg=CL_NOIR, height=2).pack(fill="x", padx=10)

    # Bloc date qui contient tous les champs pour le temps : date, heure
    bloc_date = Frame(frame_interieur)
    bloc_date.pack(fill="x", padx=10)

    # Date avec le calendrier
    frame_date = Frame(bloc_date)
    frame_date.grid(row=0, column=0, pady=5, sticky="w")
    Label(frame_date, text="Date (JJ/MM/AAAA) :").pack(side="left")
    Label(frame_date, text="*", fg=CL_ROUGE, font=TITRE).pack(side="left")
    e_date = DateEntry(bloc_date, width=20, date_pattern="dd/mm/yyyy", locale="fr_FR")
    e_date.grid(row=0, column=1, pady=5)

    # Heure
    frame_heure = Frame(bloc_date)
    frame_heure.grid(row=0, column=2, pady=5, sticky="w", padx=(20,0))
    Label(frame_heure, text="Heure (HH:MM) :").pack(side="left")
    Label(frame_heure, text="*", fg=CL_ROUGE, font=TITRE).pack(side="left")
    e_hm = Entry(bloc_date, width=20)
    e_hm.grid(row=0, column=3, pady=5)

    ### Localisation
    Label(frame_interieur, text="Localisation", fg=CL_NOIR, font=TITRE).pack(anchor="w", padx=10, pady=(10,0))
    Frame(frame_interieur, bg=CL_NOIR, height=2).pack(fill="x", padx=10)

    # Bloc localisation qui contient tous les champs pour la localisation : commune, lat, long
    bloc_local = Frame(frame_interieur)
    bloc_local.pack(fill="x", padx=10)

    # Commune
    frame_com = Frame(bloc_local)
    frame_com.grid(row=0, column=0, pady=5, sticky="w")
    Label(frame_com, text="Code de la commune :").pack(side="left")
    Label(frame_com, text="*", fg=CL_ROUGE, font=TITRE).pack(side="left")
    e_com = Entry(bloc_local, width=20)
    e_com.grid(row=0, column=1, pady=5)

    # Latitude
    frame_lat = Frame(bloc_local)
    frame_lat.grid(row=1, column=0, pady=5, sticky="w")
    Label(frame_lat, text="Latitude :").pack(side="left")
    Label(frame_lat, text="*", fg=CL_ROUGE, font=TITRE).pack(side="left")
    e_lat = Entry(bloc_local, width=20)
    e_lat.grid(row=1, column=1, pady=5)

    # Longitude
    frame_long = Frame(bloc_local)
    frame_long.grid(row=1, column=2, pady=5, sticky="w", padx=(20,0))
    Label(frame_long, text="Longitude :").pack(side="left")
    Label(frame_long, text="*", fg=CL_ROUGE, font=TITRE).pack(side="left")
    e_long = Entry(bloc_local, width=20)
    e_long.grid(row=1, column=3, pady=5)

    ### Informations sur l'accident
    Label(frame_interieur, text="Informations sur l'accident", fg=CL_NOIR, font=TITRE).pack(anchor="w", padx=10, pady=(10,0))
    Frame(frame_interieur, bg=CL_NOIR, height=2).pack(fill="x", padx=10)

    # Bloc caractéristique qui contient tous les champs pour les caractéristiques de l'accident
    bloc_info = Frame(frame_interieur)
    bloc_info.pack(fill="x", padx=10)

    # Agglomération
    Label(bloc_info, text="Agglomération :").grid(row=0, column=0, pady=5, sticky="w")
    liste_agg = ["1. Hors agglomération", "2. En agglomération"]
    combo_agg = ttk.Combobox(bloc_info, values=liste_agg,  width=40)
    combo_agg.grid(row=0, column=1, sticky="w")

    # Type d'intersection - -1 = Non renseigné
    Label(bloc_info, text = "Type d'intersection :").grid(row=0, column=2, pady=5, sticky="w", padx=(20,0))
    liste_int = ["1. Hors intersection", "2. Intersection en X", "3. Intersection en T","4. Intersection en Y","5. Plus de 4 branches","6. Giratoire","7. Place", "8. Passage à niveau", "9. Autre Intersection"]
    combo_int = ttk.Combobox(bloc_info, values=liste_int,  width=40)
    combo_int.grid(row=0, column=3, sticky="w")

    # Type de collision - -1 = Non renseigné
    frame_col = Frame(bloc_info)
    frame_col.grid(row=1, column=0, pady=5, sticky="w")
    Label(frame_col, text = "Type de collision :").pack(side="left")
    Label(frame_col, text="*", fg=CL_ROUGE, font=TITRE).pack(side="left")
    liste_col = ["1. Deux véhicules - frontale", "2. Deux véhicules - par l'arrière", "3. Deux véhiculs - par le côté", "4. Trois véhicules et plus - en chaîne", "5. Trois véhicules et plus - collisions multiples", "6. Autre collision", "7. Sans collision"]
    combo_col = ttk.Combobox(bloc_info, values=liste_col, width=40)
    combo_col.grid(row=1, column=1, sticky="w")

    # Luminosité - -1 = Non renseigné
    Label(bloc_info, text = "Luminosité :").grid(row=1, column=2, pady=5, sticky="w", padx=(20,0))
    liste_lum = ["1. Plein jour", "2. Crépuscule ou aube", "3. Nuit sans éclairage", "4. Nuit avec éclairage public non allumé", "5. Nuit avec éclairage public allumé"]
    combo_lum = ttk.Combobox(bloc_info, values=liste_lum,  width=40)
    combo_lum.grid(row=1, column=3, sticky="w")

    # Conditions atmosphériques - -1 = Non renseigné
    Label(bloc_info, text = "Conditions atmosphériques :").grid(row=2, column=0, pady=5, sticky="w")
    liste_atm = ["1. Normal", "2. Pluie légère", "3. Plui forte","4. Neige - grêle", "5. Brouillard - fumée", "6. Vent fort - tempête", "7. Temps éblouissant", "8. Temps couvert", "9. Autre"]
    combo_atm = ttk.Combobox(bloc_info, values=liste_atm, width=40)
    combo_atm.grid(row=2, column=1, sticky="w")

    # Catégorie route
    Label(bloc_info, text = "Catégorie route :").grid(row=2, column=2, pady=5, sticky="w", padx=(20,0))
    liste_catr = ["1. Autoroute", "2. Route nationale", "3. Route départementale","4. Voie communale","5. Hors réseau public", "6. Parc de stationnement", "7. Route de métropole urbaine", "9. Autre"]
    combo_catr = ttk.Combobox(bloc_info, values=liste_catr,  width=40)
    combo_catr.grid(row=2, column=3, sticky="w")

    # Circulation - -1 = Non renseigné
    Label(bloc_info, text = "Circulation :").grid(row=3, column=0, pady=5, sticky="w")
    liste_circ = ["1. A sens unique", "2. Bidirectionnelle","3. A chaussées séparées","4. Avec voies d'affectation variable", "6. Parc de stationnement", "7. Route de métropole urbaine", "9. Autre"]
    combo_circ = ttk.Combobox(bloc_info, values=liste_circ,  width=40)
    combo_circ.grid(row=3, column=1, sticky="w")

    # Nombre de voies
    Label(bloc_info, text = "Nombre de voies :").grid(row=3, column=2, pady=5, sticky="w", padx=(20,0))
    e_nbv = Entry(bloc_info, width=20)
    e_nbv.grid(row=3, column=3, sticky="w")

    # Profil en long - -1 = Non renseigné
    Label(bloc_info, text = "Profil en long :").grid(row=4, column=0, pady=5, sticky="w")
    liste_prof = ["1. Plat", "2. Pente","3. Sommet de côté","4. Bas de côté"]
    combo_prof = ttk.Combobox(bloc_info, values=liste_prof, width=40)
    combo_prof.grid(row=4, column=1, sticky="w")

    # Tracé en plan
    Label(bloc_info, text = "Tracé en plan :").grid(row=4, column=2, pady=5, sticky="w", padx=(20,0))
    liste_plan = ["1. Partie rectiligne", "2. En courbe à gauche","3. En courbe à droite","4. En 'S'"]
    combo_plan = ttk.Combobox(bloc_info, values=liste_plan, width=40)
    combo_plan.grid(row=4, column=3, sticky="W")

    # Largeur TPC
    l_lartpc = Label(bloc_info, text = "Largeur terre-plein central (en m):").grid(row=5, column=0, pady=5, sticky="w")
    e_lartpc = Entry(bloc_info, width=20)
    e_lartpc.grid(row=5, column=1, sticky="W")

    # Largeur de la chaussée
    Label(bloc_info, text = "Largeur de la chaussée (en m) :").grid(row=5, column=2, pady=5, sticky="w", padx=(20,0))
    e_larrout = Entry(bloc_info, width=20)
    e_larrout.grid(row=5, column=3, sticky="W")

    # Etat de la surface
    Label(bloc_info, text = "Etat de la surface :").grid(row=6, column=0, pady=5, sticky="w")
    liste_surf = ["1. Normale", "2. Mouillée","3. Flaques","4. Inondée", "5. Enneigée", "6. Boue", "7. Verglacée", "8. Corp Gras - huile", "9. Autre"]
    combo_surf = ttk.Combobox(bloc_info, values=liste_surf, width=40)
    combo_surf.grid(row=6, column=1, sticky="W")

    # Aménagement - infrastructure
    l_infra = Label(bloc_info, text = "Aménagement - Infrastructure :").grid(row=6, column=2, pady=5, sticky="w", padx=(20,0))
    liste_infra = ["0. Aucun" ,"1. Souterrain - tunnel", "2. Pont - autopont","3. Bretelle d'échangeur ou de raccordement","4. Voie ferrée", "5. Carrefour aménagé", "6. Zone piétonne", "7. Zone de péage", "8. Chantier", "9. Autre"]
    combo_infra = ttk.Combobox(bloc_info, values=liste_infra, width=40)
    combo_infra.grid(row=6, column=3, sticky="W")

    # Situation
    Label(bloc_info, text = "Situation : ").grid(row=7, column=0, pady=5, sticky="w")
    liste_situ = ["0. Aucun" ,"1. Sur chaussée", "2. Sur bande d'arrêt d'urgence","3. Sur accotement","4. Sur troittoir", "5. Sur piste cyclable", "6. Sur autre voie spéciale", "7. Autres"]
    combo_situ = ttk.Combobox(bloc_info, values=liste_situ, width=40)
    combo_situ.grid(row=7, column=1, sticky="W")

    # Choc subi
    Label(bloc_info, text="Choc subi : ").grid(row=7, column=2, pady=5, sticky="w", padx=(20,0))
    liste_choc = ["0. Aucun","1. Avant", "2. Avant droit", "3. Avant gauche","4. Arrière","5. Arrière droit","6. Arrière gauche","7. Côté droit", "8. Côté gauche", "9. Chocs multiples (tonneaux)"]
    combo_choc = ttk.Combobox(bloc_info, values=liste_choc, width=40)
    combo_choc.grid(row=7, column=3, sticky="W")

    # Obstacle heurté fixe == refaire ici
    Label(bloc_info, text = "Obstacle fixe heurté :").grid(row=8, column=0, pady=5, sticky="w")
    liste_obs = ["0. Sans object","1. Véhicule en stationnement", "2. Arbre", "3. Glissière métallique", "4. Glissière béton", "5. Autre glissière", "6. Bâtiment, mur, pile de pont", "7. Signalisation ou poste d'appel d'urgence" ,"8. Poteau", "9. Mobilier urbain", "10. Parapet", "11. Ilot, refuge, borne haute", "12. Trottoir", "13. Fossé", "14. Autre obstacle fixe", "16. Sans obstacle fixe", "17. Buse"]
    combo_obs = ttk.Combobox(bloc_info, values=liste_obs, width=40)
    combo_obs.grid(row=8, column=1, sticky="W")

    # Obstacle mobile == refaire ici
    Label(bloc_info, text = "Obstacle mobile :").grid(row=8, column=2, pady=5, sticky="w", padx=(20,0))
    liste_obsm = ["0. Aucun","1. Piéton", "2. Véhicule", "3. Véhicule sur rail", "4. Animal domestique", "5. Animal sauvage", "9. Autre"]
    combo_obsm = ttk.Combobox(bloc_info, values=liste_obsm, width=40)
    combo_obsm.grid(row=8, column=3, sticky="W")


    ### Informations sur la victime
    Label(frame_interieur, text="Informations sur la victime", fg=CL_NOIR, font=TITRE).pack(anchor="w", padx=10, pady=(10,0))
    Frame(frame_interieur, bg=CL_NOIR, height=2).pack(fill="x", padx=10)

    # Bloc victime qui contient tous les champs pour les infos de la victime
    bloc_victime = Frame(frame_interieur)
    bloc_victime.pack(fill="x", padx=10)

    # Gravité
    frame_grav = Frame(bloc_victime)
    frame_grav.grid(row=0, column=0, pady=5, sticky="w")
    Label(frame_grav, text = "Gravité : ").pack(side="left")
    Label(frame_grav, text = "*", fg=CL_ROUGE, font=TITRE).pack(side="left")
    liste_grv = ["1. Indemne", "2. Tué","3. Blessé hospitalisé","4. Blessé leger"]
    combo_grv = ttk.Combobox(bloc_victime, values=liste_grv)
    combo_grv.grid(row=0, column=1, sticky="W")

    # Sexe
    frame_sexe = Frame(bloc_victime)
    frame_sexe.grid(row=0, column=2, pady=5, sticky="w", padx=(20,0))
    Label(frame_sexe, text = "Sexe :").pack(side="left")
    Label(frame_sexe, text = "*", fg=CL_ROUGE, font=TITRE).pack(side="left")
    liste_sexe = ["1. Masculin", "2. Féminin"]
    combo_sexe = ttk.Combobox(bloc_victime, values=liste_sexe)
    combo_sexe.grid(row=0, column=3, sticky="W")

    # Age
    frame_age = Frame(bloc_victime)
    frame_age.grid(row=1, column=0, pady=5, sticky="w")
    Label(frame_age, text = "Age : ").pack(side="left")
    Label(frame_age, text = "*", fg=CL_ROUGE, font=TITRE).pack(side="left")
    e_age = Entry(bloc_victime)
    e_age.grid(row=1, column=1, sticky="W")

    # Motif de déplacement
    frame_trajet = Frame(bloc_victime)
    frame_trajet.grid(row=1, column=2, pady=5, sticky="w", padx=(20,0))
    Label(frame_trajet, text = "Motif de déplacement : ").pack(side="left")
    Label(frame_trajet, text = "*", fg=CL_ROUGE, font=TITRE).pack(side="left")
    liste_trajet = ["1. Domicile-Travail", "2. Domicile-école", "3. Courses-achats", "4. Utilisation professionnel", "5. Promenade-Loisir","9. Autre"]
    combo_trajet = ttk.Combobox(bloc_victime, values=liste_trajet, width=40)
    combo_trajet.grid(row=1, column=3, sticky="W")

    # Usage de sécurité
    Label(bloc_victime, text = "Usage de sécurité : ").grid(row=2, column=0, pady=5, sticky="w")
    liste_secuexist = ["1. Oui", "2. Non", "3. Non déterminable"]
    combo_secuexist = ttk.Combobox(bloc_victime, values=liste_secuexist, width=40)
    combo_secuexist.grid(row=2, column=1, sticky="W")

    # Equipement
    Label(bloc_victime, text = "Equipement : ").grid(row=2, column=2, pady=5, sticky="w", padx=(20,0))
    liste_equipement = ["0. Aucun équipement","1. Ceinture", "2. Casque", "3. Dispositif enfants", "4. Gilet Réfléchissant", "5. Airbag (2RM/3RM)", "6. Gants (2RM/3RM)", "7.Gants + Airbag (2RM/3RM)", "8. Non déterminable", "9. Autre"]
    combo_equipement = ttk.Combobox(bloc_victime, values=liste_equipement, width=40)
    combo_equipement.grid(row=2, column=3, sticky="W")

    ### Informations sur les autres véhicules liés à l'accident
    Label(frame_interieur, text="Informations sur les autres véhicules liés à l'accident", fg=CL_NOIR, font=TITRE).pack(anchor="w", padx=10, pady=(10,0))
    Frame(frame_interieur, bg=CL_NOIR, height=2).pack(fill="x", padx=10)

    # Bloc autre qui contient tous les champs pour les informations sur les autres véhicules liés à l'accident
    bloc_autre = Frame(frame_interieur)
    bloc_autre.pack(fill="x", padx=10)

    # Manoeuvre avant l'accident
    Label(bloc_autre, text = "Manoeuvre avant l'accident :").grid(row=0, column=0, pady=5, sticky="w")
    liste_manv = ["0. Inconnue","1. Sans changement de direction", "2. Même sens, même file","3. Entre 2 files", "4. Marche arrière", "5. Contre sens", "6. En franchissant le terre-plein central", "7. Dans le couloir bus, dans le même sens" ,"8. Dans le couloir bus, dans le sens inverse", "9. En s'insérant", "10. Demi-tour sur la chaussée", "11. Changement de file à gauche", "12. Changement de file à droite", "13. Déporté à gauche", "14. Déporté à droite", "15. Tournant à gauche", "16. Tournant à droite", "17. Dépassant à gauche", "18. Dépassant à droite", "19. Traversant la chaussée", "20. Stationnement", "21. Evitemment", "22. Ouverture de porte", "23. Arrêt", "25. Circulant sur troittoir", "26. Autre manoeuvre"]
    combo_manv = ttk.Combobox(bloc_autre, values=liste_manv, width=40)
    combo_manv.grid(row=0, column=1, sticky="W")

    # Type des autres véhicules
    Label(bloc_autre, text = "Type des autres véhicules :").grid(row=0, column=2, pady=5, sticky="w", padx=(20,0))
    liste_typevehicules = ["0. Indeterminable","1. Bicyclette", "2. Cyclomoteur < 50cm3", "3. Voiturette", "4. Scooteur immatriculé", "5. Motocyclette", "6. Side car", "7. Vl seul" ,"8. Vl + Caravane", "9. Vl + remorque", "10. VU seul 1,5T <= PTAC <= 3,5T", "11. VU (10) + caravane", "12. VU (10) + remorque", "13. Pl seul 3,5T", "14. Pl seul > 7,5T", "15. Pl > 3,5T + remorque", "16. Tracteur routier seul", "17. Tracteur routier + semi-remorque", "18. Transport en commun","19. Tramway", "20. Engin spécial", "21. Tracteur agricole", "30. Scooter < 50cm3", "31. Motocyclette > 50cm3 et <= 125cm3", "32. Scooter > 50cm3 et <= 125m3", "33. Motocyclette > 125m3", "34. Scooter > 125m3", "35. Quad léger <= 50cm3", "36. Quad lourd > 50cm3", "37. Autobus", "38. Autocar", "39. Train", "40. Autre"]
    combo_typevehicules = ttk.Combobox(bloc_autre, values=liste_typevehicules, width=40)
    combo_typevehicules.grid(row=0, column=3, sticky="W")

    # Manoeuvre du véhicule lié à l'accident
    Label(bloc_autre, text="Manoeuvre du véhicule lié à l'accident : ").grid(row=1, column=0, pady=5, sticky="w")
    combo_manoeuvehicule = ttk.Combobox(bloc_autre, values=liste_manv, width=40)
    combo_manoeuvehicule.grid(row=1, column=1, sticky="W")

    # Nombre d'autres véhicules lié à l'accident
    Label(bloc_autre, text="Nombre d'autres véhicules : ").grid(row=1, column=2, pady=5, sticky="w", padx=(20,0))
    e_nbvehi = Entry(bloc_autre, width=20)
    e_nbvehi.grid(row=1, column=3, sticky="W")

    # Mettre tous les champs à saisir dans un dictionnaire afin de les récupérer quand on clique sur le bouton "Ajouter"
    champs_recuperes = {
        'e_date': e_date,
        'e_hm': e_hm,
        'e_com': e_com,
        'e_lat': e_lat,
        'e_long': e_long,
        'combo_agg': combo_agg,
        'combo_int': combo_int,
        'combo_col': combo_col,
        'combo_lum': combo_lum,
        'combo_atm': combo_atm,
        'combo_catr': combo_catr,
        'combo_circ': combo_circ,
        'e_nbv': e_nbv,
        'combo_prof': combo_prof,
        'combo_plan': combo_plan,
        'e_lartpc': e_lartpc,
        'e_larrout': e_larrout,
        'combo_surf': combo_surf,
        'combo_infra': combo_infra,
        'combo_situ': combo_situ,
        'combo_choc': combo_choc,
        'combo_obs': combo_obs,
        'combo_obsm': combo_obsm,
        'combo_grv': combo_grv,
        'combo_sexe': combo_sexe,
        'e_age': e_age,
        'combo_trajet': combo_trajet,
        'combo_secuexist': combo_secuexist,
        'combo_equipement': combo_equipement,
        'combo_manv': combo_manv,
        'combo_typevehicules': combo_typevehicules,
        'combo_manoeuvehicule': combo_manoeuvehicule,
        'e_nbvehi': e_nbvehi
    }

    ### Boutons pour saisir le nouvel accident et opur annuler le formulaire
    groupe_boutons = Frame(frame_interieur)
    groupe_boutons.pack(pady=30)

    btn_valider = Button(groupe_boutons, text="Ajouter", bg=CL_VERT, font=TITRE, fg="white", width=12, command=lambda: ajouterSaisit(champs_recuperes, formulaire))
    btn_valider.pack(side="left", padx=10)

    btn_annuler = Button(groupe_boutons, text="Annuler", bg=CL_ROUGE, font=TITRE, fg="white", width=12, command=formulaire.destroy)
    btn_annuler.pack(side="right", padx=10)


## Fonction qui renvoie None si l'utilisateur ne saisit rien, sinon elle renvoie la valeur saisie - pour la liste déroulante de comobox
def recuperer_valeur_de_comobox(cle, champs_recuperes):
    val = champs_recuperes[cle].get()
    val_case = ""

    if val == "":
        val_case = None
    else:
        val_case = int(val.split(".")[0])
    return val_case

## Fonction qui renvoie None si l'utilisateur ne saisit rien, sinon elle renvoie la valeur saisie - pour les Entry
def recuperer_val_de_entry(cle, champs_recuperes):
    val = champs_recuperes[cle].get()
    val_case = ""

    if val == "":
        val_case = None
    else:
        val_case = int(val)
    return val_case


## Fonction qui permet de valider et d'ajouter un nouvel accident
def ajouterSaisit(champs_recuperes, formulaire):
    # Vérifier que les champs obligatoires sont remplis
    # s'il y a des champs qui sont manquants, une notification s'affiche
    champs_obligatoires = {
        'e_date': "Date",
        'e_hm': "Heure",
        'e_lat': "Latitude",
        'e_long': "Longitude",
        'e_com': "Commune",
        'combo_grv': "Gravité",
        'combo_col' : "Type de collision",
        'e_age' : "Age",
        'combo_sexe': "Sexe",
        'combo_trajet': "Motif de déplacement"
    }

    for cle, champ in champs_obligatoires.items():
        if champs_recuperes[cle].get() == "":
            messagebox.showwarning("Champ manquant", "Veuillez remplir le champ: " + champ)
            return

    # Récupérer la date
    date_saisie = datetime.strptime(champs_recuperes['e_date'].get(), "%d/%m/%Y")

    jours_semaine = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    t_mois = ["janvier", "févirer", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

    an = date_saisie.year
    mois = t_mois[date_saisie.month-1]
    jour = jours_semaine[date_saisie.weekday()]
    date = str(an) + "-" + str(date_saisie.month) + "-" + str(date_saisie.day)

    # Récupérer la commune et le département à partir du champ de la commune
    com = champs_recuperes['e_com'].get()
    dep = com[:2]

    # Récupérer tous les champs
    hrmn = champs_recuperes['e_hm'].get() # heure
    lat = float(champs_recuperes['e_lat'].get()) # latitude
    long = float(champs_recuperes['e_long'].get()) # longitude

    agg = recuperer_valeur_de_comobox('combo_agg', champs_recuperes)
    inter = recuperer_valeur_de_comobox('combo_int', champs_recuperes)
    col = recuperer_valeur_de_comobox('combo_col', champs_recuperes)
    lum = recuperer_valeur_de_comobox('combo_lum', champs_recuperes)
    atm = recuperer_valeur_de_comobox('combo_atm', champs_recuperes)
    catr = recuperer_valeur_de_comobox('combo_catr', champs_recuperes)
    circ = recuperer_valeur_de_comobox('combo_circ', champs_recuperes)
    nbv =  recuperer_val_de_entry('e_nbv', champs_recuperes)
    prof = recuperer_valeur_de_comobox('combo_prof', champs_recuperes)
    plan = recuperer_valeur_de_comobox('combo_plan', champs_recuperes)
    lartpc = recuperer_val_de_entry('e_lartpc', champs_recuperes)
    larrout = recuperer_val_de_entry('e_larrout', champs_recuperes)
    surf = recuperer_valeur_de_comobox('combo_surf', champs_recuperes)
    infra = recuperer_valeur_de_comobox('combo_infra', champs_recuperes)
    situ = recuperer_valeur_de_comobox('combo_situ', champs_recuperes)
    grav = recuperer_valeur_de_comobox('combo_grv', champs_recuperes)
    sexe = recuperer_valeur_de_comobox('combo_sexe', champs_recuperes)
    age = recuperer_val_de_entry('e_age', champs_recuperes)
    trajet = recuperer_valeur_de_comobox('combo_trajet', champs_recuperes)
    secuexist = recuperer_valeur_de_comobox('combo_secuexist', champs_recuperes)
    equipement = recuperer_valeur_de_comobox('combo_equipement', champs_recuperes)
    obs = recuperer_valeur_de_comobox('combo_obs', champs_recuperes)
    obsm = recuperer_valeur_de_comobox('combo_obsm', champs_recuperes)
    choc = recuperer_valeur_de_comobox('combo_choc', champs_recuperes)
    manv = recuperer_valeur_de_comobox('combo_manv', champs_recuperes)
    typevehicule = recuperer_valeur_de_comobox('combo_typevehicules', champs_recuperes)
    manoeuvehicules = recuperer_valeur_de_comobox('combo_manoeuvehicule', champs_recuperes)
    numVehicules = recuperer_val_de_entry('e_nbvehi', champs_recuperes)


    # Générer le numéro d'accident Num_Acc
    num_aleatoire = random.randint(1, 99999999)
    num_acc = str(an) + str(num_aleatoire)

    # Gérer l'identifiant du véhicule
    numa = random.randint(1, 999)
    vehiculeid = num_acc + str(numa)

    # Vérifier que l'identifiant du véhicule n'existe pas déjà selon le mode choisi : CSV ou BDD
    if mode_source.get() == "csv":
        # Vérifier si dataframe df existe
        if df is not None:
            # Vérifier que le num_accident n'existe pas déjà
            while num_acc in df["Num_Acc"]:
                num_aleatoire = random.randint(1, 99999999)
                num_acc = str(an) + str(num_aleatoire)
    else:
        # Vérifier dans la bdd
        cursor.execute("SELECT Num_Acc FROM accidents WHERE Num_Acc = %s", [num_acc])
        while cursor.fetchone() is not None:
            num_aleatoire = random.randint(1, 99999999)
            num_acc = str(an) + str(num_aleatoire)
            cursor.execute("SELECT Num_Acc FROM accidents WHERE Num_Acc = %s", [num_acc])

    # Ajouter une nouvelle ligne pour un nouvel accident
    nv_ligne = {"Num_Acc" : [num_acc], "date" : [date], "an" : [an], "mois" : [mois], "jour" : [jour], "hrmn" : [hrmn], "dep" : [dep], "com" : [com], "lat": [lat], "long" : [long], "agg" : [agg], "int" : [inter], "col" : [col], "lum" : [lum], "atm" : [atm], "catr" : [catr], "circ" : [circ], "nbv" : [nbv], "prof" : [prof], "plan" : [plan], "lartpc" : [lartpc], "larrout" : [larrout], "surf" : [surf], "infra" : [infra], "situ" : [situ], "grav" : [grav], "sexe" : [sexe], "age" : [age], "trajet" : [trajet], "secuexist" : [secuexist], "equipement" : [equipement], "obs" : [obs], "obsm" : [obsm], "choc" : [choc], "manv" : [manv], "vehiculeid" : [vehiculeid], "typevehicules" : [typevehicule], "manoeuvehicules" : [manoeuvehicules], "numVehicules" : [numVehicules]}

    # Convertir en DataFrame
    nv_acc = pd.DataFrame(nv_ligne)

    # Ajouter le marqueur sur la carte
    creerMarqueur(nv_acc.loc[0,])
    map.save("carte.html")
    browser_frame.browser.Reload()

    # Sauvegarder le nouvel accident en fonction de le mode choisi CSV ou BDD
    if mode_source.get() == "csv":
        # Vérifier si nfichier existe ou pas
        # s'il n'existe pas => il faut charger le fichier csv d'abord
        # => puis ajouter un nouvel accident dans ce fichier
        if nfichier is None:
            messagebox.showwarning("Attention", "Veuillez d'abord charger un fichier CSV avant d'ajouter un accident!")
            return
        else:
            # Ajouter dans le fichier CSV
            try:
                nv_acc.to_csv("data/" + nfichier, mode="a", sep=",", header=False, index=False)
                messagebox.showinfo("Succès", "Le nouvel accident ajouté au fichier CSV!")
            except Exception as e:
                messagebox.showerror("Ereur", "Erreur sur l'ajout dans CSV : " + str(e))
    else:
        # Ajouter dans la bdd
        try:
            # Vérifier et convertir chaque valeur de la ligne
            valeurs_de_ligne = []
            for val in nv_acc.loc[0]:
                if pd.isna(val):
                    valeurs_de_ligne.append(None)
                else:
                    if type(val) == str:
                        valeurs_de_ligne.append(val)
                    else:
                        valeurs_de_ligne.append(val.item())

            cursor.execute("""
                INSERT INTO accidents VALUES (
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,%s,%s,%s
                )
            """, valeurs_de_ligne)

            conn.commit()
            messagebox.showinfo("Succès", "Le nouvel accident ajouté dans la base de données!")
        except Exception as e:
            messagebox.showerror("Erreur", "Erreur sur l'ajout dans BDD : " + str(e))

    # Fermer le formulaire
    formulaire.destroy()


## L'interface de la source des données - le choix de CSV ou BDD
# Le bloc pour le choix de quelle source on veut charger des données
label_source = LabelFrame(maFenetre, text="SOURCE DES DONNEES", padx=5, pady=5, fg=CL_BLEU, font=TITRE)
label_source.place(x=5, y=5, width=530, height=120)

# Des boutons radio
btn_csv = Radiobutton(label_source, text="Fichier CSV", variable=mode_source, value="csv", command=afficher_config_bdd)
btn_csv.place(x=10, y=5)

btn_bdd = Radiobutton(label_source, text="Base de données", variable=mode_source, value="bdd", command=afficher_config_bdd)
btn_bdd.place(x=120, y=5)

# Un bouton pour l'ajout d'un accident en fonction de la mode choisie CSV ou BDD
b_ajout_acc = Button(label_source, text="Saisir un nouvel accident", command = ouvrir_formulaire)
b_ajout_acc.place(x=180,y=50)


## L'interface du chargement de données depuis le fichier CSV
# Le bloc pour le chargement des données depuis fichier CSV
label_csv = LabelFrame(maFenetre, text="FICHIER CSV", padx=5, pady=5, fg=CL_BLEU, font=TITRE)
label_csv.place(x=5, y=130, width=530, height=100)

# Nom du fichier CSV téléchargé
l_fichier = Label(label_csv, text="Fichier CSV : ")
l_fichier.place(x=10, y=5)

nom_f = Label(label_csv, text="Aucun fichier sélectionné", fg = CL_ROUGE)
nom_f.place(x=100, y=5)

b_fichier = Button(label_csv, text="Charger des données", command=ouvrir)
b_fichier.place(x=180, y=35)


## L'interface de la configuration de la connexion à bdd PostgreSQL
# Le bloc pour la connexion BDD
label_bdd = LabelFrame(maFenetre, text="CONNEXION BASE DE DONNEES", fg=CL_BLEU, font=TITRE, padx=5, pady=5)
label_bdd.place_forget() # cacher ce bloc au démarrage

Label(label_bdd, text="Adresse serveur :").place(x=5, y=5)
e_adresse = Entry(label_bdd, width=25)
e_adresse.place(x=150, y=5)

Label(label_bdd, text="Nom d'utilisateur :").place(x=5, y=35)
e_nom = Entry(label_bdd, width=25)
e_nom.place(x=150, y=35)

Label(label_bdd, text="Mot de passe :").place(x=5, y=65)
e_mdp = Entry(label_bdd, width=25, show="*")
e_mdp.place(x=150, y=65)

Label(label_bdd, text="Nom de BDD :").place(x=5, y=95)
e_nombdd = Entry(label_bdd, width=25)
e_nombdd.place(x=150, y=95)

b_connecter = Button(label_bdd, text="Se connecter", command=seconnecter)
b_connecter.place(x=5, y=128)

b_deconnecter = Button(label_bdd, text="Se déconnecter", command=sedeconnecter)
b_deconnecter.place(x=150, y=128)

Label(label_bdd, text="L'état de connexion : ").place(x=5, y=160)
l_etat_conn = Label(label_bdd, text="Pas de connexion", fg=CL_ROUGE)
l_etat_conn.place(x=150, y=160)

# Zone pour la création d'une table vierge dans Postrges
b_creer_table = Button(label_bdd, text="Créer une table", command=creer_table_bdd)
b_creer_table.place(x=5, y=200)

l_etat_table = Label(label_bdd, text="Aucune table créée", fg=CL_ROUGE)
l_etat_table.place(x=150, y=200)

# Zone pour déverser des données dans postgres
b_deverser = Button(label_bdd, text="Importer CSV", command=deverser_csv_bdd)
b_deverser.place(x=5, y=230)

l_etat_deverser = Label(label_bdd, text="")
l_etat_deverser.place(x=150, y=230)

# Zone pour charger des données depuis Postgres
b_bdd = Button(label_bdd, text="Charger depuis BDD", command=charger_depuis_bdd)
b_bdd.place(x=180, y=280)


## Carte Folium
map = folium.Map(location = [46.83, 1.85], zoom_start = 6)
marker_cluster = MarkerCluster().add_to(map)

# Légende en HTML pur injectée dans la carte
legende_html = """
<div style="
    position: fixed;
    bottom: 20px;
    left: 20px;
    background-color: white;
    padding: 10px;
    border: 2px solid #ccc;
    border-radius: 8px;
    font-size: 13px;
    line-height: 24px;
    z-index: 1000;">
    <b style="color:#125D98;">Gravité de l'accident</b><br>
    <img src="image/icon_aucun_blesse.png" width="20" height="20"> Indemne<br>
    <img src="image/icon_blesse_leger.png" width="20" height="20"> Blessé léger<br>
    <img src="image/icon_blesse_hospitalise.png" width="20" height="20"> Blessé hospitalisé<br>
    <img src="image/icon_blesse_grave.png" width="20" height="20"> Tué
</div>
"""

map.get_root().html.add_child(folium.Element(legende_html))
map.save("carte.html")


########################################
def cree_cadrecarte():
    cef.Initialize()

    #Create Frame
    global maFenetre
    frame = Frame(maFenetre, bg='black')
    frame.place(x=550, y=10, width=630, height=600)

    # Create Browser Frame
    global browser_frame
    browser_frame = BrowserFrame(frame)
    browser_frame.pack(fill=tk.BOTH, expand=tk.YES)

    maFenetre.mainloop()
    cef.Shutdown()


########################################
class BrowserFrame(tk.Frame):

    def __init__(self, mainframe, navigation_bar=None):
        self.navigation_bar = navigation_bar
        self.closing = False
        self.browser = None
        tk.Frame.__init__(self, mainframe)
        self.mainframe = mainframe
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        self.bind("<Configure>", self.on_configure)
        """For focus problems see Issue #255 and Issue #535. """
        self.focus_set()

    #URLURLURL
    def embed_browser(self):
        window_info = cef.WindowInfo()
        rect = [0, 0, self.winfo_width(), self.winfo_height()]
        window_info.SetAsChild(self.get_window_handle(), rect)
        self.browser = cef.CreateBrowserSync(window_info,
                                             url="file:///carte.html")
        assert self.browser
        self.message_loop_work()

    def get_window_handle(self):
        if self.winfo_id() > 0:
            return self.winfo_id()
        else:
            raise Exception("Couldn't obtain window handle")

    def message_loop_work(self):
        cef.MessageLoopWork()
        self.after(10, self.message_loop_work)

    def on_configure(self, _):
        if not self.browser:
            self.embed_browser()

    def on_root_configure(self):
        # Root <Configure> event will be called when top window is moved
        if self.browser:
            self.browser.NotifyMoveOrResizeStarted()

    def on_mainframe_configure(self, width, height):
        if self.browser:
            if WINDOWS:
                ctypes.windll.user32.SetWindowPos(
                    self.browser.GetWindowHandle(), 0,
                    0, 0, width, height, 0x0002)
            self.browser.NotifyMoveOrResizeStarted()

    def on_focus_in(self, _):
        #logger.debug("BrowserFrame.on_focus_in")
        if self.browser:
            self.browser.SetFocus(True)

    def on_focus_out(self, _):
        #logger.debug("BrowserFrame.on_focus_out")
        """For focus problems see Issue #255 and Issue #535. """
        pass

    def on_root_close(self):
        #logger.info("BrowserFrame.on_root_close")
        if self.browser:
            #logger.debug("CloseBrowser")
            self.browser.CloseBrowser(True)
            self.clear_browser_references()
        else:
            #logger.debug("tk.Frame.destroy")
            self.destroy()


    def clear_browser_references(self):
        # Clear browser references that you keep anywhere in your
        # code. All references must be cleared for CEF to shutdown cleanly.
        self.browser = None

## Finir le programme
maFenetre.config()
cree_cadrecarte()