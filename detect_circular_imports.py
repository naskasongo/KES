import os
import sys
from pathlib import Path
import ast


def get_module_name(file_path, base_dir):
    """Convertit un chemin absolu en nom de module Python"""
    try:
        rel_path = file_path.relative_to(base_dir)
    except ValueError:
        return ""  # Retourne vide si le chemin n'est pas dans le projet

    parts = rel_path.parts

    # ⚠️ Protection contre les tuples vides
    if not parts:
        return ""

    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts = parts[:-1] + (parts[-1].replace(".py", ""),)

    return ".".join(parts)


class ImportVisitor(ast.NodeVisitor):
    def __init__(self):
        self.imports = set()

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name.split('.')[0])
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.add(node.module.split('.')[0])
        self.generic_visit(node)


def analyze_imports(file_path, base_dir, visited=None):
    """Analyse les imports d’un fichier et retourne les modules importés"""
    visited = visited or set()
    if file_path in visited:
        return []
    visited.add(file_path)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))
    except Exception as e:
        print(f"⚠️ Échec de lecture {file_path}: {e}")
        return []

    visitor = ImportVisitor()
    visitor.visit(tree)

    base_module = get_module_name(file_path.parent, base_dir)
    resolved_imports = []

    for imp in visitor.imports:
        if imp == base_module.split('.')[0]:
            continue  # Ignore auto-import via structure de package

        potential_paths = [
            file_path.parent / f"{imp}.py",
            file_path.parent / imp / "__init__.py"
        ]

        imported_file = None
        for p in potential_paths:
            if p.exists():
                imported_file = p
                break

        if imported_file:
            resolved_imports.append(imported_file)

    return resolved_imports


def find_circular_imports(start_file, base_dir, path=None):
    """Trouve les cycles d'imports à partir d'un fichier donné"""
    path = path or []
    if start_file in path:
        return [path + [start_file]]

    cycles = []
    imports = analyze_imports(start_file, base_dir, visited=set(path))

    for imp in imports:
        sub_cycles = find_circular_imports(imp, base_dir, path + [start_file])
        if sub_cycles:
            cycles.extend(sub_cycles)

    return cycles


def main(project_root):
    project_root = Path(project_root).resolve()
    print(f"\n🔍 Recherche des imports cycliques depuis la racine : {project_root}\n")

    python_files = list(project_root.rglob("*.py"))

    for file in python_files:
        cycles = find_circular_imports(file, project_root)

        if cycles:
            print(f"🔁 Cycle trouvé à partir de : {file.relative_to(project_root)}")
            for cycle in cycles:
                cycle_rel = [str(f.relative_to(project_root)) for f in cycle]
                print("   ➡ ".join(cycle_rel) + "\n")


if __name__ == "__main__":
    # Remplacez par le chemin de votre projet
    PROJECT_ROOT = r"D:\Projects\wantashi"

    main(PROJECT_ROOT)
