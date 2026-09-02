---
name: jekyll-deploy
description: Déploie un site Jekyll sur GitHub Pages. Crée le dépôt distant, active GitHub Pages, initialise Git et pousse le premier commit. Ne gère pas l'archivage dans le registre — c'est une commande séparée.
---

# Skill: Jekyll Deploy

Déploie un site Jekyll existant sur GitHub Pages. Ce skill se concentre uniquement sur la création du dépôt distant, l'activation de GitHub Pages et le push initial.

## Quand utiliser ce skill

- L'utilisateur veut pousser un dépôt Jekyll local vers GitHub
- L'utilisateur veut activer GitHub Pages sur un dépôt
- L'étape de déploiement d'une conversion de quest (après `jekyll-create`)

## Responsabilités

1. Vérifier l'état pré-requis (dossier local, dépôt distant absent, workflow présent)
2. Créer le dépôt distant sur GitHub
3. Activer GitHub Pages
4. Initialiser Git et pousser le premier commit (après confirmation explicite)
5. Vérifier que le déploiement a réellement réussi
6. Mettre à jour les liens de la fiche `En cours` dans `REGISTRY.md`

## Prérequis

- Le dossier du site Jekyll doit exister dans `repos/`
- Le dossier doit contenir au minimum `_config.yml` et `README.md`
- Le fichier `.github/workflows/jekyll.yml` doit être présent (sinon copier depuis le template)
- L'outil `gh` (GitHub CLI) doit être installé et authentifié
- Le dépôt ne doit pas déjà exister sur GitHub

## Flux de travail

### Étape 1 : Informations de déploiement

Demander à l'utilisateur (si non renseigné) :
- **Nom du dépôt** : au format `{domain}-{slug}` (ex: `dev-web-installer-et-utiliser-visual-studio-code`)
- **Organisation** : `simplonco` (par défaut)
- **Visibilité** : public (par défaut)
- **Description** : description de la ressource (optionnel)

### Étape 2 : Vérifications préalables

1. **Vérifier que le dossier local existe** dans `repos/`
2. **Vérifier que le dépôt n'existe pas déjà sur GitHub** :
   ```bash
   gh repo view simplonco/{repo-name} 2>&1
   ```
   Si le dépôt existe déjà → avertir l'utilisateur et demander s'il faut écraser ou annuler.
3. **Vérifier que `jekyll.yml` est présent** dans `.github/workflows/` :
   ```bash
   ls repos/{repo-name}/.github/workflows/jekyll.yml
   ```
   Si absent → le copier depuis `templates/jekyll.yml`.

### Étape 3 : Créer le dépôt distant

```bash
gh repo create simplonco/{repo-name} \
  --public \
  --description "Description de la ressource" \
  --add-readme=false \
  --gitignore=none \
  --license=none
```

### Étape 4 : Activer GitHub Pages

```bash
gh api repos/simplonco/{repo-name}/pages -X POST -f build_type=workflow
```

### Étape 5 : Git init, commit et push

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

### Étape 6 : Vérification post-push

Vérifier que le déploiement a bien démarré :

```bash
gh run list --repo simplonco/{repo-name} --limit 1
```

Si le build échoue → afficher les logs et aider à diagnostiquer.

### Étape 7 : Mise à jour des liens dans le registre

**Ne pas déplacer la fiche vers Terminé** (c'est le rôle de `quest-files-archive`).

Modifier uniquement les liens de la fiche existante dans `REGISTRY.md` section `🔄 En cours` :
- Ajouter ou mettre à jour la ligne `**Dépôt**`
- Ajouter ou mettre à jour la ligne `**Site**`

La fiche reste dans `🔄 En cours` jusqu'à ce que l'utilisateur déclenche explicitement la commande `Archive` ou `Valide`.

### Étape 8 : Confirmation

Résumer les actions effectuées :
- Dépôt GitHub créé : `https://github.com/simplonco/{repo-name}`
- GitHub Pages activé : `https://simplonco.github.io/{repo-name}/`
- Fiche dans le registre : mise à jour des liens dans `🔄 En cours`
- **L'archivage et le passage à Terminé sont des commandes séparées** (ex: `Archive quest-{id}`)
- Appeler l'outil `question` avec `{ "questions": [{ "question": "Le déploiement est terminé. Voulez-vous archiver la quest et passer la fiche à Terminé ?", "header": "Déploiement terminé", "options": [{"label": "Oui", "description": "Archiver et passer à Terminé"}, {"label": "Non", "description": "Laisser dans En cours"}] }] }` pour demander à l'utilisateur s'il veut archiver ou non.

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
| Dépôt déjà existant | Double déploiement | Vérifier avec `gh repo view` avant création |

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
