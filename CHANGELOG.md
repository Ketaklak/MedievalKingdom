# 📜 Changelog - Empires Médiévaux

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/), et ce projet adhère au [Versioning Sémantique](https://semver.org/lang/fr/).

---

## [0.5.1a] - 2025-01-01

### 🔧 Corrections
- **Interface Utilisateur**
  - Correction de l'erreur React "Objects are not valid as a React child" dans AdminPanel
  - Résolution du problème d'affichage "NaN:NaN:NaN" pour les temps de construction
  - Correction des icônes manquantes (`Refresh` → `RefreshCw`, `Dragon` → `Flame`)

- **Système Admin**
  - Correction de la visibilité du bouton Admin Panel pour les utilisateurs admin
  - Réparation de l'endpoint `/api/admin/system-info` avec de vraies valeurs système
  - Amélioration de la gestion des permissions administrateur

- **Stabilité**
  - Sécurisation de la fonction `formatTime()` contre les valeurs undefined/null
  - Amélioration de la sérialisation des objets MongoDB (ObjectId, datetime)
  - Correction des erreurs de compilation frontend

### 🏗️ Améliorations
- **Diplomatie**
  - Ajout de l'affichage des alliances existantes avec détails complets
  - Affichage des offres de trade avec boutons d'acceptation
  - Section "Mon Alliance" et "Mes Offres de Trade"
  - Badges pour les alliances élites (10+ membres)

---

## [0.5.0a] - 2024-12-28

### ✨ Nouvelles Fonctionnalités
- **Système de Boutique**
  - Implémentation complète de la boutique en jeu
  - Ajout des "Parchemins de Changement de Race"
  - Protection du changement de race via objets boutique uniquement
  - Interface utilisateur dédiée avec `ShopModal.jsx`

- **Carte des Alliances**
  - Nouveau composant `AllianceMap.jsx`
  - Visualisation des territoires d'alliance
  - Blasons personnalisés pour les alliances de 10+ membres
  - Système de couleurs et motifs (Rayures, Croix, Diagonal, Uni)
  - Symboles disponibles : Couronne, Épée, Bouclier, Flamme, Aigle, Lion

### 🔧 Corrections
- **Backend**
  - Correction des problèmes de sérialisation ObjectId dans tous les endpoints
  - Résolution des erreurs `datetime.utcnow()` vs `datetime.utcnow`
  - Amélioration de la gestion d'erreurs dans les routes diplomatie

---

## [0.4.2a] - 2024-12-25

### 🏗️ Améliorations
- **Panel Admin Avancé**
  - Console de débogage intégrée avec capture des logs
  - Affichage temps réel des nouveaux joueurs et messages
  - Fonctionnalité de diffusion de messages globaux
  - Capacité de réinitialiser les ressources des joueurs
  - Système pour promouvoir des joueurs au statut admin

### 🔧 Corrections
- **Système de Chat**
  - Résolution des erreurs de sérialisation ObjectId
  - Amélioration de la stabilité des messages en temps réel

---

## [0.4.1a] - 2024-12-22

### ✨ Nouvelles Fonctionnalités
- **Système de Diplomatie Complet**
  - Création et gestion d'alliances
  - Système d'invitations et de leadership d'alliance
  - Offres de commerce entre joueurs
  - Négociation et acceptation d'échanges de ressources
  - Endpoints API dédiés (`/api/diplomacy/*`)

### 🔧 Corrections
- **Données Joueur**
  - Correction de l'erreur "Objects are not valid as a React child" dans ProfileModal
  - Amélioration de l'affichage des statistiques d'armée
  - Résolution des problèmes de rendu des objets React

---

## [0.4.0a] - 2024-12-20

### ✨ Nouvelles Fonctionnalités
- **Système Militaire Avancé**
  - Réécriture complète du système de raids
  - Entraînement d'armée avec différents types d'unités
  - Combat tactique avec calculs de puissance
  - Système de butin et récompenses

- **Panel d'Administration**
  - Interface administrateur complète
  - Gestion des joueurs et modération
  - Statistiques serveur en temps réel
  - Outils de débogage et monitoring

### 🏗️ Améliorations
- **Performance**
  - Optimisation des requêtes MongoDB
  - Amélioration du cache des données joueur
  - Réduction de la latence des API

---

## [0.3.2a] - 2024-12-18

### 🔧 Corrections
- **File de Construction**
  - Résolution des bugs de la queue de construction
  - Amélioration de la synchronisation backend/frontend
  - Correction des calculs de temps d'achèvement

### 🏗️ Améliorations
- **Interface Utilisateur**
  - Amélioration de l'affichage des bâtiments en construction
  - Indicateurs visuels de progression améliorés
  - Messages d'erreur plus informatifs

---

## [0.3.1a] - 2024-12-15

### ✨ Nouvelles Fonctionnalités
- **Système de Chat Global**
  - Chat en temps réel entre joueurs
  - Historique des messages persistant
  - Modération basique des messages
  - Interface utilisateur intuitive

### 🔧 Corrections
- **Authentification**
  - Amélioration de la sécurité JWT
  - Correction des problèmes de session
  - Validation renforcée des tokens

---

## [0.3.0a] - 2024-12-12

### ✨ Nouvelles Fonctionnalités
- **Système de Construction Avancé**
  - File de construction avec gestion des priorités
  - 6 bâtiments médiévaux distincts :
    - 🏰 Château (Défense et prestige)
    - 🌾 Ferme (Production de nourriture)
    - 🪓 Scierie (Production de bois)
    - ⛏️ Mine (Production de pierre et or)
    - 🛡️ Caserne (Entraînement militaire)
    - ⚒️ Forge (Équipement militaire)
  - Calculs de temps de construction réalistes
  - Système de prérequis entre bâtiments

### 🏗️ Améliorations
- **Gestion des Ressources**
  - Production automatique en arrière-plan
  - Bonus d'empire appliqués aux ressources
  - Système de stockage et limites

---

## [0.2.2a] - 2024-12-10

### 🔧 Corrections
- **Backend**
  - Résolution des problèmes de connexion MongoDB
  - Amélioration de la gestion d'erreurs API
  - Correction des fuites mémoire dans les tâches background

### 🏗️ Améliorations
- **Sécurité**
  - Hachage des mots de passe avec bcrypt
  - Validation renforcée des données d'entrée
  - Protection contre les attaques par force brute

---

## [0.2.1a] - 2024-12-08

### ✨ Nouvelles Fonctionnalités
- **Système d'Empires**
  - 5 empires disponibles avec bonus uniques :
    - 🛡️ Empire Norman (+10% défense des bâtiments)
    - ⚔️ Royaume Viking (+15% efficacité des raids)
    - 🏹 Royaume Saxon (+10% production de nourriture)
    - 🍀 Clans Celtiques (+10% production de bois)
    - 👑 Empire Franc (+10% production d'or)

### 🏗️ Améliorations
- **Interface Utilisateur**
  - Écran de sélection d'empire amélioré
  - Affichage des bonus d'empire dans l'interface
  - Thèmes visuels spécifiques à chaque empire

---

## [0.2.0a] - 2024-12-05

### ✨ Nouvelles Fonctionnalités
- **Système Multijoueur Complet**
  - Inscription et authentification des utilisateurs
  - Création de royaume personnalisé
  - Système de classements globaux
  - Découverte d'autres joueurs

- **Architecture Full-Stack**
  - Backend FastAPI avec endpoints RESTful
  - Base de données MongoDB pour la persistance
  - Authentication JWT sécurisée
  - Tâches en arrière-plan pour la progression du jeu

### 🏗️ Améliorations
- **Performance**
  - Migration des données mockées vers une vraie base de données
  - Optimisation des requêtes et indexation
  - Gestion asynchrone des opérations

---

## [0.1.2a] - 2024-12-03

### 🔧 Corrections
- **Interface Utilisateur**
  - Correction des problèmes de responsive design
  - Amélioration de l'accessibilité
  - Résolution des bugs d'affichage sur mobile

### 🏗️ Améliorations
- **Expérience Utilisateur**
  - Animations et transitions améliorées
  - Feedback visuel des actions utilisateur
  - Messages d'erreur plus clairs

---

## [0.1.1a] - 2024-12-01

### ✨ Nouvelles Fonctionnalités
- **Système de Ressources de Base**
  - Gestion de 4 ressources principales : Or, Bois, Pierre, Nourriture
  - Production automatique basée sur les bâtiments
  - Interface de gestion des ressources

### 🔧 Corrections
- **Stabilité**
  - Correction des calculs de ressources
  - Amélioration de la synchronisation des données
  - Résolution des problèmes de state management

---

## [0.1.0a] - 2024-11-28

### 🎉 Version Initiale (MVP)
- **Fonctionnalités de Base**
  - Interface utilisateur React avec Tailwind CSS
  - Système de construction de bâtiments basique
  - Gestion des ressources fondamentale
  - Architecture frontend-only avec données mockées

- **Technologies Implémentées**
  - React 18 avec hooks modernes
  - Tailwind CSS pour le styling
  - Shadcn/ui pour les composants réutilisables
  - Lucide React pour les icônes

### 🎯 Objectifs de Départ
- Créer un jeu de stratégie médiéval inspiré d'OGame
- Interface utilisateur moderne et intuitive
- Mécaniques de jeu engageantes
- Base solide pour le développement futur

---

## 📋 Légende des Types de Changements

- 🎉 **Version Majeure** - Nouvelles fonctionnalités importantes
- ✨ **Nouvelles Fonctionnalités** - Ajout de nouvelles capacités
- 🏗️ **Améliorations** - Améliorations des fonctionnalités existantes
- 🔧 **Corrections** - Corrections de bugs et problèmes
- 🔒 **Sécurité** - Améliorations de sécurité
- 📚 **Documentation** - Changements de documentation uniquement
- 🎨 **Style** - Changements qui n'affectent pas la signification du code
- ♻️ **Refactorisation** - Changements de code qui ne corrigent pas de bug ni n'ajoutent de fonctionnalité
- ⚡ **Performance** - Changements qui améliorent les performances
- ✅ **Tests** - Ajout de tests ou correction de tests existants

---

## 🔗 Liens Utiles

- [Documentation API](./api-docs.md)
- [Guide de Contribution](./CONTRIBUTING.md)
- [Issues GitHub](https://github.com/your-repo/issues)
- [Roadmap du Projet](./ROADMAP.md)

---

**Développé avec ❤️ pour la communauté des jeux de stratégie médiévaux**