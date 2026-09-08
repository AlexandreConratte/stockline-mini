**TP 1 , Partie 2 :** 

*commande pour construire l'image :*

docker build -f Dockerfile.naif -t stockline-mini:naif .

*cmd pour lancer le contenur sur port 8000 :*

docker run -d --name stockline-naif -p 8000:8000 stockline-mini:naif

*verif de l'image /conteneur :* docker images & docker ps


**Quelle est la taille approximative de l’image stockline-mini:naif ? Est-elle proche de 1,2 Go ?**   

La taille est 439MB, donc non tout de même en dessous des 1,2Go

**Avec quel utilisateur le processus du conteneur est-il exécuté ?**  

Avec l'utilisateur root

**Quels sont les deux principaux problèmes que vous pouvez identifier avec cette première image Docker ?**

Les deux principaux problèmes sont la taille de l'image, trop volumineuse pour l'application qu'elle représente , et l'utilisateur root qui n'est pas optimisé niveau sécurité 

*cmd pour nettoyer le contenur* : 
docker stop stockline-naif & docker rm stockline-naif


*docker history stockline-mini:1.0  :* 

La couche la plus lourde visible dans docker history stockline-mini:1.0 est la couche de base Debian, avec environ 87,5 MB


**TP 2 , Brancher la vraie base :**

**Partie 1 — L’API passe à PostgreSQL**  

1. Pourquoi le mot de passe est-il le seul paramètre sans valeur par défaut (os.environ['DB_MOT_DE_PASSE'] et pas .get(...)) ?

car un mdp est une données sensibles, qui ne doit pas apparaitre dans le code pur/sur github, à fournir soit via les variables d'environnement ou hachés/cryptés dans certaines bdd . Ici = via variables d'environnement

2. À quoi sert la boucle de la fonction cycle_de_vie ? Que se passerait-il sans elle au démarrage d’une stack Docker Compose ?

La boucle de la fonction sert à attendre la connexion via postgresql jusqu'à 10 fois. Si la connexion se fait : alors cela va créer la table de produit si elle n'existe pas, puis d'en indiquer le nombre, et si la table est vide (=0) , d'y insérer les tuples des PRODUITS_INITIAUX. Annuler toute l'opération si la bdd reste injoignable apràs 10 tentatives.     

Sans elle, le docker compose pourrait ne pas réussir à se connecter à postegresql à son démarrage et donc l'app ne fonctionnerait pas

3. Pourquoi écrit-on : WHERE id = %s

Apparemment dans SQL on utilise des requêtes paramètrées (donc transmettre les données utilisateurs en paramètres) afin de prévenir les injections SQL, qui consistent à  tromper une base de données pour qu'elle révèle des choses qu'elle ne devrait pas révéler.

**Partie 3 — La stack Docker Compose** 

Questions de comprehension : 

1. Dans la configuration du service api, pourquoi la variable : DB_HOTE: db
utilise-t-elle le nom db au lieu d’une adresse IP ou de localhost ?

- Cela indique au service api que la bdd est accessible à db, car dans docker compose les services se joignent via leurs noms

2. À quoi sert la configuration suivante :
depends_on:
  db:
    condition: service_healthy
et quel est le rôle du healthcheck configuré sur PostgreSQL ? 

- Même principe je suppose que la boucle de cycle-de-vie : attendre que postgresql réponde et accepte les connexions au démarrage du contenur, vu qu'il peut y avoir une latence entre les deux ?


3. Dans les deux services, le mot de passe est récupéré de cette manière :
${DB_MOT_DE_PASSE}
D’où Docker Compose récupère-t-il cette valeur et pourquoi est-il préférable de procéder ainsi plutôt que d’écrire directement le mot de passe dans compose.yaml ?

- Docker Compose récupère ${DB_MOT_DE_PASSE} par la valeur définie dans l’environnement du terminal (ex: tout à l'heure, la cmd DB_MOT_DE_PASSE=********** python3 -m pytest -v ) ou dans un fichier .env du projet



Explication fin de TP 2 : 

docker compose down stop+suppr les conteneurs et les réseaux, mais conserve le volume nommé PostgreSQL. Après docker compose up -d, la base retrouve ses données; le produit ajouté est encore là

docker compose down -v supprime les volumes du projet en plus d'arrêter et suppr les conteneurs, dont le volume donnees-db,  donc efface les données PostgreSQL.
Lorsqu'on relance l'api, la nouvelle base est recomposé des trois produits initiaux, mais pas des produits ajoutés
