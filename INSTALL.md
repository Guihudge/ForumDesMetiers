# Installation

## En mode développement

Créer un env python
```sh
$ python3 -m venv .venv
$ source .venv/bin/activate
```

Installation des dépendances
```sh
$ pip install -r requirment.txt
```

## En production dans un environnement virtuelle

Création de l'environnement
```sh
$ python3 -m venv .venv
$ source .venv/bin/activate
```

Installation des dépendances et du serveur de production
```sh
$ pip install -r requirment.txt
$ pip install waitress
```

Génération du secret :
```sh
$ python -c 'import secrets; print("export SECRET_KEY="+secrets.token_hex())' > .env
$ source .env
```

Lancement de l'application :
```sh
$ waitress-serve app:app
```

## Via docker

Construction de l'image docker :
```sh
$ docker build --tag forum-metier .
```

Génération du secret :
```sh
$ python -c 'import secrets; print("SECRET_KEY="+secrets.token_hex())'
```

Lancement de l'image :
```sh
$ touch ./app.db # adapter le chemain en fonction de l'emplaement du fichier de base de données
$ docker run -p "out_port":8080 -t -e "secret-precedant" -v ./app.db:/ForumMetier/app/app.db forum-metier
```
Pensez à changer le port et le secret.

## Commun pour toutes les méthodes
Lors du premier démarrage de l'application les identifiants administrateur sont affichés dans la sortie standard. Ensuite accéder à l'application et se connecter avec les identifiants précédents.