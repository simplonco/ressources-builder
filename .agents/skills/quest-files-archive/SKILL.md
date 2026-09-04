---
name: quest-files-archive
description: "Archive les fichiers locaux d'une ressource après déploiement. Déplace le JSON source et le repo local vers les archives."
---

# Skill: Archive les fichiers

Archive les fichiers locaux d'une ressource déjà déployée. Ce skill est déclenché uniquement par une commande explicite de l'utilisateur (ex: `Archive quest-{id}`).

## Quand utiliser ce skill

- L'utilisateur a terminé le déploiement et veut nettoyer les fichiers locaux
- L'utilisateur demande explicitement d'archiver une quest
- Après `jekyll-deploy` — c'est la dernière étape du workflow

## Prérequis

- Le dépôt local doit exister dans `repos/`
- Le dépôt distant doit **réellement exister** sur GitHub (vérifié via `gh repo view`)
- La fiche dans `registry.jsonl` doit être en statut `done` (ajoutée par `jekyll-deploy`)

## Flux de travail

### Étape 1 : Vérification que le déploiement existe

Vérifier que le dépôt distant existe **réellement** sur GitHub (et pas seulement dans le registre) :

```bash
gh repo view simplonco/{repo-name} --json name,createdAt
```

Si le dépôt n'existe pas :
- **Refuser l'archivage**
- Informer l'utilisateur : "Le dépôt GitHub {repo-name} n'existe pas encore. Exécute d'abord `Déploie {slug}`."
- Proposer via l'outil `question` avec `{ "questions": [{ "question": "Le dépôt GitHub n'existe pas encore. Déployer maintenant ?", "header": "Dépôt", "options": [{"label": "Déployer maintenant", "description": "Appeler jekyll-deploy"}, {"label": "Annuler", "description": "Ne rien faire"}] }] }`

### Étape 2 : Déplacement du JSON (optionnel)

Si un fichier JSON source existe dans `quests/todo/quest-{id}.json` (ressources créées via quest) :

```bash
mv quests/todo/quest-{id}.json quests/archives/quest-{id}.json
```

Si le fichier est déjà dans `quests/archives/` (cas d'un re-archivage) : ne rien faire.

**Variantes** : pas de JSON à déplacer — passer directement à l'étape 3.

### Étape 3 : Déplacement du dépôt local

Déplacer le dépôt généré vers les archives :

```bash
mkdir -p repos/archives
mv repos/{domain}-{slug} repos/archives/{domain}-{slug}
```

### Étape 4 : Confirmation

Résumer les actions effectuées :
- JSON déplacé vers `quests/archives/` (si applicable)
- Dépôt déplacé vers `repos/archives/`

---

## Erreurs courantes

| Erreur | Cause | Solution |
|--------|-------|----------|
| Dépôt distant inexistant | Pas encore déployé | Exécuter `Déploie {slug}` avant d'archiver |
| JSON déjà archivé | Double archivage | Vérifier `quests/archives/` avant de déplacer |
| Dépôt local non trouvé | Supprimé manuellement | Vérifier `repos/` et `repos/archives/` |

---

## Commandes utiles

### Vérifier un dépôt archivé
```bash
ls -la repos/archives/{domain}-{slug}/
```

### Vérifier un JSON archivé
```bash
ls -la quests/archives/quest-{id}.json
```

### Vérifier l'existence du dépôt distant
```bash
gh repo view simplonco/{repo-name}
```
