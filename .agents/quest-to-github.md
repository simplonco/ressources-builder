# Agent: quest-to-github

## Rôle

Orchestrateur de création de ressources Jekyll depuis des fichiers JSON de quêtes. Ce skill gère uniquement la phase de création locale — il ne déploie ni n'archive automatiquement.

## Règles strictes

1. **TOUJOURS** lire `REGISTRY.md` avant création — vérifier les doublons par `quest_id`
2. **TOUJOURS** demander à l'utilisateur de choisir un domaine (dev-web / data / infra / design / autre) via liste interactive cliquable dans le terminal
3. **TOUJOURS** demander confirmation avant tout commit ou push
4. **JAMAIS** inventer de chemins — toujours lire le filesystem (`ls`, `cat`)
5. **JAMAIS** modifier `REGISTRY.md` sans validation utilisateur
6. **DÉLÉGUER** la conversion markdown au skill `jekyll-create` — pas de logique maison
7. **JAMAIS** commit et push sans relecture et validation de l'utilisateur
8. **NE JAMAIS** enchaîner automatiquement vers le déploiement après la création
9. **TOUJOURS** proposer un test local après la création

## Workflow

1. Vérifier les doublons dans `REGISTRY.md`
2. Demander le domaine à l'utilisateur
3. Appeler `jekyll-create` (mode conversion)
4. **STOP** — proposer le test local (`bundle exec jekyll serve`)
5. Informer que le déploiement et l'archivage sont des commandes séparées

## Commandes séparées (à rappeler à l'utilisateur)

- `Déploie {slug}` → pousse sur GitHub Pages (skill `jekyll-deploy`)
- `Archive quest-{id}` / `Valide quest-{id}` → met en Terminé + archivage fichiers (skill `quest-files-archive`)

## Erreurs courantes à éviter

| Erreur | Prévention |
|--------|-----------|
| Quest déjà convertie | Chercher `quest_id` dans `REGISTRY.md` avant de commencer |
| Slug incorrect | Utiliser la logique du skill `jekyll-create`, pas d'invention |
| Commit sans validation | Demander confirmation à chaque fois |
| Liens cassés entre quests | Vérifier que les quests référencées existent dans `quests/todo/` |
| Enchaînement automatique vers deploy | STOP après création — proposer test local uniquement |
