---
name: json-to-github
description: Orchestrateur de conversion de fichiers JSON de quêtes en dépôts GitHub utilisant le thème Jekyll Simplonline. Coordonne les skills jekyll-create, jekyll-deploy et quest-archive.
---

# Skill: JSON to GitHub (Orchestrateur)

Convertit les fichiers JSON de quêtes en dépôts GitHub. Ce skill coordonne les skills spécialisés pour réaliser le workflow complet.

## Quand utiliser ce skill

- L'utilisateur demande de convertir une quest JSON en dépôt GitHub
- L'utilisateur veut lister les quests en attente
- Workflow complet de conversion : création → déploiement → archivage

## Skills coordonnés

| Skill | Rôle |
|-------|------|
| `jekyll-create` | Conversion du JSON en markdown Jekyll + templates |
| `jekyll-deploy` | Déploiement sur GitHub Pages |
| `quest-archive` | Archivage + maintenance du registre |

## Structure du projet

```
odyssey-quests-to-github/
├── quests/
│   ├── todo/                          # JSON en attente
│   ├── archives/                      # JSON traités
│   └── REGISTRY.md                    # Registre des correspondances
├── repos/                             # Dépôts générés (sortie)
│   └── archives/                      # Dépôts archivés
└── AGENTS.md
```

## Flux de travail

### Conversion complète d'une quest

Quand l'utilisateur demande de convertir une quest (ex: "Convertis quest-2114.json") :

#### Étape 1 : Vérification des doublons

1. Lire `quests/REGISTRY.md`
2. Chercher le `quest_id` dans toutes les fiches
3. Si trouvé :
   - Informer l'utilisateur : "Cette quest a déjà été convertie : {URL_DU_DEPOT}"
   - Demander confirmation pour continuer (écraser) ou annuler
4. Si non trouvé : continuer

#### Étape 2 : Demander le domaine

Demander à l'utilisateur la valeur de {domain} :
- dev-web
- data
- infra
- design
- autre (préciser)

#### Étape 3 : Appeler jekyll-create (mode conversion)

Déléguer au skill `jekyll-create` avec les paramètres :
- `mode`: "conversion"
- `quest_id`: l'identifiant de la quest
- `source`: `quests/todo/quest-{id}.json`
- `domain`: la valeur choisie

Le skill `jekyll-create` s'occupe de :
- Parser le JSON
- Appliquer les mappings de syntaxe markdown
- Télécharger les images
- Générer les fichiers Jekyll (README.md, solution.md, templates)
- Ajouter la fiche dans `REGISTRY.md` section `🔄 En cours`

#### Étape 4 : Proposer le déploiement

Demander à l'utilisateur s'il souhaite déployer sur GitHub Pages.

Si oui : appeler `jekyll-deploy` avec :
- `repo-name`: `{domain}-{slug}`
- `description`: la description de la quest

Le skill `jekyll-deploy` s'occupe de :
- Créer le dépôt distant sur GitHub
- Activer GitHub Pages
- Initialiser Git + premier commit

#### Étape 5 : Informer pour les tests

Donner à l'utilisateur les prochaines étapes :
1. Tester localement : `cd repos/{domain}-{slug} && bundle exec jekyll serve --livereload`
2. Vérifier le rendu sur `http://localhost:4000`
3. Quand satisfait : appeler "Archiver quest-{id}" ou "Archiver {slug}"

#### Étape 6 : Proposition d'archivage (ultérieur)

Quand l'utilisateur confirme que les tests et relectures sont terminés :
- Appeler `quest-archive` avec le quest_id

Le skill `quest-archive` s'occupe de :
- Générer un résumé de la quest
- Inscrire le résumé dans le registre
- Déplacer la fiche `🔄 En cours` → `✅ Terminé` dans le registre
- Déplacer le JSON vers `quests/archives/`
- Déplacer le dépôt local vers `repos/archives/`
- Proposer le push GitHub

---

### Listing des quests en attente

Quand l'utilisateur veut voir les quests en attente :

1. Lire les fichiers dans `quests/todo/`
2. Lister chaque quest avec :
   - Nom du fichier
   - `quest_id` (extrait du nom)
   - Statut dans le registre (en cours / non convertie)
3. Afficher le résultat

---

## Commandes utiles

### Lister les quests en attente
```bash
ls quests/todo/
```

### Vérifier le registre
```bash
cat quests/REGISTRY.md
```

### Voir les dépôts générés
```bash
ls repos/
```

### Voir les archives
```bash
ls repos/archives/
ls quests/archives/
```

---

## Limitations de l'orchestrateur

Ce skill ne contient aucune logique de :
- Conversion markdown (délégué à `jekyll-create`)
- Déploiement GitHub (délégué à `jekyll-deploy`)
- Archivage (délégué à `quest-archive`)

Il est uniquement responsable de :
- La coordination des skills
- La vérification des doublons
- Le choix du domaine
- Le workflow utilisateur (questions, confirmations)
