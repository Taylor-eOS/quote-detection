import os
from utils import prompt_folder
import replace_em_dash
import replace_curly_quotes
import move_quote_punctuation

EXTENSIONS = {'.txt', '.md'}
RECURSIVE = True
STEPS = [replace_em_dash, replace_curly_quotes, move_quote_punctuation]

def find_files(folder):
    found = []
    for root, dirs, names in os.walk(folder):
        dirs.sort()
        for name in sorted(names):
            if os.path.splitext(name)[1].lower() in EXTENSIONS:
                found.append(os.path.join(root, name))
        if not RECURSIVE:
            break
    return found

def process_file(path):
    for step in STEPS:
        print(f"--- {step.__name__} ---")
        step.run(path)

def main():
    folder = prompt_folder()
    files = find_files(folder)
    if not files:
        print(f"No files with extensions {', '.join(sorted(EXTENSIONS))} found in {folder}")
        return
    failed = []
    for path in files:
        print(f"=== {path} ===")
        try:
            process_file(path)
        except (UnicodeDecodeError, OSError) as error:
            print(f"Skipped: {error}")
            failed.append(path)
    print(f"Processed {len(files) - len(failed)} of {len(files)} file(s).")
    for path in failed:
        print(f"Failed: {path}")

if __name__ == '__main__':
    main()
