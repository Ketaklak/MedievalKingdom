# 🏰 Empires Médiévaux - JRPG Multijoueur

Une application de jeu de rôle médiéval inspirée d'OGame, axée sur la gestion des ressources en temps réel et la construction de royaume.

## 📋 Table des Matières

- [Aperçu](#aperçu)
- [Fonctionnalités](#fonctionnalités)
- [Technologies](#technologies)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Structure du Projet](#structure-du-projet)
- [API](#api)
- [Contribution](#contribution)

## 🎯 Aperçu

Empires Médiévaux est un jeu de stratégie multijoueur en temps réel où les joueurs construisent et gèrent leur royaume médiéval. Inspiré des mécaniques d'OGame, le jeu met l'accent sur la gestion des ressources, la construction de bâtiments, la diplomatie et la conquête.

### Gameplay Principal
- 🏗️ **Construction** : Construisez et améliorez 6 bâtiments médiévaux
- ⚔️ **Militaire** : Recrutez et entraînez vos armées
- 🤝 **Diplomatie** : Formez des alliances et négociez des échanges
- 📊 **Classements** : Montez dans les classements mondiaux
- 💬 **Chat** : Communiquez avec les autres joueurs

## ✨ Fonctionnalités

### 🎮 Système de Jeu
- **Gestion des Ressources** : Or, Bois, Pierre, Nourriture
- **Construction de Bâtiments** : 
  - 🏰 Château (Défense et prestige)
  - 🌾 Ferme (Production de nourriture)
  - 🪓 Scierie (Production de bois)
  - ⛏️ Mine (Production de pierre et or)
  - 🛡️ Caserne (Entraînement militaire)
  - ⚒️ Forge (Équipement militaire)
- **File de Construction** : Gérez vos projets de construction
- **Système Militaire** : Raids, entraînement, combat

### 👥 Multijoueur
- **Comptes Utilisateur** : Inscription et authentification
- **Sélection d'Empire** : 5 empires avec bonus uniques
  - 🛡️ Empire Norman
  - ⚔️ Royaume Viking
  - 🏹 Royaume Saxon
  - 🍀 Clans Celtiques
  - 👑 Empire Franc
- **Chat Global** : Communication en temps réel
- **Système d'Alliances** : Création, invitations, leadership
- **Commerce** : Échanges de ressources entre joueurs

### 🗺️ Fonctionnalités Avancées
- **Carte des Alliances** : Visualisation des territoires
- **Blasons Personnalisés** : Pour les alliances de 10+ membres
- **Boutique** : Objets spéciaux (Parchemin de Changement de Race)
- **Classements Globaux** : Compétition mondiale
- **Panneau Admin** : Gestion complète du serveur

## 🛠️ Technologies

### Backend
- **FastAPI** - Framework Python moderne et rapide
- **MongoDB** - Base de données NoSQL
- **Motor** - Driver MongoDB asynchrone
- **Pydantic** - Validation des données
- **JWT** - Authentification sécurisée
- **Passlib** - Hachage des mots de passe

### Frontend
- **React** - Library JavaScript pour l'interface utilisateur
- **Vite** - Outil de build moderne
- **Tailwind CSS** - Framework CSS utilitaire
- **Shadcn/ui** - Composants UI réutilisables
- **Lucide React** - Icônes modernes
- **Axios** - Client HTTP

## 🚀 Installation

### Prérequis
- Node.js (v18+)
- Python (v3.9+)
- MongoDB
- Yarn ou npm

### 1. Cloner le Projet
```bash
git clone <repository-url>
cd medieval-empires
```

### 2. Installation Backend
```bash
cd backend
pip install -r requirements.txt
```

### 3. Installation Frontend
```bash
cd frontend
yarn install
# ou
npm install
```

## ⚙️ Configuration

### Backend (.env)
```env
MONGO_URL=mongodb://localhost:27017/medieval_empires
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
```

### Frontend (.env)
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

## 🎯 Utilisation

### Démarrer le Backend
```bash
cd backend
python server.py
```
Le serveur démarre sur `http://localhost:8001`

### Démarrer le Frontend
```bash
cd frontend
yarn start
# ou
npm start
```
L'application est accessible sur `http://localhost:3000`

### Première Connexion
1. Accédez à `http://localhost:3000`
2. Cliquez sur "Créer un royaume"
3. Remplissez vos informations
4. Choisissez votre empire
5. Commencez à construire votre royaume !

## 📁 Structure du Projet

```
/app
├── backend/
│   ├── auth/                 # Système d'authentification
│   ├── database/            # Connexion MongoDB
│   ├── models/              # Modèles Pydantic
│   ├── routes/              # Endpoints API
│   ├── tasks/               # Tâches de fond
│   ├── server.py            # Point d'entrée
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/      # Composants React
│   │   ├── contexts/        # Contextes React
│   │   ├── hooks/           # Hooks personnalisés
│   │   ├── services/        # Services API
│   │   └── utils/           # Utilitaires
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

### Composants Principaux

#### Frontend
- **AuthScreen.jsx** - Écran d'authentification
- **MultiplayerDashboard.jsx** - Interface principale du jeu
- **AdminPanel.jsx** - Panneau d'administration
- **ChatSystem.jsx** - Système de chat
- **AllianceMap.jsx** - Carte des alliances
- **ShopModal.jsx** - Boutique du jeu

#### Backend
- **auth/** - Gestion JWT et authentification
- **routes/game.py** - Logique de jeu principale
- **routes/diplomacy.py** - Alliances et commerce
- **routes/admin.py** - Fonctions administratives
- **tasks/background_tasks.py** - Tâches automatiques

## 🔌 API

### Endpoints Principaux

#### Authentification
- `POST /api/auth/register` - Inscription
- `POST /api/auth/login` - Connexion
- `GET /api/auth/me` - Profil utilisateur

#### Jeu
- `GET /api/game/status` - Statut du joueur
- `POST /api/game/upgrade-building` - Améliorer bâtiment
- `POST /api/game/recruit-army` - Recruter armée
- `POST /api/game/raid` - Lancer raid

#### Diplomatie
- `POST /api/diplomacy/create-alliance` - Créer alliance
- `POST /api/diplomacy/trade-offer` - Offre d'échange
- `GET /api/diplomacy/alliance-map` - Carte des alliances

#### Chat
- `GET /api/chat/messages` - Messages récents
- `POST /api/chat/send` - Envoyer message

#### Administration
- `GET /api/admin/stats` - Statistiques serveur
- `POST /api/admin/broadcast` - Message diffusion
- `PUT /api/admin/player/{username}` - Modifier joueur

## 🎨 Personnalisation

### Thèmes d'Empire
Chaque empire possède des bonus uniques :
- **Norman** : +10% défense des bâtiments
- **Viking** : +15% efficacité des raids
- **Saxon** : +10% production de nourriture
- **Celtic** : +10% production de bois
- **Frankish** : +10% production d'or

### Système de Blasons
Les alliances de 10+ membres peuvent créer des blasons personnalisés :
- **Couleurs** : Rouge, Bleu, Vert, Violet, Or, Argent
- **Motifs** : Rayures, Croix, Diagonal, Uni
- **Symboles** : Couronne, Épée, Bouclier, Flamme, Aigle, Lion

## 🔧 Développement

### Lancer en Mode Développement
```bash
# Terminal 1 - Backend
cd backend
python server.py

# Terminal 2 - Frontend
cd frontend
yarn dev
```

### Tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
yarn test
```

### Build de Production
```bash
# Frontend
cd frontend
yarn build

# Le dossier build/ contient les fichiers statiques
```

## 🐛 Dépannage

### Problèmes Courants

**Frontend ne compile pas :**
- Vérifiez que toutes les dépendances sont installées
- Assurez-vous que les variables d'environnement sont correctes

**Backend ne démarre pas :**
- Vérifiez la connexion MongoDB
- Vérifiez que Python 3.9+ est installé
- Vérifiez le fichier `.env`

**Erreurs d'authentification :**
- Vérifiez que JWT_SECRET_KEY est défini
- Clearez le localStorage du navigateur

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Forkez le projet
2. Créez votre branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Pushez sur la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

### Guidelines de Développement
- Suivez les conventions de nommage existantes
- Ajoutez des tests pour les nouvelles fonctionnalités
- Documentez les changements importants
- Respectez le style de code (ESLint/Prettier)

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- Inspiré par les mécaniques de jeu d'OGame
- Interface utilisateur basée sur Shadcn/ui
- Icônes fournies par Lucide React

---

**Développé avec ❤️ pour la communauté des jeux de stratégie médiévaux**

Pour plus d'informations, consultez la documentation ou contactez l'équipe de développement.
