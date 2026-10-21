from dataclasses import dataclass
from utils import prompt_path, load_text, classify_quote

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

def compute_line_col(text, pos):
    line = text.count('\n', 0, pos) + 1
    last_nl = text.rfind('\n', 0, pos)
    col = pos - last_nl
    return line, col

def extract_quotes(text, word_positions=None):
    quotes = []
    for i, ch in enumerate(text):
        if ch != '"':
            continue
        role = classify_quote(text, i)
        line, col = compute_line_col(text, i)
        start = max(0, i - 30)
        end = min(len(text), i + 30)
        ctx = text[start:end].replace('\r', '').replace('\n', '↵')
        quotes.append(QuoteMark(pos=i, line=line, col=col, char_index=i, role=role, raw_context=ctx))
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
    path = prompt_path()
    text = load_text(path)
    quotes = extract_quotes(text)
    pairs, orphaned = pair_quotes(quotes)
    report(pairs, orphaned, len(quotes))

if __name__ == '__main__':
    main()
