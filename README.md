<p align="center">
  <img width="35%" src="amibot.png" alt="Banner">
</p>
<p align="center">
  <b font-size="larger">AMIBOT</b>
</p>
<p align="center">
  <b>Robot Discord pour le serveur de l'AMI.</b>
</p>

## À propos
Un robot discord à multiple usage pour le serveur discord de l'association
des étuidants en mathématiques et informatique de l'université du Québec à 
Trois-Rivières.

Fonctionnalités:
1. Afficher les détails d'un cours à partir de son sigle.
2. Afficher l'horaire d'un cours à partir de son sigle.
3. Générer un horaire à partir d'une liste de cours(sigle).

## Comment le rouler
### Prérequis
- Avoir une version de python 3.8 d'installer sur votre système;
- avoir [pipenv](https://pipenv.pypa.io/en/latest/) d'installer sur votre sytème;
- obtenir un jeton discord pour tester le bot ([tutoriel pour ajouter un bot discord](https://medium.com/simple-guides-to-technology/a-simple-guide-to-making-a-discord-bot-using-python-1e4738f2cdd0));
- créer un fichier `.env` à la racine du projet ayant comme contenu:
```
DISCORD_TOKEN=ton_jeton_discord_ici
```

### Démarrer le bot
Pour le premier démarrage assurez-vous d'avoir exécuter cette commande avant:
``` sh
pipenv install
```
Quand les dépendances du projet on finis d'être installer vous pouvez démarrer le bot avec la commande suivante:
``` sh
pipenv run main
```
