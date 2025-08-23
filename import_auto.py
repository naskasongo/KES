import re


def extract_insert_statements():
    print("📦 EXTRACTION DES DONNÉES SEULEMENT")
    print("=" * 50)

    input_file = r"D:\Projects\school\script.sql"
    output_file = r"D:\Projects\school\data_only.sql"

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extraire seulement les INSERT statements
    insert_pattern = r'INSERT INTO .*?;'
    insert_statements = re.findall(insert_pattern, content, re.IGNORECASE | re.DOTALL)

    # Nettoyer les INSERT (supprimer les quotes)
    cleaned_inserts = []
    for insert in insert_statements:
        cleaned = insert.replace('"', '').replace('`', '')
        cleaned_inserts.append(cleaned)

    # Écrire dans le fichier de sortie
    with open(output_file, 'w', encoding='utf-8') as f:
        for insert in cleaned_inserts:
            f.write(insert + '\n')

    print(f"✅ {len(cleaned_inserts)} instructions INSERT extraites")
    print(f"💾 Sauvegardé dans: {output_file}")

    # Aperçu    print("\n📋 APERÇU DES INSERT:")
    for i, insert in enumerate(cleaned_inserts[:5]):
        print(f"   {i + 1}: {insert[:100]}...")

    return True


if __name__ == "__main__":
    extract_insert_statements()