---
name: create-variant
description: "Crée une variante d'une ressource existante. Clone le dépôt parent, crée une fiche JSONL avec `variant_of`, et laisse le formateur éditer le clone."
---

# Skill: Créer une variante

Crée une variante d'une ressource existante en clonant le dépôt parent et en créant une fiche dans le registre.

## Quand utiliser ce skill

- L'utilisateur demande de créer une variante d'une ressource existante
- Déclencheur : `Créer une variante de {titre}`

## Prérequis

- La ressource parente doit exister dans `registry.jsonl`
- Le dépôt distant du parent doit être accessible sur GitHub (`git@github.com:simplonco/{slug-parent}.git`)

## Flux de travail

### Étape 1 : Résolution du parent

1. Chercher le titre dans `registry.jsonl` :
   ```
   grep(pattern="\"title\":\"{titre}\"", path=".", include="registry.jsonl")
   ```
2. Si correspondance exacte → continuer
3. Si plusieurs résultats partiels → appeler l'outil `question` avec `{ "questions": [{ "question": "Plusieurs ressources correspondent. Laquelle ?", "header": "Parent", "options": [{"label": "Titre 1", "description": "…"}, {"label": "Titre 2", "description": "…"}] }] }`
4. Si aucun résultat → avertir et arrêter

Retenir le `slug` du parent résolu.

### Étape 2 : Choix du suffixe

Appeler l'outil `question` avec `{ "questions": [{ "question": "Quel suffixe pour la variante ? (ex: pokedex, 2026-09-03)", "header": "Suffixe", "options": [] }] }` — l'utilisateur saisit librement.

Slugifier le suffixe (minuscules, tirets, pas de caractères spéciaux).

Vérifier l'unicité : si `{slug-parent}-{suffixe}` existe déjà dans `registry.jsonl` → proposer un autre suffixe.

Nouveau slug : `{slug-parent}-{suffixe}`

### Étape 3 : Cloner le dépôt parent

```bash
git clone git@github.com:simplonco/{slug-parent}.git repos/{nouveau-slug}
rm -rf repos/{nouveau-slug}/.git
```

⚠️ Le `rm -rf .git` est indispensable : sans lui, le clone conserve l'origin du parent et `jekyll-deploy` risquerait de pousser la variante dans le dépôt parent.

**Repli** : si le clone distant échoue, chercher dans `repos/archives/{slug-parent}` puis `repos/{slug-parent}`. Si introuvable → avertir l'utilisateur et arrêter.

### Étape 4 : Mettre à jour le titre

Dans `repos/{nouveau-slug}/_config.yml`, remplacer le titre par celui de la variante.

### Étape 5 : Ajouter la ligne dans le brouillon

Ajouter une ligne dans `REGISTRY.md` sous la section « En cours » :

```markdown
- [{titre-parent} - {suffixe}](../repos/{nouveau-slug}/) ({domain})
```

Incrémenter le compteur dans l'en-tête « En cours (N) ».

**Ne pas toucher à `registry.jsonl`** — ce fichier n'est mis à jour qu'au moment de la publication.

### Étape 6 : Confirmation

Résumer les actions effectuées :
- Parent : `{titre-parent}` (`{slug-parent}`)
- Variante créée : `{titre-parent} - {suffixe}` (`{nouveau-slug}`)
- Ligne « En cours » ajoutée dans `REGISTRY.md` (variante de `{slug-parent}`)
- Le dépôt local est prêt à être édité dans `repos/{nouveau-slug}/`

Proposer le test local :
```bash
cd repos/{nouveau-slug}
bundle install
bundle exec jekyll serve --livereload
→ http://localhost:4000
```

Rappeler que le déploiement et l'archivage sont des commandes séparées :
- `Déploie {nouveau-slug}`
- `Archive {nouveau-slug}`

---

## Erreurs courantes

| Erreur | Cause | Solution |
|--------|-------|----------|
| Parent introuvable | Titre inexistant dans le registre | Vérifier le titre exact dans le registre |
| Slug déjà utilisé | Collision de slug | Choisir un autre suffixe |
| Clone échoue | Dépôt distant inexistant ou inaccessible | Vérifier `gh repo view simplonco/{slug-parent}` |
| `rm -rf .git` oublié | Origin du parent encore présente | Supprimer `repos/{nouveau-slug}/.git` et réinitialiser |

---

## Commandes utiles

### Vérifier un dépôt parent
```bash
gh repo view simplonco/{slug-parent}
```

### Vérifier les variantes existantes
```
grep(pattern="variant_of", path=".", include="registry.jsonl")
```

### Lister les fiches d'un domaine
```bash
cat registry/{domaine}.md
```
