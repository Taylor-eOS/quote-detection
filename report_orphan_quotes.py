import sys
from dataclasses import dataclass, field

MAX_PAIR_WORD_SPAN = 20
OPEN_PRECEDERS = set(' \t\n\r\x00([{,;:')
CLOSE_FOLLOWERS = set(' \t\n\r\x00)]}.,;:!?-')

@dataclass
class QuoteMark:
    pos: int
    line: int
    col: int
    char_index: int
    role: str  # 'open', 'close', 'ambiguous'
    word_index: int
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

def word_index_at(words_positions, char_pos):
    lo, hi = 0, len(words_positions) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        start, end = words_positions[mid]
        if char_pos < start:
            hi = mid - 1
        elif char_pos > end:
            lo = mid + 1
        else:
            return mid
    return lo

def build_word_positions(text):
    positions = []
    i = 0
    n = len(text)
    while i < n:
        while i < n and text[i] in ' \t\n\r':
            i += 1
        if i >= n:
            break
        start = i
        while i < n and text[i] not in ' \t\n\r':
            i += 1
        positions.append((start, i))
    return positions

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

def extract_quotes(text, word_positions):
    quotes = []
    for i, ch in enumerate(text):
        if ch != '"':
            continue
        role = classify_quote(text, i)
        line, col = compute_line_col(text, i)
        wi = word_index_at(word_positions, i) if word_positions else 0
        start = max(0, i - 30)
        end = min(len(text), i + 30)
        ctx = text[start:end].replace('\n', '↵')
        quotes.append(QuoteMark(
            pos=i,
            line=line,
            col=col,
            char_index=i,
            role=role,
            word_index=wi,
            raw_context=ctx,
        ))
    return quotes

def score_pair(opener, closer):
    span = closer.word_index - opener.word_index
    if span < 0:
        return float('inf')
    if span <= MAX_PAIR_WORD_SPAN:
        return span
    return span * 10

def pair_quotes(quotes):
    openers = []
    closers = []
    ambiguous = []
    for q in quotes:
        if q.role == 'open':
            openers.append(q)
        elif q.role == 'close':
            closers.append(q)
        else:
            ambiguous.append(q)
    for q in ambiguous:
        if openers and openers[-1].word_index <= q.word_index:
            q.role = 'close'
            closers.append(q)
        else:
            q.role = 'open'
            openers.append(q)
    openers.sort(key=lambda q: q.pos)
    closers.sort(key=lambda q: q.pos)
    used_openers = set()
    used_closers = set()
    pairs = []
    for ci, closer in enumerate(closers):
        best_opener = None
        best_score = float('inf')
        for oi, opener in enumerate(openers):
            if oi in used_openers:
                continue
            if opener.pos >= closer.pos:
                break
            s = score_pair(opener, closer)
            if s < best_score:
                best_score = s
                best_opener = oi
        if best_opener is not None and best_score < float('inf'):
            used_openers.add(best_opener)
            used_closers.add(ci)
            pairs.append(Pair(opener=openers[best_opener], closer=closer))
    orphaned = []
    for oi, opener in enumerate(openers):
        if oi not in used_openers:
            orphaned.append(opener)
    for ci, closer in enumerate(closers):
        if ci not in used_closers:
            orphaned.append(closer)

    orphaned.sort(key=lambda q: q.pos)
    return pairs, orphaned

def report(pairs, orphaned, total_quotes):
    print(f"Total quote marks  : {total_quotes}")
    print(f"Matched pairs      : {len(pairs)}")
    print(f"Orphaned quotes    : {len(orphaned)}")
    print()
    if not orphaned:
        print("No orphaned quotes found.")
        return
    print("Orphaned quotes:")
    print("-" * 70)
    for q in orphaned:
        print(f"  Line {q.line:>5}, Col {q.col:>4}  [{q.role:>9}]  ...{q.raw_context}...")
    print("-" * 70)

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else 'input.txt'
    text = load_text(path)
    word_positions = build_word_positions(text)
    quotes = extract_quotes(text, word_positions)
    pairs, orphaned = pair_quotes(quotes)
    report(pairs, orphaned, len(quotes))

main()

