---
name: quest-files-archive
description: "Archive les fichiers d'une quest convertie : déplace le JSON et le dépôt local vers les archives."
---

# Skill: Quest Files Archive

Archive les fichiers d'une quest convertie après validation et déploiement.

## Quand utiliser ce skill

- L'utilisateur a terminé de tester et relire une ressource convertie
- L'étape finale d'une conversion de quest (après `jekyll-create` et `jekyll-deploy`)
- L'archivage dans le registre est déjà fait par `jekyll-deploy`

## Prérequis

- Le dépôt local doit exister dans `repos/`
- Le JSON source doit exister dans `quests/todo/`
- Les tests et relectures doivent être terminés
- La fiche dans le registre est déjà en section `✅ Terminé` (géré par `jekyll-deploy`)

## Flux de travail

### Étape 1 : Déplacement du JSON

Déplacer le fichier JSON source vers les archives :

```bash
mv quests/todo/quest-{id}.json quests/archives/quest-{id}.json
```

Si le fichier est déjà dans `quests/archives/` (cas d'une re-archivage) : ne rien faire.

### Étape 2 : Déplacement du dépôt local

Déplacer le dépôt généré vers les archives :

```bash
mkdir -p repos/archives
mv repos/{domain}-{slug} repos/archives/{domain}-{slug}
```

### Étape 3 : Confirmation

Résumer les actions effectuées :
- JSON déplacé vers `quests/archives/`
- Dépôt déplacé vers `repos/archives/`

---

## Erreurs courantes

| Erreur | Cause | Solution |
|--------|-------|----------|
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
