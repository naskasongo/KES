import os
import re


def clean_sql_file():
    print("🧹 NETTOYAGE DU FICHIER SQL POUR POSTGRESQL")
    print("=" * 50)

    input_file = r"D:\Projects\school\script.sql"
    output_file = r"D:\Projects\school\cleaned_script.sql"

    # Vérifier que le fichier existe
    if not os.path.exists(input_file):
        print(f"❌ Fichier introuvable: {input_file}")
        return False

    try:
        # Lire le fichier avec encodage approprié
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✅ Fichier lu avec UTF-8: {len(content)} caractères")

    except UnicodeDecodeError:
        try:
            # Essayer latin-1 si UTF-8 échoue
            with open(input_file, 'r', encoding='latin-1') as f:
                content = f.read()
            print(f"✅ Fichier lu avec Latin-1: {len(content)} caractères")
        except Exception as e:
            print(f"❌ Erreur de lecture: {e}")
            return False

    # Remplacements pour PostgreSQL
    replacements = [
        (r'integer\s+not null\s+primary key autoincrement', 'SERIAL PRIMARY KEY'),
        (r'autoincrement', ''),
        (r'bool', 'BOOLEAN'),
        (r'datetime', 'TIMESTAMP'),
        (r'decimal', 'NUMERIC(10, 2)'),
        (r'text\s+not null', 'TEXT NOT NULL'),
        (r'varchar\((\d+)\)', 'VARCHAR(\\1)'),
        (r'references (\w+)\s+deferrable initially deferred', 'REFERENCES \\1'),
        (r'check \("[^"]*"\)', ''),  # Supprimer les checks
        (r'unsigned', ''),
        (r'"', ''),
        (r'CREATE TABLE sqlite_sequence.*?;', ''),
        (r'CREATE TABLE sqlite_master.*?;', ''),
        (r'CREATE UNIQUE INDEX.*?;', ''),
        (r'CREATE INDEX.*?;', ''),
    ]

    cleaned_content = content
    for pattern, replacement in replacements:
        cleaned_content = re.sub(pattern, replacement, cleaned_content, flags=re.IGNORECASE | re.DOTALL)

    # Écrire le fichier nettoyé
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)

    print(f"✅ Fichier nettoyé: {output_file}")
    print(f"📊 Taille: {len(cleaned_content)} caractères")

    # Aperçu du contenu
    lines = cleaned_content.split('\n')
    print("\n📋 APERÇU DES PREMIÈRES LIGNES:")
    for i, line in enumerate(lines[:10]):
        if line.strip():
            print(f"   {i + 1}: {line.strip()}")

    return True


if __name__ == "__main__":
    clean_sql_file()