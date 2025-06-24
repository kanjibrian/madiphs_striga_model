import os

EXCLUDE = {'__pycache__'}
EXCLUDE_EXTENSIONS = {'.pyc', '.pyo', '.pyd'}

def tree(dir_path, prefix=""):
    # Get all entries except excluded
    entries = [e for e in os.listdir(dir_path) if e not in EXCLUDE and not e.endswith(tuple(EXCLUDE_EXTENSIONS))]

    # Separate folders and files
    folders = sorted([e for e in entries if os.path.isdir(os.path.join(dir_path, e))])
    files = sorted([e for e in entries if not os.path.isdir(os.path.join(dir_path, e))])

    # Combine folders first, then files
    sorted_entries = folders + files
    pointers = ['├── '] * (len(sorted_entries) - 1) + ['└── ']

    lines = []
    for pointer, entry in zip(pointers, sorted_entries):
        path = os.path.join(dir_path, entry)
        display_name = entry + '/' if os.path.isdir(path) else entry
        lines.append(f"{prefix}{pointer}{display_name}")
        if os.path.isdir(path):
            extension = "│   " if pointer == '├── ' else "    "
            lines.extend(tree(path, prefix=prefix + extension))
    return lines

if __name__ == "__main__":
    root_dir = "."  # or specify your root path
    root_name = os.path.basename(os.path.abspath(root_dir)) + '/'
    tree_lines = [root_name] + tree(root_dir)

    for line in tree_lines:
        print(line)

    with open("project_file_structure/project_file_structure.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(tree_lines))

    # print("\nFile structure saved to 'project_file_structure.txt'")
