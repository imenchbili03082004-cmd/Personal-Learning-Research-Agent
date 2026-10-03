<!-- image -->

## Institut Supérieur des Sciences Appliquées et de Technologie de Sousse

## Internet ET Protocoles

DNI-A1

Semestre 2

Enseignante: INSAF SAGAAMA

Année universitaire: 2025 - 2026

Ce document doit être complété par les notes de cours !

## Objectif du cours

L'objectif du ce cours est:

- Avoir une vue générale sur le réseau Internet. Savoir comment les ordinateurs communiquent entre eux
- Connaître les principaux protocoles de communication. Savoir comment est sécurisé un accès Internet.
- Connaître et manipuler les principaux Protocoles utilisés par INTERNET.

## Contenu:

1. Présentation de l'Internet (Qu'est ce qu'Internet, Comment accéder à Internet, Comment communiquer sur Internet ?, Adresse IP, Autres adresses...).
2. Protocole IP (Adressage IPv4, Formatage du paquet IP, Fragmentation/réassemblage, Résolution d'adresses, Routage IP)
3. Services DNS et Service DHCP
4. Quelques applications de l'Internet : messagerie électronique et transfert de fichier
5. Sécurité : Pare-feu (Firewall).

## Plan du module

- I. Chapitre 1: Introduction : Présentation de l'internet
- II. Chapitre 2: Protocoles et communications réseau
- III. Chapitre 3: Adressage dans les Réseaux IP
- IV. Chapitre 4: Fragmentation aux sein des réseaux TCP-IP
- V. Chapitre 5: Routage IP aux sein des réseaux TCP-IP
6. VI.Chapitre 6: Traduction d'adresse réseau pour IPv4: NAT
7. VII.Chapitre 7: Protocoles et Services de la Couche Application

## Chapitre 1: Présentation de l'internet

## Objectifs du chapitre 1

Les objectifs du chapitre 1 sont les suivants :

- Expliquer comment les réseaux affectent la façon dont nous interagissons, apprenons, travaillons et jouons
- Expliquer comment les périphériques hôtes peuvent être utilisées comme des clients, des serveurs ou les deux
- Expliquer l'utilisation des périphériques reseau
- Comparer les topologies et les périphériques d'un réseau local aux périphériques et aux topologies d'un réseau étendu
- Décrire la structure de base d'Internet
- Expliquer comment les réseaux locaux et étendus se connectent à Internet
- Expliquer le concept d'un réseau convergent

## Connecté au monde entier

## Les réseaux dans la vie quotidienne

- Evolution des technologies
- Nous vivons dans un monde à peine imaginable il y a 20 ans.
- Qu'est-ce que nous n'aurions pas sans Internet ?
- Qu'est-ce qui sera possible à l'avenir en utilisant le réseau comme plateforme ?
- La fin des frontières
- Communication instantannée sur internet
- Les réseaux facilitent l'apprentissage
- EAD (Enseignement à distance),…
- Les réseaux facilitent notre travail
- Nouvelles formes de communication: SMS, Réseaux sociaux, outils de collaboration, blogs, wikis, …
- Les réseaux facilitent les divertissements
- De la musique, des films, des livres, des jeux en ligne,...

<!-- image -->

## Fourniteurs de ressources dans un réseau

## Réseaux de tailles diverses

- Les petits réseaux domestiques : connectent plusieurs ordinateurs entre eux, ainsi qu'à Internet
- Petits bureaux/bureaux à domicile : permet à l'ordinateur au sein d'un bureau à domicile ou d'un bureau distant de se connecter à un réseau d'entreprise
- Moyens et grands réseaux :

<!-- image -->

Plusieurs emplacements où des centaines, voire des milliers d'ordinateurs sont reliés

- Réseaux mondiaux : relie des centaines de millions d'ordinateurs dans le monde, par exemple Internet

## Fourniteurs de ressources dans un réseau

## Clients et serveurs

- Chaque ordinateur connecté à un réseau est appelé hôte ou périphérique final.
- Les serveurs sont des ordinateurs qui fournissent des informations aux périphériques finaux sur le réseau.
- Par exemple, les serveurs de messagerie, les serveurs web ou les serveurs de fichiers
- Les clients sont des ordinateurs qui envoient des requêtes aux serveurs pour

<!-- image -->

récupérer des informations comme une page web à partir d'un serveur web ou un e-mail à partir d'un serveur de messagerie.

## Fourniteurs de ressources dans un réseau

## Peer-to-Peer (P2P)

- Le logiciel client et le logiciel serveur sont généralement exécutés sur des ordinateurs distincts.
- Toutefois, dans les petites entreprises ou chez les particuliers, il est typique pour un client de faire également office de serveur. Ces réseaux sont appelés des réseaux peer to peer.
- Les avantages des réseaux peer to peer : faciles à configurer, plus simples, moins onéreux.
- Les inconvénients : aucune administration centralisée, pas aussi sécurisés, pas évolutifs, des performances ralenties.

<!-- image -->

## Composants du réseau

- Un réseau peut être aussi simple que la connexion entre deux ordinateurs via un seul câble ou aussi complexe qu'une collection de réseaux Parcourant le globe terrestre.
- L'infrastructure de réseau comprend trois grandes catégories de composants réseau:
- Appareils
- Supports
- Services

<!-- image -->

## Composants du réseau

## Terminaux

- Un périphérique final correspond à l'équipement d'où provient un message ou d'où il est reçu.
- Les données proviennent d'un périphérique final, traversent le réseau et arrivent sur un périphérique final

<!-- image -->

## Composants du réseau

## Périphériques réseau intermédiaires

- Un périphérique intermédiaire connecte entre eux les périphériques finaux dans un réseau. Voici quelques exemples : les commutateurs, points d'accès sans fil, routeurs et pare-feu.
- La gestion des données lors de leur passage à travers un réseau constitue également le rôle du périphérique intermédiaire, notamment:
- Régénérer et retransmettre des signaux de données.
- Gérer des informations indiquant les chemins qui existent à travers le réseau et l'interréseau.
- Indiquer aux autres périphériques les erreurs et les échecs de communication.

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

Routeur

<!-- image -->

Périphériques intermédiaires Pare-feu

<!-- image -->

## Composants du réseau

## Supports de transmission

- La communication à travers un réseau s'effectue

sur un support (média) qui

permet à un message de se déplacer

depuis la Source vers la destination.

- Les réseaux utilisent généralement trois types de supports:
- Fils métalliques dans des câbles, comme le cuivre
- Verre, tels que les câbles à fibre optique
- Transmission sans fil

<!-- image -->

## Les réseaux locaux et les réseaux étendus Types de réseau

- Les deux types de réseaux les plus courants :
- Réseau local (LAN : Local Area Network) s'étend sur une petite zone géographique détenue Ou gérée par un individu ou un service IT.
- Réseau étendu (WAN:

Wide Area Network) s'étend sur une large zone géographique, généralement impliquant un prestataire (fournisseur) de services.

- Autres types de réseau:
- réseau métropolitain (MAN: metropolitain Area Network)
- réseau local sans fil (WLAN : Wireles LAN).

<!-- image -->

## Les réseaux locaux et les réseaux étendus

<!-- image -->

- Trois caractéristiques des réseaux locaux :
- S'étend sur une petite zone géographique telle qu'une maison, une école, un immeuble de bureaux ou un campus.
- Généralement géré par une seule entreprise ou une seule personne.
- Fournit une bande passante très élevée aux périphériques finaux et aux périphériques intermédiaires au sein du réseau.
- Trois caractéristiques des réseaux étendus :
- Les WAN relient des LAN sur des zones étendues couvrant des villes, des états ou des pays.
- Habituellement gérés par plusieurs fournisseurs de services.
- Les réseaux WAN fournissent généralement des liaisons à plus bas débit entre les réseaux locaux.

<!-- image -->

## Internet

- Internet est un ensemble de réseaux locaux et étendus

interconnectés à l'échelle

internationale.

- Les réseaux locaux sont connectés entre eux par le biais des réseaux étendus.
- Les réseaux étendus Sont ensuite connectés les uns aux autres à l'aide de fils de cuivre, de câbles de fibre optique ou de Transmissions sans fil.
- Internet n'appartient
- pas à une personne ou à un groupe en particulier

<!-- image -->

## Internet, intranets et extranets

- Contrairement à Internet, un intranet est une connexion privée de réseaux LAN et WAN interne à une entreprise qui est conçue pour être accessible uniquement

pour les membres de l'entreprise ou des personnes tierces autorisées.

- Une entreprise peut utiliser Un extranet pour fournir un accès sécurisé à son réseau pour les personnes qui travaillent pour une autre entreprise qui ont besoin d'accéder aux données du réseau.

<!-- image -->

## Connexions Internet

## Technologie d'accès à Internet

<!-- image -->

- Il existe plusieurs manières de connecter des utilisateurs et des entreprises à Internet :
- Les services les plus populaires pour les particuliers et les petits bureaux comprennent le câble haut débit, la technologie DSL (Digital Subscriber Line) haut débit, les WAN sans fil et les services mobiles.
- Les entreprises ont besoin de connexions plus rapides pour prendre en charge les téléphones IP, la vidéoconférence et le stockage dans des data centers.
- 18 · Les connexions professionnelles sont généralement fournies par des prestataires de services et peuvent comprendre la DSL, les lignes louées et les solutions Metro Ethernet.

## Connexions Internet

## Connexions Internet des bureaux à domicile et des petits bureaux

<!-- image -->

- Câble : bande passante élevée, toujours disponible, connexion Internet proposée par les fournisseurs de services de télévision par câble.
- DSL : bande passante élevée, toujours disponible, connexion Internet qui utilise une ligne téléphonique.
- Cellulaire : utilise un réseau de téléphonie mobile pour se connecter à Internet ; uniquement disponible dans les endroits où il est possible de capter un signal cellulaire.
- Satellite : un avantage majeur pour les zones rurales dépourvues de fournisseurs d'accès à Internet.
- Ligne commutée : une option peu coûteuse et à faible bande passante utilisant un modem.

## Connexions Internet

## Connexions Internet d'entreprise

- Les connexions commerciales

d'entreprises peuvent nécessiter une bande passante plus élevée, des connexions dédiées ou des services gérés. Options de connexion typiques pour les entreprises :

- Lignes louées : des circuits dédiés appartenant au réseau du fournisseur d'accès qui relient des bureaux distants avec la transmission de données et/ou de communications vocales privées.
- WAN Ethernet : étend la technologie d'accès des réseaux LAN au réseau étendu.
- DSL : la DSL d'entreprise est disponible dans divers formats, y compris la SDSL (ligne d'abonné numérique à débit symétrique).
- 20 · Satellite : peut fournir une connexion lorsqu'aucune solution par câble n'est disponible.

<!-- image -->

## Réseaux distincts classiques

<!-- image -->

- Il y a 30 ans, une école était un bon exemple de réseaux multiples. Certaines classes étaient reliées au réseau de données. Ces mêmes salles de classe étaient câblées au réseau téléphonique et au réseau de télévision.
- Chacun de ces réseaux utilisait des technologies différentes pour acheminer les signaux de communication en utilisant un ensemble différent de règles et de normes.

## Réseau convergent

<!-- image -->

- Les réseaux de données convergents transportent plusieurs services sur une même liaison, y compris les données, la voix et la vidéo.
- Contrairement aux réseaux spécialisés, les réseaux convergés transmettent des données, de la voix et des flux vidéo entre différents types d'appareil, par le biais d'une même infrastructure réseau.
- L'infrastructure réseau utilise le même ensemble de règles et de normes.

## Réseau fiable

## Architecture réseau

<!-- image -->

- Architecture réseau désigne les technologies qui prennent en charge l'infrastructure qui fait transiter les données sur le réseau.
- Il existe quatre caractéristiques de base que les architectures sousjacentes doivent prendre en considération si elles veulent répondre aux attentes des utilisateurs :
- Tolérance aux pannes
- Évolutivité
- Qualité de service (QoS)
- Sécurité