#!/usr/bin/env python3
"""Vérifie la fidélité d'une conversion quest JSON → README.md Jekyll.

Usage: python3 scripts/verify-conversion.py <quest_id>

Compare les titres, paragraphes, blocs spéciaux et images
entre le JSON source et le README.md généré.
"""

import json
import re
import sys
import os
from pathlib import Path
from difflib import SequenceMatcher

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent


def extract_titles(content):
    """Extrait les titres markdown en ignorant les titres dans les blocs spéciaux."""
    titles = []
    in_block = False
    block_type = None
    for line in content.split('\n'):
        stripped = line.strip()
        # Détecter l'ouverture de blocs spéciaux (``` au début de ligne)
        if re.match(r'^```,', stripped) or re.match(r'^```\w', stripped):
            if not in_block:
                in_block = True
                block_type = stripped
                continue
        if in_block and stripped == '```':
            in_block = False
            block_type = None
            continue
        if not in_block and re.match(r'^#{1,6}\s', stripped):
            titles.append(stripped)
    return titles


def normalize_title(t):
    """Supprime les emojis, le markdown et normalise pour comparaison floue."""
    # Supprimer le markup markdown
    t = re.sub(r'^[#\s]+', '', t)
    t = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', t)
    t = re.sub(r'`([^`]+)`', r'\1', t)
    # Supprimer les emojis (tout caractère hors ASCII imprimable latin)
    t = re.sub(r'[^\x00-\x7F]+', '', t)
    # Supprimer les tirets, points, etc. en début/fin
    t = re.sub(r'^[\s\-:•]+', '', t)
    t = re.sub(r'[\s\-:•]+$', '', t)
    return t.strip().lower()


def fuzzy_match(t1, t2):
    """Vérifie si deux titres se correspondent approximativement."""
    if t1 == t2:
        return True
    # Un titre est un sous-chaîne de l'autre
    if t1 in t2 or t2 in t1:
        return True
    # Similarité par SequenceMatcher (seuil 0.6)
    ratio = SequenceMatcher(None, t1, t2).ratio()
    return ratio >= 0.6


def count_paragraphs(content):
    """Compte les paragraphes de texte brut (exclut structures et métadonnées)."""
    paragraphs = 0
    in_code = False
    in_block = False
    in_frontmatter = False
    line_count = 0
    for line in content.split('\n'):
        stripped = line.strip()
        line_count += 1
        # Front matter YAML
        if line_count == 1 and stripped == '---':
            in_frontmatter = True
            continue
        if in_frontmatter and stripped == '---':
            in_frontmatter = False
            continue
        if in_frontmatter:
            continue
        # Blocs de code
        if re.match(r'^```', stripped):
            in_code = not in_code
            in_block = in_code
            continue
        if in_code:
            continue
        # Ignorer lignes vides, séparateurs, titres
        if stripped == '' or stripped == '---':
            continue
        if re.match(r'^#{1,6}\s', stripped):
            continue
        # Ignorer blockquotes, listes, tableaux, images
        if stripped.startswith('>'):
            continue
        if re.match(r'^[-*]\s', stripped):
            continue
        if re.match(r'^\|', stripped):
            continue
        if re.match(r'^!\[', stripped):
            continue
        # Ignorer les lignes Jekyll ({% %}, {:.})
        if re.match(r'^\{[%{]', stripped):
            continue
        # Ignorer HTML inline (<details>, <summary>, etc.)
        if re.match(r'^<', stripped):
            continue
        paragraphs += 1
    return paragraphs


def extract_json_blocks(json_content):
    """Extrait les blocs spéciaux et leur contenu du JSON."""
    blocks = []
    pattern = r'```(\w+(?:\s+\w+)?)\n(.*?)```'
    for match in re.finditer(pattern, json_content, re.DOTALL):
        block_type = match.group(1).strip()
        block_content = match.group(2).strip()
        blocks.append({'type': block_type, 'content': block_content})
    return blocks


def check_special_blocks(json_content):
    """Vérifie la présence de blocs spéciaux dans le JSON."""
    blocks = {
        'quiz': bool(re.search(r'```\s*quiz', json_content)),
        'youtube': bool(re.search(r'```\s*youtube', json_content)),
        'tabs': bool(re.search(r'````\s*tabs', json_content)),
        'stepper': bool(re.search(r'````\s*stepper', json_content)),
        'solution': bool(re.search(r'````\s*solution', json_content)),
        'quests': bool(re.search(r'```\s*quests', json_content)),
        'ressource': bool(re.search(r'```\s*ressource', json_content)),
        'js_live': bool(re.search(r'```\s*js\s+live', json_content)),
        'sql_live': bool(re.search(r'```\s*sql\s+live', json_content)),
        'alert_info': bool(re.search(r'```\s*alert[\s-]info', json_content)),
        'alert_warning': bool(re.search(r'```\s*alert[\s-]warning', json_content)),
        'alert_error': bool(re.search(r'```\s*alert[\s-]error', json_content)),
        'xtext_story': bool(re.search(r'```\s*xtext\s+story', json_content)),
        'xtext_arrow': bool(re.search(r'```\s*xtext\s+arrow', json_content)),
        'xtext_intro': bool(re.search(r'```\s*xtext\s+intro', json_content)),
    }
    return blocks


def check_blocks_in_readme(blocks, json_content, readme_content):
    """Vérifie que les blocs spéciaux ont été correctement convertis."""
    conversions = {}

    if blocks['quiz']:
        conversions['quiz'] = 'quiz_data' in readme_content or 'quiz.html' in readme_content

    if blocks['youtube']:
        # Vérifier qu'au moins une URL YouTube est présente
        yt_urls = re.findall(r'```\s*youtube\n(.*?)```', json_content, re.DOTALL)
        conversions['youtube'] = 'youtube.com' in readme_content or 'youtu.be' in readme_content

    if blocks['tabs']:
        conversions['tabs'] = '<details markdown=' in readme_content

    if blocks['stepper']:
        conversions['stepper'] = 'stepper' in readme_content

    if blocks['solution']:
        conversions['solution'] = '<details' in readme_content or 'solution.md' in readme_content

    if blocks['js_live']:
        conversions['js_live'] = 'playground.html' in readme_content

    if blocks['sql_live']:
        conversions['sql_live'] = 'sql-playground.html' in readme_content

    if blocks['alert_info']:
        conversions['alert_info'] = '{:.alert-info}' in readme_content

    if blocks['alert_warning']:
        conversions['alert_warning'] = '{:.alert-warning}' in readme_content

    if blocks['alert_error']:
        # alert-error → alert-warning en Jekyll
        conversions['alert_error'] = '{:.alert-warning}' in readme_content

    if blocks['ressource']:
        conversions['ressource'] = '{:.alert-info}' in readme_content

    if blocks['xtext_story']:
        # Vérifier que le contenu du bloc est dans un blockquote
        xtext_blocks = re.findall(r'```\s*xtext\s+story\n(.*?)```', json_content, re.DOTALL)
        if xtext_blocks:
            first_line = xtext_blocks[0].strip().split('\n')[0].strip()
            conversions['xtext_story'] = f'> {first_line}' in readme_content or '> ' in readme_content
        else:
            conversions['xtext_story'] = '> ' in readme_content

    if blocks['xtext_arrow']:
        xtext_blocks = re.findall(r'```\s*xtext\s+arrow\n(.*?)```', json_content, re.DOTALL)
        if xtext_blocks:
            first_line = xtext_blocks[0].strip().split('\n')[0].strip()
            conversions['xtext_arrow'] = f'> {first_line}' in readme_content or '> ' in readme_content
        else:
            conversions['xtext_arrow'] = '> ' in readme_content

    if blocks['xtext_intro']:
        # xtext intro → paragraphe normal (pas de bloc quote)
        conversions['xtext_intro'] = True  # Pas de vérification spécifique

    return conversions


def check_images(json_content, readme_content, readme_path):
    """Vérifie que les images du JSON sont dans le README."""
    json_images = re.findall(r'!\[.*?\]\((https?://[^)]+)\)', json_content)
    readme_images = re.findall(r'!\[.*?\]\(([^)]+)\)', readme_content)
    readme_dir = os.path.dirname(readme_path)
    local_images = []
    for img in readme_images:
        if img.startswith('images/'):
            local_path = os.path.join(readme_dir, img)
            local_images.append(os.path.exists(local_path))
    return {
        'json_count': len(json_images),
        'readme_count': len(readme_images),
        'local_count': sum(local_images),
    }


def strip_non_ascii(s):
    """Supprime les caractères non-ASCII (emojis, zero-width joiners, etc.)."""
    return re.sub(r'[^\x00-\x7F]+', '', s).strip()


def normalize_for_match(s):
    """Normalise une chaîne pour comparaison (minusculule, sans accents, sans emojis)."""
    import unicodedata
    # Décomposer les caractères Unicode et garder seulement les base letters
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    # Supprimer non-ASCII
    s = re.sub(r'[^\x00-\x7F]+', '', s)
    return s.strip().lower()


def find_readme_for_quest(quest_id, data):
    """Trouve le README.md correspondant à une quest."""
    title = data['revision']['title']
    title_norm = normalize_for_match(title)
    repos_dir = PROJECT_ROOT / 'repos'
    for d in repos_dir.iterdir():
        if d.is_dir() and not d.name.startswith('.'):
            config = d / '_config.yml'
            if config.exists():
                with open(config) as f:
                    config_content = f.read()
                # Chercher la ligne title: dans le config
                for line in config_content.split('\n'):
                    if line.strip().startswith('title:'):
                        config_title = line.split(':', 1)[1].strip().strip('"').strip("'")
                        config_title_norm = normalize_for_match(config_title)
                        if title_norm == config_title_norm or title_norm in config_title_norm or config_title_norm in title_norm:
                            return d / 'README.md'
    return None


def verify(quest_id):
    """Vérifie la fidélité d'une conversion."""
    json_path = PROJECT_ROOT / 'quests' / 'todo' / f'quest-{quest_id}.json'
    if not json_path.exists():
        print(f"❌ Fichier JSON non trouvé: {json_path}")
        return False

    with open(json_path) as f:
        data = json.load(f)

    # Combiner le contenu de TOUTES les pages
    json_content = '\n\n'.join(page['content'] for page in data['pages'])
    title = data['revision']['title']

    readme_path = find_readme_for_quest(quest_id, data)
    if not readme_path or not readme_path.exists():
        print(f"❌ README.md non trouvé pour quest {quest_id}")
        return False

    with open(readme_path) as f:
        readme_content = f.read()

    print(f"🔍 Vérification de fidélité pour quest-{quest_id}: {title}")
    print(f"   JSON: {json_path}")
    print(f"   README: {readme_path}")
    print(f"   Pages JSON: {len(data['pages'])}\n")

    errors = 0
    warnings = 0

    # 1. Comparer les titres (correspondance floue)
    json_titles = extract_titles(json_content)
    readme_titles = extract_titles(readme_content)

    json_titles_norm = [normalize_title(t) for t in json_titles]
    readme_titles_norm = [normalize_title(t) for t in readme_titles]

    # Pour chaque titre JSON, chercher une correspondance dans le README
    missing_titles = []
    for i, jt in enumerate(json_titles_norm):
        found = False
        for rt in readme_titles_norm:
            if fuzzy_match(jt, rt):
                found = True
                break
        if not found:
            missing_titles.append(json_titles[i])

    # Pour chaque titre README, vérifier qu'il correspond à un titre JSON
    invented_titles = []
    for i, rt in enumerate(readme_titles_norm):
        found = False
        for jt in json_titles_norm:
            if fuzzy_match(jt, rt):
                found = True
                break
        if not found:
            invented_titles.append(readme_titles[i])

    print(f"📖 Titres: {len(readme_titles)}/{len(json_titles)}")
    if missing_titles:
        print(f"   ❌ Manquants:")
        for m in missing_titles:
            print(f"      - {m}")
        errors += len(missing_titles)
    if invented_titles:
        print(f"   ⚠️ Inventés (absents du JSON):")
        for i in invented_titles:
            print(f"      - {i}")
        warnings += len(invented_titles)
    if not missing_titles and not invented_titles:
        print(f"   ✅ Tous les titres correspondent")

    # 2. Comparer les paragraphes
    json_paras = count_paragraphs(json_content)
    readme_paras = count_paragraphs(readme_content)
    ratio = readme_paras / json_paras if json_paras > 0 else 0
    status = "✅" if ratio >= 0.8 else "❌"
    print(f"\n📄 Paragraphes: {readme_paras}/{json_paras} ({ratio:.0%}) {status}")
    if ratio < 0.8:
        errors += 1

    # 3. Vérifier les blocs spéciaux
    blocks = check_special_blocks(json_content)
    block_results = check_blocks_in_readme(blocks, json_content, readme_content)
    active_blocks = [k for k, v in blocks.items() if v]
    converted_blocks = [k for k, v in block_results.items() if v]
    unconverted = [k for k in active_blocks if k not in converted_blocks]

    if active_blocks:
        print(f"\n🧩 Blocs spéciaux: {len(converted_blocks)}/{len(active_blocks)}")
        if unconverted:
            print(f"   ❌ Non convertis:")
            for b in unconverted:
                print(f"      - {b}")
            errors += len(unconverted)
        else:
            print(f"   ✅ Tous les blocs convertis")
    else:
        print(f"\n🧩 Blocs spéciaux: aucun détecté")

    # 4. Vérifier les images
    images = check_images(json_content, readme_content, str(readme_path))
    if images['json_count'] > 0:
        img_status = "✅" if images['local_count'] == images['json_count'] else "❌"
        print(f"\n🖼️  Images: {images['local_count']}/{images['json_count']} {img_status}")
        if images['local_count'] < images['json_count']:
            errors += 1
    else:
        print(f"\n🖼️  Images: aucune détectée dans le JSON")

    # Résumé
    print(f"\n{'='*50}")
    if errors == 0 and warnings == 0:
        print(f"✅ Conversion fidèle")
    elif errors == 0:
        print(f"✅ Conversion fidèle ({warnings} avertissement(s))")
    else:
        print(f"❌ {errors} erreur(s) détectée(s), {warnings} avertissement(s)")
    print(f"{'='*50}")

    return errors == 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/verify-conversion.py <quest_id>")
        sys.exit(1)
    quest_id = int(sys.argv[1])
    success = verify(quest_id)
    sys.exit(0 if success else 1)
