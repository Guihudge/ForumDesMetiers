# Forum des metier

Application de répartition pour le forum des métiers

## Fonctionnalités manquantes

### V1 milestone
- Done !

### V2 milestone
- Algo de répartition

## Fonctionnalités présentes
- Création d'élève
- création des métiers
- importation d'élève depuis Pronote
- Résumé globale
- Édition du résumé par classe
- Statistique de base
- blocage du choix des veux

## Installation

### En mode développement

Créer un env python
```
$ python3 -m venv .venv
$ source .venv/bin/activate
```

Installation des dépendances
```
$ pip install -r requirment.txt
```

### En production dans un environement virtuelle

Création de l'environnement
```
$ python3 -m venv .venv
$ source .venv/bin/activate
```

Installation des dépendances et du serveur de production
```
$ pip install -r requirment.txt
$ pip install waitress
```

Génération du secret :
```
$ python -c 'import secrets; print("export SECRET_KEY="+secrets.token_hex())' > .env
$ source .env
```

Lancement de l'application :
```
$ waitress-serve app:app
```

### Via docker

Construction de l'image docker :
```
$ docker build --tag forum-metier .
```

Génération du secret :
```
$ python -c 'import secrets; print("SECRET_KEY="+secrets.token_hex())'
```

Lancement de l'image :
```
$ docker run -p "out_port":8080 -e "secret-precedant" forum-metier
```
Pensez à changer le port et le secret.

### Commun pour toutes les méthodes
Lors du premier démarrage de l'application les identifiants administrateur sont affichés dans la sortie standard. Ensuite accéder à l'application et se connecter avec les identifiants précédents.