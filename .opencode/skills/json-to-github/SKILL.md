---
name: json-to-github
description: Ce skill convertit les fichiers JSON de quêtes (stockés dans `quests/todo/`) en dépôts GitHub utilisant le thème Jekyll Simplonline.
---

# Skill: JSON to GitHub

Ce skill convertit les fichiers JSON de quêtes (stockés dans `quests/todo/`) en dépôts GitHub utilisant le thème Jekyll Simplonline.

## Quand utiliser ce skill

- L'utilisateur demande de convertir une quest JSON en dépôt GitHub
- L'utilisateur demande de lister les quests en attente
- L'utilisateur veut pousser un dépôt local vers GitHub

## Structure du projet

```
odyssey-quests-to-github/
├── .opencode/skills/json-to-github/   # Ce skill
├── quests/
│   ├── todo/                          # JSON en attente
│   ├── archives/                      # JSON traités
│   └── REGISTRY.md                    # Registre des correspondances quest → repo
├── repos/                             # Dépôts générés (sortie)
└── AGENTS.md
```

## Flux de travail

### 1. Conversion d'une quest

Quand l'utilisateur demande de convertir une quest (ex: "Convertis quest-2114.json") :

0. **Vérifier si la quest a déjà été convertie** : lire `quests/REGISTRY.md` et chercher le quest_id. Si trouvé, informer l'utilisateur ("Cette quest a déjà été convertie : {URL}") et demander confirmation pour continuer (écraser le dépôt existant) ou annuler.
   - Si la quest n'est pas dans le registre, **ajouter une ligne** avec :
     - Quest ID, Titre, Domaine (à déterminer à l'étape 1)
     - URL GitHub du dépôt (sera remplie à l'étape 9)
     - URL de déploiement : `https://simplonco.github.io/{domain}-{slug}/`
     - État : `en cours`
     - Résumé : vide (sera rempli à l'archivage)
1. Demander à l'utilisateur la valeur de {domain} : à quel domaine est affecté ce contenu ? Valeurs possibles :
   - dev-web
   - data
   - infra
   - autre : préciser
2. **Lire le fichier JSON** depuis `quests/todo/`
3. **Extraire les métadonnées** :
   - `quest_id` → identifiant unique
   - `revision.title` → titre de la quest
   - `pages[]` → tableau des pages (content, solution)
4. **Slugifier le titre** pour le nom du dépôt :
   - Supprimer les emojis (ex: 👩‍🏫, ✅, 🤓)
   - Minuscules
   - Remplacer les espaces par des tirets
   - Supprimer les caractères spéciaux (ponctuation, accents)
   - Ex: "👩‍🏫 Installer et utiliser Visual Studio Code" → `installer-et-utiliser-visual-studio-code`
5. **Vérifier l'unicité du slug** : si `repos/{domain}-{slug}/` existe déjà, ajouter le `quest_id` : `{domain}-{slug}-{quest_id}`
6. **Créer le dossier** `repos/{domain}-{slug}/` et le sous-dossier `repos/{domain}-{slug}/images/`
7. **Générer les fichiers Jekyll** :
   - `README.md` → page principale (page avec chapter_type="content"). Ajouter un lien vers la page solution si elle existe en bas de page.
   - `solution.md` → page solution (si chapter_type="solution" existe). Ajouter " - Solution" au titre de la page dans le front matter.
   - `_config.yml` → copier depuis `templates/_config.yml` et remplacer les placeholders :
     - `{{TITLE}}` → "`revision.title`"
     - `{{DESCRIPTION}}` → "`revision.description`" (ou valeur par défaut si `null`)
   - `Gemfile` → copier depuis `templates/Gemfile`
   - `.gitignore` → copier depuis `templates/.gitignore`
   - `jekyll.yml` → copier depuis `templates/jekyll.yml` vers `repos/{domain}-{slug}/.github/workflows/jekyll.yml`
8. **Télécharger les images** :
   - Extraire toutes les URLs d'images du markdown (`![...](...)`)
   - Télécharger chaque image dans `repos/{domain}-{slug}/images/`
   - Renommer les fichiers avec un nom descriptif (pas d'URL longue)
   - Réécrire les URLs dans le markdown : `![alt](images/nom-fichier.ext)`
9. Créer le dépôt vide distant sur GitHub via `gh repo create` :
   - compte : `simplonco`
   - nom du dépôt : `{domain}-{slug}` 
   - description : `revision.description`
   - visibilité : public.
   - add a README file : non
   - gitignore : none
   - license : none
   - pousser le dépôt : non (sera fait manuellement par l'utilisateur après tests)
10. **Activer GitHub Pages** :
   ```bash
   gh api repos/simplonco/{domain}-{slug}/pages -X POST -f build_type=workflow
   ```
11. **Git init et premier commit** : 
   - initialiser un dépôt Git dans le répertoire
   - ajouter le remote `origin` au format ssh `git@github.com:simplonco/{domain}-{slug}.git` dans le dépôt local lié au dépôt GitHub créé précédemment
   - effectuer un premier commit d'initialisation
11. **Tester localement** (effectué manuellement par l'utilisateur) : `bundle exec jekyll serve --livereload`

### 2. Archiver

Lorsque l'utilisateur confirme que les tests, reviews et ajustement sont terminés :
    - si nécessaire, effectuer un commit pour sauvegarder les modifications 
    ```bash
    cd repos/{domain}-{slug}
    git add .
    git commit -m "Corrections après tests et review : {details des changements}"
    ```
    - **Générer un résumé** de la quest en analysant le contenu JSON source. Le résumé doit inclure :
      - Technologies abordées
      - Niveau de difficulté
      - Présence de ressources externes (vidéos YouTube, documentation, etc.)
      - Contenus interactifs (quiz, playground, exercices, etc.) mais pas les informations de mise en page (ex : "blocs d'exercices", "alertes", etc.)
      - Toute autre information utile
    - **Présenter le résumé à l'utilisateur** et attendre sa **validation explicite** avant de poursuivre
    - **Mettre à jour le registre** dans `quests/REGISTRY.md` :
      - Passer la valeur de la colonne `État` de `en cours` à `terminé`
      - Ajouter le résumé validé dans la colonne `Résumé`
    - déplacer le JSON vers `quests/archives/`
    - demander si le dossier doit être poussé sur GitHub. Si oui, utiliser la commande :
    ```bash
    git push -u origin main
    ```
    - **Déplacer le dépôt local vers les archives** :
    ```bash
    mkdir -p repos/archives
    mv repos/{domain}-{slug} repos/archives/{domain}-{slug}
    ```

## Front Matter des pages

Définir le front matter pour chaque page :
```yaml
---
title: {{TITLE}}
description: {{DESCRIPTION}}
show_toc: true
---
```

S'il s'agit d'une page solution, ajouter :
```yaml
parent: titre-de-la-page-principale
```

## Conversion du markdown

### Mapping des syntaxes

| Syntaxe source | Équivalent Jekyll |
|---------------|-------------------|
| ` ```alert-info\n...\n``` ` | Contenu avec `{:.alert-info}` après chaque paragraphe |
| ` ```alert-warning\n...\n``` ` | Contenu avec `{:.alert-warning}` après chaque paragraphe |
| ` ```xtext story\n...\n``` ` | Bloc quote `> ` avec chaque ligne préfixée |
| ` ```js live\n...\n``` ` | Playground interactif (`playground.html`) |
| ` ```quests\n2114\n``` ` | Lien relatif vers le repo de la quest |
| ` ```ressource\n...\n``` ` | Bloc avec `{:.alert-info}` + contenu formaté |

### Règles de conversion

#### Remplacement de termes

| Terme source | Terme cible |
|--------------|-------------|
| `quête` | `ressource` |
| `À la fin de cette quête tu sauras` | `Objectifs` |

#### Titres
- Vérifier que les titres sont bien formatés en Markdown (`#`, `##`, `###`, etc.) et respectent une hiérarchie logique.
- Supprimer le titre Sommaire si présent, car Jekyll génère automatiquement la table des matières.

#### Listes

Avant :
````
✅ Qu'est ce qu'un éditeur de code
✅ Comment installer Visual Studio Code.
````

Après :
```markdown
- ✅ Qu'est ce qu'un éditeur de code
- ✅ Comment installer Visual Studio Code.
```

#### Balisage spécial
Avant :
```
:def[HTML]{value=”HyperText Markup Language”}
```
Après :
```markdown
HTML (HyperText Markup Language)
```

#### alert-info / alert-warning

Avant :
````
```alert-info
Contenu de l'alerte
```
````

Après :
```markdown
Contenu de l'alerte
{:.alert-info}
```

#### xtext story

Avant :
````
```xtext story
Bonjour,
Ceci est un brief.
```
````

Après :
```markdown
> Bonjour,
> Ceci est un brief.
```

#### xtext arrow

Avant :
````
```xtext arrow
**🎯 À toi de jouer !**
Ceci est un brief.
```
````

Après :
```markdown
> #### 🎯 À toi de jouer !
> Ceci est un brief.
```

Note : ajuster le niveau d'intertitre en cohérence avec la hiérarchie de la page.

#### js live (→ Playground interactif)

Les blocs `js live` contiennent du code HTML/CSS/JS séparé par des marqueurs `!--- nom-fichier.ext`. Le parser doit :
1. Séparer le bloc par les marqueurs `!--- `
2. Identifier le type selon le nom du fichier (`.html` → `my_html`, `.css` → `my_css`, `.js` → `my_js`)
3. Générer les blocs `{% capture %}` et l'include `playground.html`

**Avant** :
````
```js live
!--- index.html

<!DOCTYPE html>
<html>...</html>

!--- style.css

:root { ... }
```
````

**Après** :
````markdown
{% capture my_html %}
<!DOCTYPE html>
<html>...</html>
{% endcapture %}

{% capture my_css %}
:root { ... }
{% endcapture %}

{% include playground.html
  id="demo"
  initial_html=my_html
  initial_css=my_css
%}
````

**Variante inline** (si un seul type de code) :
````markdown
{% include playground.html
  id="demo"
  initial_html="<h1>Hello</h1>"
%}
````

**Règles** :
- L'`id` doit être unique par page (utiliser un slug ou un numéro)
- Si le bloc contient uniquement HTML, utiliser la syntaxe inline
- Si le bloc contient HTML + CSS + JS, utiliser les 3 captures

#### quests (liens vers autres quests)

Avant :
````
```quests
2114
```
````

Après :
```markdown
[Voir la ressource "Installer et utiliser Visual Studio Code"](https://simplonco.github.io/dev-web-installer-et-utiliser-visual-studio-code/)
```

Note : utiliser l'**URL de déploiement** depuis `quests/REGISTRY.md` (colonne "URL de déploiement"). Si la quest cible n'est pas dans le registre, avertir l'utilisateur et lui demander ce qu'il souhaite faire : ignorer le lien, le renseigner manuellement ou le mettre à jour plus tard.

#### ressource

Avant :
````
```ressource
https://example.com
# Titre de la ressource
Description de la ressource
```
````

Après :
```markdown
**Titre de la ressource**

Description de la ressource

[Lien vers la ressource](https://example.com)
{:.alert-info}
```

#### Liens vers des ressources externes
- Récupérer le titre de la page web pour l'utiliser comme titre de la ressource. Exemple : `https://developer.mozilla.org/fr/docs/Web/HTML` → `HTML: HyperText Markup Language`
- Formater le lien en markdown : `[Titre de la ressource](URL)`

## Templates

Les templates se trouvent dans `templates/` :
- `_config.yml` : Configuration Jekyll avec le thème simplonline
- `Gemfile` : Dépendances Ruby (github-pages, webrick)
- `.gitignore` : Fichiers à ignorer (_site/, .jekyll-cache/, etc.)

## Structure d'un dépôt généré

```
repos/{domain}-{slug}/
├── README.md        # Page principale (content)
├── solution.md      # Page solution (si existe)
├── images/          # Images téléchargées
├── _config.yml      # Config Jekyll
├── Gemfile          # Dépendances
└── .gitignore       # Fichiers à ignorer
```

## Commandes Jekyll pour test local

### Installation des dépendances

```bash
cd repos/{domain}-{slug}
bundle install
```

### Lancer le serveur local

```bash
bundle exec jekyll serve --livereload
```

Le site sera disponible sur `http://localhost:4000`

## Limitations

- Les emojis dans les titres sont supprimés lors du slugifield
- Les images externes (storage.googleapis.com) sont téléchargées dans le dossier `/images` et les URLs réécrites
- Les liens vers d'autres quests utilisent le format `quest-{id}` si le slug n'est pas connu
