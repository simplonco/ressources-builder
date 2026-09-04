---
name: jekyll-create
description: Assistant de création de ressources Jekyll avec le thème Simplonline. Gère la conversion depuis JSON, la création depuis zéro via un assistant interactif, et l'ajout de brouillons dans REGISTRY.md.
---

# Skill: Jekyll Create

Assistant de création de ressources Jekyll utilisant le thème Simplonline.

## Quand utiliser ce skill

- L'utilisateur veut créer une ressource Jekyll (depuis un fichier JSON ou depuis zéro)
- L'utilisateur veut convertir un fichier de quest JSON en markdown Jekyll
- L'utilisateur veut créer un squelette de contenu avec le thème Simplonline

## Modes de fonctionnement

| Mode | Déclencheur | Description |
|------|-------------|-------------|
| **Assistant** | "Créer une ressource Jekyll" | Questionnaire interactif → recherche dans le registre → génère squelette |
| **Conversion** | "Convertir quest-{id}.json" | Parse JSON → applique mappings → génère markdown complet |
| **From scratch** | "Créer depuis mon markdown" | Applique front matter + templates Jekyll uniquement |

## Structure du projet

```
ressources-builder/
├── .agents/skills/jekyll-create/   # Ce skill
│   ├── SKILL.md
│   └── templates/
│       ├── _config.yml               # Configuration Jekyll
│       ├── Gemfile                   # Dépendances Ruby
│       ├── .gitignore                # Fichiers à ignorer
│       └── jekyll.yml                # Workflow GitHub Actions
├── quests/
│   ├── todo/                         # JSON en attente
│   └── archives/                     # JSON traités
├── repos/                            # Dépôts générés (sortie)
├── registry.jsonl                    # Registre source de vérité (JSONL)
├── registry/                         # Registres par domaine (tableaux générés)
│   ├── dev-web.md
│   └── design.md
├── REGISTRY.md                       # Index du registre (liens vers domaines)
└── AGENTS.md
```

---

## Mode Assistant

Quand l'utilisateur demande de créer une ressource Jekyll sans fichier JSON source.

### Étape 1 : Questionnaire

Poser les questions suivantes à l'utilisateur :

**1. Besoin d'assistance pour le squelette ?**
Appeler l'outil `question` avec `{ "questions": [{ "question": "Besoin d'assistance pour le squelette ?", "header": "Squelette", "options": [{"label": "Oui", "description": "Continuer avec le questionnaire"}, {"label": "Non", "description": "Mode from scratch"}] }] }` :
- **Oui** → continuer
- **Non** → passer au mode "From scratch" (l'utilisateur fournit son propre markdown)

**2. Quel domaine ?**
Appeler l'outil `question` avec `{ "questions": [{ "question": "Quel est le domaine ?", "header": "Domaine", "options": [{"label": "dev-web", "description": "Développement web"}, {"label": "data", "description": "Data / IA"}, {"label": "infra", "description": "Infrastructure / DevOps"}, {"label": "design", "description": "Design / UI-UX"}] }] }`. NE JAMAIS demander de taper au clavier.

**3. Objectifs et notions abordées ?**
- Demander les objectifs pédagogiques et les notions techniques couvertes
- Analyser ces informations pour la recherche de contenu similaire

**4. Recherche de contenu similaire**
- Découper le sujet en mots individuels (ex : « React Context » → `react`, `context`)
- **Passage 1** : un appel à l'outil `grep` par mot, union des résultats (dédoublonner par slug) :
  ```
  grep(pattern="react", path=".", include="registry.jsonl")
  grep(pattern="context", path=".", include="registry.jsonl")
  ```
  Extraire les champs `title`, `site_url` et `repo_url` de chaque ligne retournée.
- **Passage 2** (si le passage 1 donne 0 résultat) : réessayer avec synonymes, traductions françaises ou termes élargis (ex : `context` → `état`, `state`, `composant`, `props`)
- Si trouvé : afficher les ressources avec des liens cliquables :
  ```
  Ressources similaires trouvées :
  - [Titre](site_url)
  ```
  Si `site_url` vide (ressource non déployée) → `[Titre](repo_url)`.
  Si plusieurs résultats, demander d'abord lequel est concerné (même logique de résolution que `create-variant`). Puis appeler l'outil `question` avec `{ "questions": [{ "question": "La ressource [X] couvre déjà [Y]. Que veux-tu faire ?", "header": "Inspiration", "options": [{"label": "S'en inspirer", "description": "Utiliser comme référence"}, {"label": "Créer une variante", "description": "Cloner la ressource existante et la modifier"}, {"label": "Créer différent", "description": "Continuer avec autre chose"}] }] }` :
   - **S'en inspirer** : proposer un lien vers le site existant comme référence, puis continuer le questionnaire (étape 5)
   - **Créer une variante** : déléguer au skill `create-variant` avec le titre de la ressource parente. Le questionnaire s'arrête ici — le skill crée le clone et la fiche JSONL.
   - **Créer différent** : continuer le questionnaire (étape 5)
- Si pas trouvé après les deux passages : continuer (étape 5)

**5. Quel serait le titre de ta ressource ?**

**6. Veux-tu des contenus interactifs ?**
Appeler l'outil `question` avec `{ "questions": [{ "question": "Veux-tu des contenus interactifs ?", "header": "Interactif", "multiple": true, "options": [{"label": "YouTube", "description": "Vidéo intégrée"}, {"label": "Quiz", "description": "Questions à choix"}, {"label": "Stepper", "description": "Pas à pas"}, {"label": "Playground", "description": "HTML/CSS/JS interactif"}, {"label": "SQL Playground", "description": "Éditeur SQL interactif"}, {"label": "Solution cachée", "description": "Section dépliable inline"}, {"label": "Solution séparée", "description": "Page dédiée"}, {"label": "Exercices inline", "description": "Blocs dépliants"}] }] }`. NE JAMAIS demander de taper au clavier.

### Étape 2 : Génération du squelette minimal

**IMPORTANT** : Ne PAS générer de contenu beyond le squelette. Ne pas rédiger d'objectifs, de notions ni de texte explicatif. Laisser des placeholders `[À compléter]`. Le rôle du squelette est de poser la structure et les artefacts, pas de rédiger.

En fonction des réponses, générer un fichier markdown `README.md` avec :

**1. Structure de base** :
```markdown
---
title: "{{TITLE}}"
description: "{{DESCRIPTION}}"
show_toc: true
---

# {{TITLE}}

> #### 🎯 Objectifs
> - [À compléter]

## Notions abordées

- [À compléter]

## Contenu

[À compléter]
```

**2. Artefacts préconfigurés** (ajoutés après la section « Contenu » selon les choix question 6) :

**YouTube** — thumbnail auto-convertie en iframe :
```markdown
[![Titre de la vidéo](https://img.youtube.com/vi/VIDEO_ID/0.jpg)](https://youtu.be/VIDEO_ID)
```

**Quiz** — include du thème :
```markdown
{% capture quiz_data %}
[{"question": "Question exemple ?", "options": ["Réponse A", "Réponse B", "Réponse C", "Réponse D"], "correct": 0}]
{% endcapture %}
{% include quiz.html data=quiz_data %}
```

**Stepper** — plugin `jekyll-stepper` (4 backticks) :
```markdown
````stepper
# Étape 1 : [À compléter]
[Contenu de l'étape 1]

# Étape 2 : [À compléter]
[Contenu de l'étape 2]
````
```

**Playground** — include du thème :
```markdown
{% capture my_html %}
<h1>[À compléter]</h1>
{% endcapture %}

{% include playground.html id="demo" initial_html=my_html %}
```

**SQL Playground** — include du thème (éditeur SQL + sql.js WASM) :
```markdown
{% capture db_schema %}
CREATE TABLE exemple (
  id INTEGER PRIMARY KEY,
  nom TEXT NOT NULL
);

INSERT INTO exemple VALUES (1, 'Alice');
{% endcapture %}

{% capture initial_query %}
SELECT * FROM exemple;
{% endcapture %}

{% include sql-playground.html
  id="sql-demo"
  schema=db_schema
  query=initial_query
%}
```

**Solution cachée** — section dépliable inline (documentation thème) :
```markdown
<details markdown="1">
<summary>Voir la solution</summary>

[À compléter]

</details>
```

**Solution séparée** — fichier `solution.md` séparé :
- Créer `solution.md` avec le front matter prérempli :
```yaml
---
title: "{{TITLE}} - Solution"
description: "{{DESCRIPTION}}"
show_toc: true
parent: "{{TITLE}}"
---
```
Plus `[À compléter]` dans le corps.

**Exercices** — blockquote Jekyll native (pas `xtext arrow`) :
```markdown
> #### 🎯 À toi de jouer !
> [Consigne de l'exercice à compléter]
```

### Étape 3 : Enregistrement dans le brouillon

Ajouter une ligne dans `REGISTRY.md` sous la section « En cours » :

```markdown
- [{{TITRE}}](../repos/{{DOMAIN}}-{{SLUG}}/) ({{DOMAIN}})
```

Incrémenter le compteur dans l'en-tête « En cours (N) ».

**Ne pas toucher à `registry.jsonl`** — ce fichier n'est mis à jour qu'au moment de la publication.

### Étape 4 : Créer le dépôt local

1. Créer le dossier `repos/{{DOMAIN}}-{{SLUG}}/`
2. Copier les templates Jekyll depuis `templates/`
3. Remplacer les placeholders dans `_config.yml` :
   - `{{TITLE}}` → titre de la ressource
   - `{{DESCRIPTION}}` → description (ou valeur par défaut)
4. Écrire le fichier `README.md` avec le contenu généré
5. Créer le dossier `images/`

---

## Mode From scratch

Quand l'utilisateur choisit de créer une ressource sans questionnaire (fournit son propre markdown).

### Étape 1 : Demander le markdown

Demander à l'utilisateur de fournir son contenu markdown.

### Étape 2 : Recherche de contenu similaire

Extraire le titre du markdown fourni (premier `# Titre` ou front matter `title`).

Découper le sujet en mots individuels (ex : « CSS Variables » → `css`, `variables`).

- **Passage 1** : un appel à l'outil `grep` par mot, union des résultats (dédoublonner par slug) :
  ```
  grep(pattern="css", path=".", include="registry.jsonl")
  grep(pattern="variables", path=".", include="registry.jsonl")
  ```
  Extraire les champs `title`, `site_url` et `repo_url` de chaque ligne retournée.
- **Passage 2** (si passage 1 donne 0 résultat) : réessayer avec synonymes, traductions françaises ou termes élargis
- Si trouvé : afficher les ressources avec des liens cliquables :
  ```
  Ressources similaires trouvées :
  - [Titre](site_url)
  ```
  Si `site_url` vide (ressource non déployée) → `[Titre](repo_url)`.
  Si plusieurs résultats, demander d'abord lequel est concerné. Puis appeler l'outil `question` avec `{ "questions": [{ "question": "La ressource [X] couvre déjà [Y]. Que veux-tu faire ?", "header": "Inspiration", "options": [{"label": "S'en inspirer", "description": "Utiliser comme référence"}, {"label": "Créer une variante", "description": "Cloner la ressource existante et la modifier"}, {"label": "Créer différent", "description": "Continuer avec mon propre contenu"}] }] }` :
    - **S'en inspirer** : proposer un lien vers le site existant comme référence, puis passer à l'étape 3
    - **Créer une variante** : déléguer au skill `create-variant` avec le titre de la ressource parente. Le workflow s'arrête ici.
    - **Créer différent** : passer à l'étape 3
- Si pas trouvé après les deux passages : passer directement à l'étape 3

### Étape 3 : Domaine

Demander le domaine :
```json
{
  "questions": [{
    "question": "Quel est le domaine ?",
    "header": "Domaine",
    "options": [
      {"label": "dev-web", "description": "Développement web"},
      {"label": "data", "description": "Data / IA"},
      {"label": "infra", "description": "Infrastructure / DevOps"},
      {"label": "design", "description": "Design / UI-UX"}
    ]
  }]
}
```

### Étape 4 : Créer le dépôt local

1. Slugifier le titre → `{SLUG}`
2. Créer le dossier `repos/{{DOMAIN}}-{{SLUG}}/`
3. Copier les templates Jekyll depuis `templates/`
4. Remplacer les placeholders dans `_config.yml`
5. Écrire le fichier `README.md` avec le markdown fourni par l'utilisateur
6. Créer le dossier `images/`

### Étape 5 : Enregistrement dans le brouillon

Ajouter une ligne dans `REGISTRY.md` sous la section « En cours » :

```markdown
- [{{TITRE}}](../repos/{{DOMAIN}}-{{SLUG}}/) ({{DOMAIN}})
```

Incrémenter le compteur dans l'en-tête « En cours (N) ».

**Ne pas toucher à `registry.jsonl`** — ce fichier n'est mis à jour qu'au moment de la publication.

---

## Mode Conversion

Quand l'utilisateur fournit un fichier JSON de quest à convertir.

### Étape 1 : Vérifications préliminaires

1. **Vérifier si la quest a déjà été convertie** :
   ```
   grep(pattern="\"id\":{{quest_id}}", path=".", include="registry.jsonl")
   ```
   - Si trouvé : informer l'utilisateur ("Cette quest a déjà été convertie : {URL}") et appeler l'outil `question` avec `{ "questions": [{ "question": "Cette quest est déjà convertie. Continuer (écraser) ?", "header": "Doublon", "options": [{"label": "Continuer", "description": "Écraser la conversion"}, {"label": "Annuler", "description": "Ne rien faire"}] }] }`

2. **Demander le domaine** (si non renseigné) en appelant l'outil `question` avec `{ "questions": [{ "question": "Quel est le domaine ?", "header": "Domaine", "options": [{"label": "dev-web", "description": "Développement web"}, {"label": "data", "description": "Data / IA"}, {"label": "infra", "description": "Infrastructure / DevOps"}, {"label": "design", "description": "Design / UI-UX"}] }] }`. NE JAMAIS demander de taper au clavier.

### Étape 2 : Parse du JSON

Lire le fichier `quests/todo/quest-{id}.json` et extraire :
- `quest_id` → identifiant unique
- `revision.title` → titre de la quest
- `revision.description` → description
- `pages[]` → tableau des pages (content, solution)

### Étape 3 : Slugification du titre

- Supprimer les emojis (ex: 👩‍🏫, ✅, 🤓)
- Minuscules
- Remplacer les espaces par des tirets
- Supprimer les caractères spéciaux (ponctuation, accents)
- Ex: "👩‍🏫 Installer et utiliser Visual Studio Code" → `installer-et-utiliser-visual-studio-code`

### Étape 4 : Vérifier l'unicité du slug

Si `repos/{{DOMAIN}}-{{SLUG}}/` existe déjà, ajouter le `quest_id` : `{{DOMAIN}}-{{SLUG}}-{{quest_id}}`

### Étape 5 : Génération des fichiers

1. **Dossier** : `repos/{{DOMAIN}}-{{SLUG}}/` + `repos/{{DOMAIN}}-{{SLUG}}/images/`

2. **README.md** → page principale (page avec chapter_type="content")
   - Ajouter un lien vers la page solution si elle existe en bas de page

3. **solution.md** → page solution (si chapter_type="solution" existe)
   - Ajouter " - Solution" au titre de la page dans le front matter
   - Ajouter `parent: titre-de-la-page-principale` dans le front matter

4. **Templates Jekyll** :
   - `_config.yml` → copier depuis `templates/_config.yml` et remplacer les placeholders
   - `Gemfile` → copier depuis `templates/Gemfile`
   - `.gitignore` → copier depuis `templates/.gitignore`
   - `.github/workflows/jekyll.yml` → copier depuis `templates/jekyll.yml`

### Étape 6 : Conversion du markdown

Appliquer les mappings de syntaxe (voir section "Règles de conversion" ci-dessous).

### Étape 7 : Téléchargement des images

1. Extraire toutes les URLs d'images du markdown (`![...](...)`)
2. Télécharger chaque image dans `repos/{{DOMAIN}}-{{SLUG}}/images/`
3. Renommer les fichiers avec un nom descriptif
4. Réécrire les URLs dans le markdown : `![](images/nom-fichier.ext)`
5. Ne pas mettre de `alt` text pour les images (souvent décoratives)

### Étape 8 : Enregistrement dans le brouillon

Ajouter une ligne dans `REGISTRY.md` sous la section « En cours » :

```markdown
- [{{TITRE_SANS_EMOJIS}}](../repos/{{DOMAIN}}-{{SLUG}}/) ({{DOMAIN}})
```

Incrémenter le compteur dans l'en-tête « En cours (N) ».

**Ne pas toucher à `registry.jsonl`** — ce fichier n'est mis à jour qu'au moment de la publication.

---

## Annulation d'un brouillon

Quand l'utilisateur veut annuler une ressource en cours de création :

### Étape 1 : Retirer la ligne de REGISTRY.md

1. Ouvrir `REGISTRY.md`
2. Supprimer la ligne correspondante dans la section « En cours »
3. Décrémenter le compteur dans l'en-tête « En cours (N) »

### Étape 2 : Supprimer le dépôt local (optionnel)

Demander à l'utilisateur s'il veut supprimer le dossier local :

```bash
rm -rf repos/{{DOMAIN}}-{{SLUG}}
```

### Étape 3 : Confirmation

Informer l'utilisateur que le brouillon a été annulé. Aucun fichier dans `registry.jsonl` n'a été modifié.

---

## Règles de conversion

### Mapping des syntaxes

| Syntaxe source | Équivalent Jekyll |
|---------------|-------------------|
| ` ```alert-info\n...\n``` ` | Contenu avec `{:.alert-info}` après chaque paragraphe |
| ` ```alert-warning\n...\n``` ` | Contenu avec `{:.alert-warning}` après chaque paragraphe |
| ` ```alert-error\n...\n``` ` | `{:.alert-warning}` (error → warning) |
| ` ```alert-success\n...\n``` ` | `{:.alert-info}` (success → info) |
| ` ```xtext story\n...\n``` ` | Bloc quote `> ` avec chaque ligne préfixée |
| ` ```xtext arrow\n...\n``` ` | Bloc quote `> ` avec chaque ligne préfixée |
| ` ```xtext intro\n...\n``` ` | Texte brut (paragraphe standard) |
| ` ```js live\n...\n``` ` | Playground interactif (`playground.html`) |
| ` ```sql live\n...\n``` ` | SQL Playground (`sql-playground.html`) |
| ` ```quests\n2114\n``` ` | Lien vers le site de la quest (utiliser registry.jsonl) |
| ` ```ressource\n...\n``` ` | Bloc avec `{:.alert-info}` + contenu formaté |
| ` ````stepper\n...\n```` ` ou ` ````stepper nonLinear\n...\n```` ` | Pass-through (plugin `jekyll-stepper`) |
| ` ````solution\n...\n```` ` | `<details>` ou fichier `solution.md` séparé |
| ` ```youtube\nURL\n``` ` | Lien markdown vers la vidéo |
| ` ````tabs\n...\n```` ` | Dépliants `<details markdown="1">` avec `<summary>` |
| ` ```mermaid\n...\n``` ` | Image générée via mermaid.ink |

### Remplacement de termes

| Terme source | Terme cible |
|--------------|-------------|
| `quête` | `ressource` |
| `À la fin de cette quête tu sauras` | `Objectifs` |

### Titres

- Vérifier la hiérarchie logique des titres Markdown
- Supprimer le titre "Sommaire" si présent (Jekyll génère automatiquement la TOC)

### Listes

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

### Balisage spécial

Avant :
```
:def[HTML]{value="HyperText Markup Language"}
```

Après :
```markdown
HTML (HyperText Markup Language)
```

### alert-info / alert-warning

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

### xtext story

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

### xtext arrow

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

Ajuster le niveau d'intertitre en cohérence avec la hiérarchie de la page.

### xtext intro

Avant :
````
```xtext intro
Dans cette ressource, tu apprendras...
```
````

Après :
```markdown
Dans cette ressource, tu apprendras...
```

Le bloc `xtext intro` est un texte d'introduction — paragraphe standard, pas de bloc quote.

### js live (→ Playground interactif)

Les blocs `js live` contiennent du code HTML/CSS/JS séparé par des marqueurs `!--- nom-fichier.ext`.

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

**Variante inline** (un seul type de code) :
````markdown
{% include playground.html
  id="demo"
  initial_html="<h1>Hello</h1>"
%}
````

**Règles** :
- L'`id` doit être unique par page
- Si uniquement HTML : syntaxe inline
- Si HTML + CSS + JS : utiliser les 3 captures
- `default_tab` selon le focus du contenu :
  - `html` (défaut), `css` ou `js`
  - Si le bloc contient uniquement du JS → `default_tab="js"`

### sql live (→ SQL Playground interactif)

Les blocs `sql live` contiennent du code SQL pour un éditeur interactif.

**Avant** :
````
```sql live
SELECT * FROM wizard WHERE lastname = 'Potter';
```
````

**Après** :
````markdown
{% capture initial_query %}
SELECT * FROM wizard WHERE lastname = 'Potter';
{% endcapture %}

{% include sql-playground.html
  id="sql-demo"
  query=initial_query
%}
````

**Variante avec schema** (si le bloc contient CREATE TABLE + INSERT) :

**Avant** :
````
```sql live
CREATE TABLE wizard (
  id INTEGER PRIMARY KEY,
  firstname TEXT
);

INSERT INTO wizard VALUES (1, 'Harry');

SELECT * FROM wizard;
```
````

**Après** :
````markdown
{% capture db_schema %}
CREATE TABLE wizard (
  id INTEGER PRIMARY KEY,
  firstname TEXT
);

INSERT INTO wizard VALUES (1, 'Harry');
{% endcapture %}

{% capture initial_query %}
SELECT * FROM wizard;
{% endcapture %}

{% include sql-playground.html
  id="sql-demo"
  schema=db_schema
  query=initial_query
%}
````

**Règles** :
- L'`id` doit être unique par page
- Si le bloc contient uniquement des requêtes SELECT → pas de `schema`
- Si le bloc contient CREATE TABLE/INSERT → extraire dans `schema`
- Le contenu reste fidèle au JSON source

**Compatibilité MySQL → SQLite** :
Le SQL playground utilise sql.js (SQLite). Appliquer les transformations suivantes au `schema` :

| MySQL | SQLite |
|-------|--------|
| `INT NOT NULL AUTO_INCREMENT` | `INTEGER PRIMARY KEY` |
| `VARCHAR(n)` | `TEXT COLLATE NOCASE` |
| `BOOLEAN DEFAULT 0` | `INTEGER DEFAULT 0` |
| `DATE DEFAULT NULL` | `TEXT DEFAULT NULL` |
| `\'` (échappement apostrophe) | `''` (double apostrophe) |
| `'0'`, `'1'` (entiers en string) | `0`, `1` (entiers natifs) |

Ajouter `COLLATE NOCASE` aux colonnes TEXT pour rendre les comparaisons insensibles à la casse (comportement MySQL par défaut).

Ne pas modifier les requêtes SELECT.

### quests (liens vers autres quests)

Avant :
````
```quests
2114
```
````

Après :
```markdown
[Titre de la quest cible](URL_DEPLOYEMENT)
```

Utiliser l'URL de déploiement depuis `registry.jsonl` :
```
grep(pattern="\"id\":{{quest_id}}", path=".", include="registry.jsonl")
```
Extraire le champ `site_url` de la ligne JSON retournée.
Si la quest cible n'est pas dans le registre, avertir l'utilisateur et lui demander quoi faire.

### ressource

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

[https://example.com](https://example.com)
{:.alert-info}
```

### solution (deux cas)

**Cas 1 — Solution de challenge en bas de page** :
Le bloc `solution` contient la réponse au challenge final → fichier `solution.md` séparé.

Avant (dans le README.md) :
````
````solution
# Solution du challenge
Contenu de la solution...
````
````

Après (dans README.md) :
```markdown
---

[Voir la solution](solution){:.alert-info}
```

**Cas 2 — Solution inline** :
Si la solution apparaît au milieu du texte → bloc `<details>` :

```markdown
<details markdown="1">
<summary>Voir la solution</summary>

Contenu de la solution...

</details>
```

### Quiz

Le JSON source peut contenir des quiz au format :
```quiz
# Question ?
[x] A
[] B
[] C
[] D
```

Convertir en :
````markdown
{% capture quiz_data %}
[{"question": "Question ?", "options": ["A", "B", "C", "D"], "correct": 0}]
{% endcapture %}
{% include quiz.html data=quiz_data %}
````

### youtube

Avant :
````
```youtube
https://www.youtube.com/watch?v=VIDEO_ID
```
````

Après :
```markdown
[Voir la vidéo YouTube](https://www.youtube.com/watch?v=VIDEO_ID)
```

Le thème auto-détecte les URLs YouTube et les remplace par des iframes embed.

### tabs (→ dépliants)

Les blocs `tabs` contiennent des onglets séparés par des marqueurs `!--- nom-onglet`.

Avant :
````
````tabs
!--- Ubuntu
Tape simplement cette commande
```sh
sudo apt install gh
```

!--- Mac OS
Tape simplement cette commande
```sh
brew install gh
```
````
````

Après :
```markdown
<details markdown="1">
<summary>Ubuntu</summary>

Tape simplement cette commande
```sh
sudo apt install gh
```

</details>

<details markdown="1">
<summary>Mac OS</summary>

Tape simplement cette commande
```sh
brew install gh
```

</details>
```

Règles :
- Séparer par les marqueurs `!--- `
- Le nom après `!---` devient le `<summary>`
- Garder une ligne vide avant et après le `<summary>`

### mermaid (→ image)

1. Encoder le code mermaid en base64
2. Télécharger l'image depuis `https://mermaid.ink/img/{base64}`
3. Sauvegarder dans `images/` avec un nom descriptif
4. Remplacer le bloc par une image markdown

Commande :
```bash
echo 'CODE_MERMAID' | base64 | tr -d '\n' | xargs -I {} curl -sL -o images/nom-image.png "https://mermaid.ink/img/{}"
```

### stepper

Les blocs ````````stepper` sont en **pass-through** — le plugin `jekyll-stepper` gère le rendu.

Format attendu (4 backticks) :
`````markdown
````stepper
# Titre de l'étape 1
Contenu markdown de l'étape 1.

# Titre de l'étape 2
Contenu markdown de l'étape 2.
````
`````

Les blocs steppers utilisent 4 backticks pour permettre l'imbrication de blocs de code à 3 backticks.

### Liens vers des ressources externes

- Récupérer le titre de la page web pour le titre de la ressource
- Formater : `[Titre de la ressource](URL)`

---

## Front Matter des pages

### Page principale
```yaml
---
title: {{TITLE}}
description: {{DESCRIPTION}}
show_toc: true
---
```

### Page solution
```yaml
---
title: {{TITLE}} - Solution
description: {{DESCRIPTION}}
show_toc: true
parent: titre-de-la-page-principale
---
```

---

## Templates

Les templates se trouvent dans `templates/` :
- `_config.yml` : Configuration Jekyll avec le thème simplonline
- `Gemfile` : Dépendances Ruby (jekyll, webrick, jekyll-remote-theme, jekyll-readme-index, jekyll-stepper)
- `.gitignore` : Fichiers à ignorer (_site/, .jekyll-cache/, etc.)
- `jekyll.yml` : Workflow GitHub Actions pour le déploiement

---

## Structure d'un dépôt généré

```
repos/{{DOMAIN}}-{{SLUG}}/
├── README.md                  # Page principale (content)
├── solution.md                # Page solution (si existe)
├── images/                    # Images téléchargées
├── _config.yml                # Config Jekyll
├── Gemfile                    # Dépendances
├── .gitignore                 # Fichiers à ignorer
└── .github/
    └── workflows/
        └── jekyll.yml         # Workflow GitHub Actions
```

---

## Artefacts du thème

Ces fonctionnalités sont gérées automatiquement par le thème Jekyll Simplonline — aucune conversion nécessaire.

### YouTube (auto-détection JS)
Le module `YouTubeEmbedder` détecte automatiquement les URLs YouTube et les remplace par des iframes embed (16:9, `youtube-nocookie.com`).

### Stepper (plugin Jekyll)
Le plugin `jekyll-stepper` convertit les blocs stepper en composants accordion avec navigation Previous/Next.

### Playground — Console (auto-détection)
Le playground affiche automatiquement la sortie console du code exécuté ainsi que les erreurs JavaScript.

### Quiz (include Jekyll)
Les quiz sont convertis en utilisant `{% include quiz.html %}`.

### SQL Playground (include Jekyll)
Le SQL Playground affiche un éditeur SQL interactif avec exécution dans le navigateur via sql.js (SQLite compilé en WebAssembly). Aucun serveur requis. sql.js est lazy-loadé uniquement quand un `sql-playground` est présent (~700 KB WASM).

---

## Commandes Jekyll pour test local

### Installation des dépendances
```bash
cd repos/{{DOMAIN}}-{{SLUG}}
bundle install
```

### Lancer le serveur local
```bash
bundle exec jekyll serve --livereload
```

Le site sera disponible sur `http://localhost:4000`

---

## Limitations

- Les emojis dans les titres sont supprimés lors du slugifield
- Les images externes sont téléchargées dans le dossier `/images` et les URLs réécrites
- Les liens vers d'autres quests utilisent le format `quest-{id}` si le slug n'est pas connu
- `alert-error` et `alert-success` ne sont pas supportés — convertis en `alert-warning` et `alert-info`
