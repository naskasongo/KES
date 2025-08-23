import json
import chardet


def fix_json_encoding(input_file, output_file):
    print(f"🔧 Correction de l'encodage de {input_file}...")

    # Détecter l'encodage
    with open(input_file, 'rb') as f:
        raw_data = f.read()
        encoding = chardet.detect(raw_data)['encoding']
        print(f"Encodage détecté: {encoding}")

        try:
            # Essayer de décoder
            if encoding:
                content = raw_data.decode(encoding)
            else:
                content = raw_data.decode('utf-8', errors='ignore')
        except UnicodeDecodeError:
            content = raw_data.decode('latin-1', errors='ignore')

    # Nettoyer le contenu JSON
    try:
        # Essayer de parser pour vérifier que c'est du JSON valide
        data = json.loads(content)

        # Réencoder proprement en UTF-8
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ Fichier corrigé: {output_file}")
        return True

    except json.JSONDecodeError as e:
        print(f"❌ JSON invalide: {e}")
        # Essayer de réparer manuellement
        return repair_json_manually(content, output_file)


def repair_json_manually(content, output_file):
    """Réparer manuellement le JSON corrompu"""
    print("🔧 Tentative de réparation manuelle...")

    # Nettoyer les caractères problématiques
    cleaned_content = content.replace('\x00', '').replace('\xff', '')

    # Essayer de parser comme lignes JSON individuelles
    lines = cleaned_content.strip().split('\n')
    valid_objects = []

    for line in lines:
        line = line.strip()
        if line and line not in ['[', ']', ',']:
            try:
                obj = json.loads(line)
                valid_objects.append(obj)
            except json.JSONDecodeError:
                # Ignorer les lignes invalides
                continue

    if valid_objects:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(valid_objects, f, indent=2, ensure_ascii=False)
        print(f"✅ Réparation partielle: {output_file}")
        return True
    else:
        print("❌ Impossible de réparer le fichier JSON")
        return False


if __name__ == "__main__":
    fix_json_encoding('full_backup.json', 'fixed_backup.json')