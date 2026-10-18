import sys
from dataclasses import dataclass

INPUT_PATH = 'input.txt'
OPEN_PRECEDERS = set(' \t\n\r\x00([{,;:')
CLOSE_FOLLOWERS = set(' \t\n\r\x00)]}.,;:!?-')

@dataclass
class QuoteMark:
    pos: int
    line: int
    col: int
    char_index: int
    role: str
    raw_context: str

@dataclass
class Pair:
    opener: QuoteMark
    closer: QuoteMark

def load_text(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def compute_line_col(text, pos):
    line = text.count('\n', 0, pos) + 1
    last_nl = text.rfind('\n', 0, pos)
    col = pos - last_nl
    return line, col


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

def extract_quotes(text, word_positions=None):
    quotes = []
    for i, ch in enumerate(text):
        if ch != '"':
            continue
        role = classify_quote(text, i)
        line, col = compute_line_col(text, i)
        start = max(0, i - 30)
        end = min(len(text), i + 30)
        ctx = text[start:end].replace('\n', '↵')
        quotes.append(QuoteMark(pos=i, line=line, col=col, char_index=i, role=role, raw_context=ctx,))
    return quotes

def pair_quotes(quotes):
    stack = []
    pairs = []
    orphaned = []
    for q in quotes:
        if q.role == 'open':
            stack.append(q)
        elif q.role == 'close':
            if stack:
                pairs.append(Pair(opener=stack.pop(), closer=q))
            else:
                orphaned.append(q)
        else:
            if stack:
                pairs.append(Pair(opener=stack.pop(), closer=q))
            else:
                q.role = 'open'
                stack.append(q)
    orphaned.extend(stack)
    orphaned.sort(key=lambda q: q.pos)
    return pairs, orphaned

def report(pairs, orphaned, total_quotes):
    print(f"Total quote marks  : {total_quotes}")
    print(f"Matched pairs      : {len(pairs)}")
    print(f"Orphaned quotes    : {len(orphaned)}")
    if not orphaned:
        print("No orphaned quotes found.")
        return
    print("Orphaned quotes:")
    for q in orphaned:
        print(f"  Line {q.line:>5}, Col {q.col:>4}  [{q.role:>9}]  ...{q.raw_context}...")

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else INPUT_PATH
    text = load_text(path)
    quotes = extract_quotes(text)
    pairs, orphaned = pair_quotes(quotes)
    report(pairs, orphaned, len(quotes))

if __name__=='__main__':
    main()

