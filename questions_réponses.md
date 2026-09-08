Partie 2 : 

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
