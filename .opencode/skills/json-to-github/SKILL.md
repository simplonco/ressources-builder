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
│   └── archives/                      # JSON traités
├── repos/                             # Dépôts générés (sortie)
└── AGENTS.md
```

## Flux de travail

### 1. Conversion d'une quest

Quand l'utilisateur demande de convertir une quest (ex: "Convertis quest-2114.json") :

1. **Lire le fichier JSON** depuis `quests/todo/`
2. **Extraire les métadonnées** :
   - `quest_id` → identifiant unique
   - `revision.title` → titre de la quest
   - `pages[]` → tableau des pages (content, solution)
3. **Slugifier le titre** pour le nom du dépôt :
   - Supprimer les emojis (ex: 👩‍🏫, ✅, 🤓)
   - Minuscules
   - Remplacer les espaces par des tirets
   - Supprimer les caractères spéciaux (ponctuation, accents)
   - Ex: "👩‍🏫 Installer et utiliser Visual Studio Code" → `installer-et-utiliser-visual-studio-code`
4. **Vérifier l'unicité du slug** : si `repos/{slug}/` existe déjà, ajouter le `quest_id` : `{slug}-{quest_id}`
5. **Créer le dossier** `repos/{slug}/` et le sous-dossier `repos/{slug}/images/`
6. **Générer les fichiers Jekyll** :
   - `README.md` → page principale (page avec chapter_type="content")
   - `solution.md` → page solution (si chapter_type="solution" existe)
   - `_config.yml` → copier depuis `templates/_config.yml` et remplacer les placeholders :
     - `{{TITLE}}` → `revision.title`
     - `{{DESCRIPTION}}` → `revision.description` (ou valeur par défaut si `null`)
   - `Gemfile` → copier depuis `templates/Gemfile`
   - `.gitignore` → copier depuis `templates/.gitignore`
7. **Télécharger les images** :
   - Extraire toutes les URLs d'images du markdown (`![...](...)`)
   - Télécharger chaque image dans `repos/{slug}/images/`
   - Renommer les fichiers avec un nom descriptif (pas d'URL longue)
   - Réécrire les URLs dans le markdown : `![alt](images/nom-fichier.ext)`
8. **Git init et premier commit** : initialiser un dépôt Git dans le répertoire et effectuer un premier commit d'initialisation
9. **Tester localement** (effectué manuellement par l'utilisateur) : `bundle exec jekyll serve --livereload`
10. **Archiver** : lorsque l'utilisateur confirme que les tests, reviews et ajustement sont terminés :
    - si nécessaire, effectuer un commit pour sauvegarder les modifications
    - déplacer le JSON vers `quests/archives/`
    - demander si le dossier doit être poussé sur GitHub. Si oui, passer à l'étape 2 : Push vers GitHub

### 2. Push vers GitHub

Quand l'utilisateur demande de pousser un dépôt (ex: "Push le dépôt X vers GitHub") :

1. **Vérifier** que le dossier existe dans `repos/`
2. **Créer le dépôt** via `MCP_DOCKER_create_repository`
3. **Lire et push tous les fichiers** via `MCP_DOCKER_push_files`
4. **Retourner l'URL** du dépôt créé

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
[Voir la ressource "Installer et utiliser Visual Studio Code"](https://github.com/simplonco/installer-et-utiliser-visual-studio-code/)
```

Note : nécessite de connaître le slug de la quest cible. Si non disponible, utiliser le format `quest-{id}`.

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

## Templates

Les templates se trouvent dans `templates/` :
- `_config.yml` : Configuration Jekyll avec le thème simplonline
- `Gemfile` : Dépendances Ruby (github-pages, webrick)
- `.gitignore` : Fichiers à ignorer (_site/, .jekyll-cache/, etc.)

## Structure d'un dépôt généré

```
repos/{slug}/
├── README.md        # Page principale (content)
├── solution.md      # Page solution (si existe)
├── images/          # Images téléchargées
├── _config.yml      # Config Jekyll
├── Gemfile          # Dépendances
└── .gitignore       # Fichiers à ignorer
```

## Commandes Jekyll pour test local

```bash
cd repos/{slug}
bundle install
bundle exec jekyll serve --livereload
```

Le site sera disponible sur `http://localhost:4000`

## Limitations

- Les emojis dans les titres sont supprimés lors du slugifield
- Les images externes (storage.googleapis.com) sont téléchargées dans le dossier `/images` et les URLs réécrites
- Les liens vers d'autres quests utilisent le format `quest-{id}` si le slug n'est pas connu
