# Forum des metier

Application de répartition pour le forum des métiers

## Fonctionnalités manquantes
- Algo de répartition
- Édition du résumé par classe
- blocage du choix des veux

## Fonctionnalités présentes
- Création d'élève
- création des métiers
- importation d'élève depuis Pronote
- Résumé globale
- Statistique de base

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

# Via docker

Construction de l'image docker :
```
$ docker build --tag forum-metier .
```

Génération du secret :
```
$ python -c 'import secrets; print("export SECRET_KEY="+secrets.token_hex())'
```

Lancement de l'image :
```
$ docker run -p "out_port":8080 -e "secret-precedant" forum-metier
```
Pensez à changer le port et le secret.