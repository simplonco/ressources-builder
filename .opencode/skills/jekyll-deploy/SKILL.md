---
name: jekyll-deploy
description: Déploie un site Jekyll sur GitHub Pages et met à jour le registre des contenus. Crée le dépôt distant, active GitHub Pages, initialise Git, pousse le premier commit et archive la fiche.
---

# Skill: Jekyll Deploy

Déploie un site Jekyll existant sur GitHub Pages et gère l'archivage dans le registre.

## Quand utiliser ce skill

- L'utilisateur veut pousser un dépôt Jekyll local vers GitHub
- L'utilisateur veut activer GitHub Pages sur un dépôt
- L'étape de déploiement d'une conversion de quest
- L'étape finale de création d'une ressource (Assistant, From scratch, Conversion)

## Responsabilités

1. Créer le dépôt distant sur GitHub
2. Activer GitHub Pages
3. Initialiser Git et pousser le premier commit
4. **Mettre à jour le registre des contenus** (archivage)

## Prérequis

- Le dossier du site Jekyll doit exister dans `repos/`
- Le dossier doit contenir au minimum `_config.yml` et `README.md`
- L'outil `gh` (GitHub CLI) doit être installé et authentifié

## Flux de travail

### Étape 1 : Informations de déploiement

Demander à l'utilisateur (si non renseigné) :
- **Nom du dépôt** : au format `{domain}-{slug}` (ex: `dev-web-installer-et-utiliser-visual-studio-code`)
- **Organisation** : `simplonco` (par défaut)
- **Visibilité** : public (par défaut)
- **Description** : description de la ressource (optionnel)

### Étape 2 : Créer le dépôt distant

```bash
gh repo create simplonco/{repo-name} \
  --public \
  --description "Description de la ressource" \
  --add-readme=false \
  --gitignore=none \
  --license=none
```

### Étape 3 : Activer GitHub Pages

```bash
gh api repos/simplonco/{repo-name}/pages -X POST -f build_type=workflow
```

Cela configure GitHub Pages pour utiliser le workflow GitHub Actions comme source de build.

### Étape 4 : Git init, commit et push

```bash
cd repos/{repo-name}

# Initialiser le dépôt Git
git init

# Ajouter le remote SSH
git remote add origin git@github.com:simplonco/{repo-name}.git

# Ajouter tous les fichiers
git add .

# Premier commit
git commit -m "Initial commit: setup Jekyll site"

# Push vers GitHub
git push -u origin main
```

### Étape 5 : Archivage dans le registre

1. Lire `REGISTRY.md` section `🔄 En cours`
2. Identifier la fiche correspondant à la ressource déployée :
   - Chercher par slug du dépôt (`{domain}-{slug}`)
   - Ou par titre si le slug ne correspond pas
3. Si la fiche n'est pas trouvée :
   - Avertir l'utilisateur
   - Proposer de créer une nouvelle fiche dans `✅ Terminé`
4. Si la fiche est trouvée :
   - Générer un résumé en analysant le `README.md` du dépôt
   - Demander à l'utilisateur de valider le résumé
   - Déplacer la fiche de `🔄 En cours` → `✅ Terminé` avec le résumé
   - Mettre à jour les compteurs dans les titres de section
   - Maintenir l'ordre alphabétique par titre

**Exemple de résumé :**
```
Ressource sur les variables JavaScript pour débutants. Aborde la création de variables (let, const, var), les règles de nommage (camelCase), la réassignation de valeurs, les opérateurs d'incrément (+++=), et la concaténation de strings. Contenu : ressources externes (javascript.info, YouTube), quiz (2 questions), challenge pratique (renommage de variables). Niveau débutant. Prérequis : JS Basics 01, JS Basics 02.
```

### Étape 6 : Archivage fichiers (quests uniquement)

Si la ressource provient d'une quest JSON (le fichier existe dans `quests/todo/`) :
- Proposer à l'utilisateur d'appeler `quest-files-archive` pour déplacer le JSON et le dépôt local
Sinon :
- déplacer uniquement le dépôt local vers `repos/archives/`

### Étape 7 : Confirmation

Résumer les actions effectuées :
- Dépôt GitHub créé : `https://github.com/simplonco/{repo-name}`
- GitHub Pages activé : `https://simplonco.github.io/{repo-name}/`
- Fiche dans le registre : `✅ Terminé` avec résumé
- Archivage fichiers : effectué / non effectué (quests uniquement)

## Workflow GitHub Actions

Le fichier `.github/workflows/jekyll.yml` doit être présent dans le dépôt. Si absent, le copier depuis le template :

```yaml
name: Deploy Jekyll site to Pages

on:
  push:
    branches: ["main"]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup Ruby
        uses: ruby/setup-ruby@4a9ddd6f338a97768b8006bf671dfbad383215f4
        with:
          ruby-version: '3.1'
          bundler-cache: true
          cache-version: 0
      - name: Setup Pages
        id: pages
        uses: actions/configure-pages@v5
      - name: Build with Jekyll
        run: bundle exec jekyll build --baseurl "${{ steps.pages.outputs.base_path }}"
        env:
          JEKYLL_ENV: production
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v5
```

## URL de déploiement

Après le push, le site sera accessible sur :
```
https://simplonco.github.io/{repo-name}/
```

Le build prend quelques minutes. Vérifier le statut dans l'onglet Actions du dépôt GitHub.

## Erreurs courantes

| Erreur | Cause | Solution |
|--------|-------|----------|
| `gh: not found` | Dépôt pas encore créé | Exécuter `gh repo create` |
| `Pages not enabled` | GitHub Pages non activé | Exécuter `gh api .../pages -X POST` |
| `Permission denied` | Pas les droits sur l'org | Vérifier l'authentification `gh auth status` |
| Build échoue | Gemfile manquant ou incompatible | Vérifier que `Gemfile` est présent et à jour |

---

## Commandes utiles

### Vérifier le statut du dépôt
```bash
gh repo view simplonco/{repo-name}
```

### Vérifier le statut de GitHub Pages
```bash
gh api repos/simplonco/{repo-name}/pages
```

### Voir les builds GitHub Actions
```bash
gh run list --repo simplonco/{repo-name}
```

### Forcer un rebuild
```bash
gh api repos/simplonco/{repo-name}/pages/builds -X POST
```
