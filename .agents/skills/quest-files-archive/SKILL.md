---
name: quest-files-archive
description: "Valide et archive une ressource Jekyll après relecture. Déplace la fiche vers Terminé dans le registre, puis archive les fichiers (JSON + repo local)."
---

# Skill: Valide et Archive

Valide une ressource Jekyll après relecture et la met en archive. Ce skill est déclenché uniquement par une commande explicite de l'utilisateur (ex: `Archive quest-{id}` / `Valide quest-{id}` / `J'ai fini de relire`).

## Quand utiliser ce skill

- L'utilisateur a terminé de tester et relire une ressource convertie
- L'utilisateur demande explicitement d'archiver ou de valider une quest
- Après `jekyll-create` et `jekyll-deploy` — c'est la dernière étape du workflow

## Prérequis

- Le dépôt local doit exister dans `repos/`
- Le dépôt distant doit **réellement exister** sur GitHub (vérifié via `gh repo view`)
- Les tests et relectures doivent être terminés (confirmés par l'utilisateur)
- La fiche dans le registre doit être en statut `en_cours` avec des liens Dépôt/Site dans `registry.jsonl`
- **Optionnel** : le JSON source dans `quests/todo/` (uniquement pour les ressources créées via quest JSON, pas pour les variantes)

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

### Étape 2 : Génération du résumé

1. Lire le `README.md` du dépôt local (`repos/{repo-name}/`)
2. Générer un résumé concis (2-4 phrases) décrivant :
   - Le sujet de la ressource
   - Le public cible (niveau)
   - Les contenus principaux (exercices, vidéos, quiz...)
   - Les prérequis éventuels

Exemple de résumé :
```
Ressource sur les variables JavaScript pour débutants. Aborde la création de variables (let, const, var), les règles de nommage (camelCase), la réassignation de valeurs, les opérateurs d'incrément (+++=), et la concaténation de strings. Contenu : ressources externes (javascript.info, YouTube), quiz (2 questions), challenge pratique. Niveau débutant. Prérequis : JS Basics 01, JS Basics 02.
```

3. Appeler l'outil `question` avec `{ "questions": [{ "question": "Résumé : {résumé}. Valider ou corriger ?", "header": "Résumé", "options": [{"label": "Valider le résumé", "description": "Continuer avec ce résumé"}, {"label": "Corriger", "description": "Modifier le résumé"}] }] }` avant de continuer

### Étape 3 : Déplacement de la fiche dans le registre

1. Lire `registry.jsonl`
2. Identifier la fiche correspondant à la ressource :
   - Chercher par slug du dépôt (`{domain}-{slug}`)
   - Ou par quest_id si c'est une conversion de quest
   - Ou par titre (si recherche par titre)
3. Si la fiche n'est pas trouvée :
   - Avertir l'utilisateur
   - Proposer de créer une nouvelle fiche dans le registre (status `done`)
4. Si la fiche est trouvée :
   - Mettre à jour le champ `status` de `"en_cours"` vers `"done"`
   - Ajouter le résumé dans le champ `summary`
   - Régénérer le registre du domaine :
     ```bash
     python3 scripts/generate-registry.py
     ```

### Étape 4 : Régénération des registres

Régénérer les fichiers dérivés à partir du JSONL :

```bash
python3 scripts/generate-registry.py
```

Cela met à jour automatiquement :
- Les compteurs dans `REGISTRY.md` (index)
- Les tableaux dans `registry/{domaine}.md`

### Étape 5 : Déplacement du JSON (optionnel)

Si un fichier JSON source existe dans `quests/todo/quest-{id}.json` (ressources créées via quest) :

```bash
mv quests/todo/quest-{id}.json quests/archives/quest-{id}.json
```

Si le fichier est déjà dans `quests/archives/` (cas d'un re-archivage) : ne rien faire.

**Variantes** : pas de JSON à déplacer — passer directement à l'étape 6.

### Étape 6 : Déplacement du dépôt local

Déplacer le dépôt généré vers les archives :

```bash
mkdir -p repos/archives
mv repos/{domain}-{slug} repos/archives/{domain}-{slug}
```

### Étape 7 : Confirmation

Résumer les actions effectuées :
- Résumé validé : (le résumé choisi)
- Fiche dans le registre : déplacée de `en_cours` → `done`
- JSON déplacé vers `quests/archives/` (si applicable)
- Dépôt déplacé vers `repos/archives/`
- Compteurs mis à jour

---

## Erreurs courantes

| Erreur | Cause | Solution |
|--------|-------|----------|
| Dépôt distant inexistant | Pas encore déployé | Exécuter `Déploie {slug}` avant d'archiver |
| JSON déjà archivé | Double archivage | Vérifier `quests/archives/` avant de déplacer |
| Dépôt local non trouvé | Supprimé manuellement | Vérifier `repos/` et `repos/archives/` |
| Fiche introuvable dans En cours | Fiche déjà déplacée ou inexistante | Vérifier registry.jsonl |

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
