from utils import prompt_path, load_text, write_text, classify_quote

OPEN_QUOTE = '\u201c'
CLOSE_QUOTE = '\u201d'

def extract_quotes(text):
    quotes = []
    for i, ch in enumerate(text):
        if ch == '"':
            quotes.append((i, classify_quote(text, i)))
    return quotes

def pair_quotes(quotes):
    stack = []
    replacements = {}
    for pos, role in quotes:
        if role == 'open':
            stack.append((pos, role))
        elif role == 'close':
            if stack:
                opener_pos, _ = stack.pop()
                replacements[opener_pos] = OPEN_QUOTE
                replacements[pos] = CLOSE_QUOTE
        else:
            if stack:
                opener_pos, _ = stack.pop()
                replacements[opener_pos] = OPEN_QUOTE
                replacements[pos] = CLOSE_QUOTE
            else:
                stack.append((pos, 'open'))
    return replacements

def apply_replacements(text, replacements):
    result = []
    for i, ch in enumerate(text):
        result.append(replacements.get(i, ch))
    return ''.join(result)

def run(path):
    text = load_text(path)
    quotes = extract_quotes(text)
    replacements = pair_quotes(quotes)
    result = apply_replacements(text, replacements)
    write_text(path, result)
    replaced = len(replacements)
    skipped = len(quotes) - replaced
    print(f"Replaced {replaced} quote marks ({replaced // 2} pairs).")
    if skipped:
        print(f"Warning: {skipped} quote mark(s) were not replaced (orphaned).")

def main():
    run(prompt_path())

if __name__ == '__main__':
    main()
