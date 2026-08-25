---
name: quest-archive
description: "Archive une quest convertie : génère un résumé, met à jour le registre des contenus, déplace les fichiers vers les archives, et optionnellement pousse vers GitHub."
---

# Skill: Quest Archive

Finalise et archive une conversion de quest. Gère la maintenance du registre des contenus.

## Quand utiliser ce skill

- L'utilisateur a terminé de tester et relire une ressource convertie
- L'utilisateur veut archiver une quest après validation
- L'étape finale d'une conversion de quest (après `jekyll-create` et `jekyll-deploy`)

## Prérequis

- La quest doit exister dans `quests/REGISTRY.md` section `🔄 En cours`
- Le dépôt local doit exister dans `repos/`
- Les tests et relectures doivent être terminés

## Flux de travail

### Étape 1 : Vérification

1. Lister les quests en cours dans `quests/REGISTRY.md` section `🔄 En cours`
2. Si plusieurs quests en cours : demander laquelle archiver
3. Si une seule : la proposer par défaut

### Étape 2 : Génération du résumé

Analyser le contenu du README (`quests/repos/{domain}-{slug}/README.md`) pour générer un résumé incluant :

- **Technologies abordées** : langages, frameworks, outils
- **Niveau de difficulté** : débutant, intermédiaire, avancé
- **Présence de ressources externes** : vidéos YouTube, documentation, etc.
- **Contenus interactifs** : quiz, playground, exercices, stepper, etc.
- **Prérequis** : autres ressources nécessaires
- **Toute autre information utile**

**Exemple de résumé :**
```
Ressource sur les variables JavaScript pour débutants. Aborde la création de variables (let, const, var), les règles de nommage (camelCase), la réassignation de valeurs, les opérateurs d'incrément (+++=), et la concaténation de strings. Contenu : ressources externes (javascript.info, YouTube), quiz (2 questions), challenge pratique (renommage de variables). Niveau débutant. Prérequis : JS Basics 01, JS Basics 02.
```

### Étape 3 : Validation du résumé

1. Inscrire le résumé généré dans le registre (`quests/REGISTRY.md`) sous la fiche de la quest
2. Demander relecture et **validation explicite** avant de poursuivre

### Étape 4 : Mise à jour du registre

Dans `quests/REGISTRY.md` :

1. **Supprimer la fiche** de la section `🔄 En cours`
2. **Ajouter la fiche** dans la section `✅ Terminé` avec :
   - Le résumé comme dernière ligne
   - Tous les champs existants (ID, Domaine, Dépôt, Site)
3. **Mettre à jour les compteurs** dans les titres de section :
   - `🔄 En cours (X)` → décrémenter
   - `✅ Terminé (Y)` → incrémenter
4. **Maintenir l'ordre alphabétique** par titre dans chaque section

**Avant (section En cours) :**
```markdown
### JS Basics 05 - Les instructions conditionnelles
- **ID** : 1270
- **Domaine** : dev-web
- **Dépôt** : [simplonco/dev-web-js-basics-05-les-instructions-conditionnelles](https://github.com/simplonco/dev-web-js-basics-05-les-instructions-conditionnelles)
```

**Après (section Terminé) :**
```markdown
### JS Basics 05 - Les instructions conditionnelles
- **ID** : 1270
- **Domaine** : dev-web
- **Dépôt** : [simplonco/dev-web-js-basics-05-les-instructions-conditionnelles](https://github.com/simplonco/dev-web-js-basics-05-les-instructions-conditionnelles)
- **Site** : [simplonco.github.io/dev-web-js-basics-05-les-instructions-conditionnelles](https://simplonco.github.io/dev-web-js-basics-05-les-instructions-conditionnelles/)
- Ressource sur les instructions conditionnelles JavaScript pour débutants. Aborde les if/else, else if, switch, et les opérateurs de comparaison. Contenu : quiz, exercices pratiques. Niveau débutant.
```

### Étape 5 : Déplacement du JSON

Déplacer le fichier JSON source vers les archives :

```bash
mv quests/todo/quest-{id}.json quests/archives/quest-{id}.json
```

Si le fichier est déjà dans `quests/archives/` (cas d'une re-archivage) : ne rien faire.

### Étape 6 : Déplacement du dépôt local

Déplacer le dépôt généré vers les archives :

```bash
mkdir -p repos/archives
mv repos/{domain}-{slug} repos/archives/{domain}-{slug}
```

### Étape 7 : Proposition de push

Demander à l'utilisateur s'il souhaite pousser le dépôt sur GitHub.

Si oui :
```bash
cd repos/archives/{domain}-{slug}
git add .
git commit -m "Relecture, corrections et validation"
git push -u origin main
```

Si non : informer que le dépôt reste en local et peut être poussé ultérieurement.

### Étape 8 : Confirmation

Résumer les actions effectuées :
- Résumé ajouté au registre
- Fiche déplacée vers `✅ Terminé`
- JSON déplacé vers `quests/archives/`
- Dépôt déplacé vers `repos/archives/`
- Push GitHub : effectué / non effectué

---

## Maintenance du registre

### Structure du registre

```markdown
# Registre des quests

## 🔄 En cours (X)

### Titre de la quest
- **ID** : 1234
- **Domaine** : dev-web
- **Dépôt** : [simplonco/{slug}](https://github.com/simplonco/{slug})
- **Site** : [simplonco.github.io/{slug}](https://simplonco.github.io/{slug}/)

## ✅ Terminé (Y)

### Titre de la quest
- **ID** : 1234
- **Domaine** : dev-web
- **Dépôt** : [simplonco/{slug}](https://github.com/simplonco/{slug})
- **Site** : [simplonco.github.io/{slug}](https://simplonco.github.io/{slug}/)
- Résumé de la ressource...
```

### Règles de maintenance

1. **Ordre alphabétique** : toujours trier par titre (sans emojis) dans chaque section
2. **Compteurs** : mettre à jour les nombres entre parenthèses dans les titres de section
3. **Champs obligatoires** : ID (s'il s'agit d'une conversion de quest), Domaine, Dépôt, Site (sauf si non encore déployé)
4. **Résumé** : ajouté uniquement dans la section `✅ Terminé`

### Recherche de contenu similaire

Quand un formateur crée une nouvelle ressource (via `jekyll-create`), le skill cherche des contenus proches en :
1. Lisant les titres et résumés de toutes les fiches du registre
2. Identifiant les mots-clés en commun (technologies, concepts)
3. Proposant les ressources les plus pertinentes comme inspiration ou alerte de doublon

---

## Erreurs courantes

| Erreur | Cause | Solution |
|--------|-------|----------|
| Quest non trouvée dans le registre | Fiche pas encore créée | Créer la fiche d'abord (via `jekyll-create`) |
| JSON déjà archivé | Double archivage | Vérifier `quests/archives/` avant de déplacer |
| Dépôt local non trouvé | Supprimé manuellement | Vérifier `repos/` et `repos/archives/` |
| Push échoué | Remote pas configuré | Vérifier `git remote -v` |

---

## Commandes utiles

### Lister les quests en cours
```bash
grep -n "🔄 En cours" quests/REGISTRY.md
```

### Compter les quests archivées
```bash
grep -c "^### " quests/REGISTRY.md
```

### Vérifier un dépôt archivé
```bash
ls -la repos/archives/{domain}-{slug}/
```
