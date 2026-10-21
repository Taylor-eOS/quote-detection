import os

OPEN_PRECEDERS = set(' \t\n\r\x00([{,;:')
CLOSE_FOLLOWERS = set(' \t\n\r\x00)]}.,;:!?-')
TERMINATORS = '.!?'
TRAILING_CLOSERS = '"\u201d\u2019\')]}'
ABBREVIATIONS = {
    'mr', 'mrs', 'ms', 'dr', 'prof', 'sr', 'jr', 'st', 'mt', 'vs', 'etc',
    'inc', 'ltd', 'co', 'no', 'fig', 'approx', 'gen', 'col', 'capt', 'lt',
    'sgt', 'rev', 'hon', 'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug',
    'sep', 'sept', 'oct', 'nov', 'dec',
}

def prompt_path():
    while True:
        raw = input("Path to the file: ").strip().strip('\'"')
        path = os.path.abspath(os.path.expanduser(raw))
        if os.path.isfile(path):
            return path
        print(f"File not found: {path}")

def load_text(path):
    with open(path, 'r', encoding='utf-8', newline='') as f:
        return f.read()

def write_text(path, text):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(text)

def load_lines(path):
    return load_text(path).split('\n')

def write_lines(path, lines):
    write_text(path, '\n'.join(lines))

def classify_quote(text, pos):
    n = len(text)
    prev_char = text[pos - 1] if pos > 0 else '\x00'
    next_char = text[pos + 1] if pos + 1 < n else '\x00'
    can_open = prev_char in OPEN_PRECEDERS
    can_close = next_char in CLOSE_FOLLOWERS
    if can_open and not can_close:
        return 'open'
    if can_close and not can_open:
        return 'close'
    return 'ambiguous'

def trailing_word(text):
    start = len(text)
    while start > 0 and (text[start - 1].isalpha() or text[start - 1] == '.'):
        start -= 1
    return text[start:]

def is_abbreviation(before):
    word = trailing_word(before)
    if '.' in word:
        return True
    if word.lower() in ABBREVIATIONS:
        return True
    return len(word) == 1 and word.isupper()
