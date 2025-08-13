#!/bin/sh


# === CONFIGURATION ===
PROJECT_PATH="home/kfs/Downloads/wantashi/wantashi"           # Chemin de ton projet
GITHUB_URL="https://github.com/naskasongo/wantashi.git"  # 🔁 Remplace cette URL par celle de ton propre repo GitHub
BRANCH_NAME="main"

# === SCRIPT ===
cd "$PROJECT_PATH" || { echo "Chemin invalide : $PROJECT_PATH"; exit 1; }

# Initialiser Git si ce n’est pas encore fait
if [ ! -d ".git" ]; then
    echo "Initialisation du dépôt Git..."
    git init
fi

# Créer un fichier .gitignore si nécessaire
if [ ! -f ".gitignore" ]; then
    echo "Création du fichier .gitignore..."
    cat <<EOL > .gitignore
# Django et Python
__pycache__/
*.py[cod]
*.sqlite3
*.log
*.env
.env

# Environnements virtuels
venv/
ENV/
env/

# IDE
.vscode/
.idea/

# Fichiers de médias/statics
media/
staticfiles/
EOL
fi

# Ajouter tous les fichiers
echo "Ajout des fichiers au dépôt Git..."
git add .

# Commit (force si déjà existant)
echo "Création d'un commit..."
git commit -m "Push automatique du projet complet Wantashi" || echo "Aucun changement à committer."

# Ajouter remote s’il n’existe pas encore
if ! git remote | grep -q origin; then
    echo "Ajout du dépôt distant..."
    git remote add origin "$GITHUB_URL"
fi

# Définir la branche principale
git branch -M "$BRANCH_NAME"

# Push vers GitHub
echo "Envoi du projet sur GitHub..."
git push -u origin "$BRANCH_NAME"

echo "✅ Projet envoyé sur GitHub avec succès !"

