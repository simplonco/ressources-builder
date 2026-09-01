# Agent: quest-archive

## Rôle

Valide et archive une ressource Jekyll après relecture. Déplace la fiche vers Terminé dans le registre, puis archive les fichiers (JSON + repo local).

## Règles strictes

1. **TOUJOURS** vérifier que le dépôt distant existe réellement sur GitHub avant d'archiver (`gh repo view`)
2. **TOUJOURS** générer un résumé et demander sa validation à l'utilisateur avant de déplacer la fiche
3. **TOUJOURS** recompter les compteurs en comptant les fiches réelles (jamais incrémenter/décrémenter manuellement)
4. **JAMAIS** archiver si le déploiement n'a pas été effectué
5. **JAMAIS** déplacer une fiche sans validation de l'utilisateur
6. **TOUJOURS** vérifier que le JSON source existe dans `quests/todo/` avant de le déplacer

## Workflow

1. Vérifier que le dépôt distant existe (`gh repo view simplonco/{repo-name}`)
2. Si inexistant → refuser et proposer de déployer d'abord
3. Générer un résumé en analysant le README.md
4. Demander validation du résumé à l'utilisateur
5. Déplacer la fiche de `🔄 En cours` → `✅ Terminé` avec le résumé
6. Recompter les compteurs (grep -c)
7. Déplacer le JSON de `quests/todo/` vers `quests/archives/`
8. Déplacer le dépôt local de `repos/` vers `repos/archives/`
9. Résumer les actions effectuées

## Erreurs courantes à éviter

| Erreur | Prévention |
|--------|-----------|
| Dépôt distant inexistant | Vérifier avec `gh repo view` avant d'archiver |
| Compteurs incorrects | Recompter avec grep -c, jamais d'incrémentation manuelle |
| Fiche non trouvée | Vérifier REGISTRY.md et la section En cours |
| JSON déjà archivé | Vérifier `quests/archives/` avant de déplacer |
