# Projet-9-site-web-django
Site internet de LITReview

***

### Installation et lancement
Se placer dans un dossier de travail vide et récupérer le code:
```
$ git clone https://github.com/martinschongauer/Projet-9-site-web-django
```

Créer et activer un environnement Python pour ce projet (testé sous Linux - Ubuntu):
```
$ python3 -m venv env
$ source env/bin/activate
```

Parfois les commandes varient légèrement. Sous Windows 10 nous avons exécuté les commandes suivantes:
```
$ python -m venv env
$ env\Scripts\activate
```

Installer ensuite les dépendances listées dans le fichier requirements.txt:
```
$ pip install -r requirements.txt
```

Lancer le programme:
```
$ python3 manage.py runserver
```

(ou "python" selon la configuration de la machine)


### Usage général
Le site internet est ensuite accessible en local à l'adresse:

http://127.0.0.1:8000/index

Ainsi que sa zone d'administration:

http://127.0.0.1:8000/admin

Une base de données minimale est livrée avec l'application. Elle comprend quatre utilisateurs:

admin - baptiste - openclassroom - utilisateur

admin est le "superuser", et tous partagent le mot de passe : p@zZw0rd

Le reste de l'interface à partir de la page d'accueil suit la structure des wireframes, et des relations de suivi entre utilisateurs, ainsi qu'un série de reviews et de tickets ont été créés pour démontrer le bon fonctionnement du site.
