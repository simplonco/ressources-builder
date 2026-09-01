# Agent: jekyll-deploy

## Rôle

Déploie un site Jekyll existant sur GitHub Pages. Ce skill se concentre uniquement sur la création du dépôt distant, l'activation de GitHub Pages et le push initial. Il ne gère pas l'archivage dans le registre.

## Règles strictes

1. **TOUJOURS** vérifier que le dossier du site existe dans `repos/` avant de commencer
2. **JAMAIS** créer un dépôt sans avoir vérifié qu'il n'existe pas déjà sur GitHub
3. **JAMAIS** activer GitHub Pages sans que le dépôt distant existe
4. **TOUJOURS** vérifier que `jekyll.yml` est présent dans `.github/workflows/` avant le push
5. **TOUJOURS** demander une confirmation explicite avant le push (règle globale : jamais de push sans autorisation)
6. **TOUJOURS** vérifier que le déploiement a réellement réussi après le push
7. **NE JAMAIS** déplacer la fiche vers Terminé — uniquement mettre à jour les liens dans En cours
8. **TOUJOURS** rappeler à l'utilisateur que l'archivage est une commande séparée

## Workflow

1. Vérifier l'existence du dossier dans `repos/`
2. Vérifier que le dépôt n'existe pas déjà sur GitHub (`gh repo view`)
3. Vérifier que `jekyll.yml` est présent dans `.github/workflows/`
4. Créer le dépôt distant (`gh repo create`)
5. Activer GitHub Pages (`gh api .../pages`)
6. **Demander confirmation explicite** avant le push
7. Git init + commit + push
8. Vérifier le déploiement (`gh run list`)
9. Mettre à jour les liens Dépôt/Site de la fiche dans `REGISTRY.md` section `En cours`
10. Rappeler que l'archivage est une commande séparée (`Archive quest-{id}`)

## Erreurs courantes à éviter

| Erreur | Prévention |
|--------|-----------|
| Dépôt déjà existant | Vérifier avec `gh repo view` avant création |
| GitHub Pages non activé | Appeler l'API Pages après la création du dépôt |
| `jekyll.yml` manquant | Vérifier sa présence dans `.github/workflows/` |
| Push sans confirmation | Demander confirmation explicite avant le push |
| Push sans commit | S'assurer que `git add . && git commit` a bien été fait |
| Déploiement échoué | Vérifier `gh run list` après le push |
| Fiche déplacée vers Terminé | Ne PAS déplacer — uniquement mettre à jour les liens dans En cours |
| Archivage automatique | Rappeler que l'archivage est une commande séparée |
