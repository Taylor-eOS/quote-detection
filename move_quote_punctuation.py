from utils import prompt_path, load_lines, write_lines, is_abbreviation, TERMINATORS, TRAILING_CLOSERS

FLIP_TRAILING_COMMA = True
SHOW_CHANGES = True
QUOTE_CHARS = {'"', '\u201c', '\u201d'}
OPEN_CURLY = '\u201c'
CLOSE_CURLY = '\u201d'
lines = []
changes = []
bad_lines = []
candidate_count = 0
flipped_count = 0

def find_pairs(line):
    marks = [(i, ch) for i, ch in enumerate(line) if ch in QUOTE_CHARS]
    if len(marks) % 2:
        return None
    pairs = []
    for k in range(0, len(marks), 2):
        open_idx, open_ch = marks[k]
        close_idx, close_ch = marks[k + 1]
        if open_ch == CLOSE_CURLY or close_ch == OPEN_CURLY:
            return None
        pairs.append((open_idx, close_idx))
    return pairs

def has_internal_break(body):
    for j in range(len(body) - 1):
        if body[j] not in TERMINATORS or not body[j + 1].isspace():
            continue
        if body[j] == '.' and is_abbreviation(body[:j]):
            continue
        return True
    return False

def prefix_kind(prefix):
    stripped = prefix.rstrip()
    if not stripped:
        return 'standalone'
    core = stripped.rstrip(TRAILING_CLOSERS)
    if core and core[-1] in TERMINATORS:
        return 'standalone'
    last = stripped[-1]
    if last in ',:':
        return 'lead'
    if last.isalnum():
        return 'inline'
    return 'unknown'

def is_candidate(line, open_idx, close_idx):
    inner = line[open_idx + 1:close_idx]
    return len(inner) >= 2 and inner[-1] in '.,'

def should_flip(line, open_idx, close_idx):
    inner = line[open_idx + 1:close_idx]
    final = inner[-1]
    body = inner[:-1]
    after = line[close_idx + 1:]
    if after and not after[0].isspace():
        return False
    if not body.strip():
        return False
    if body.rstrip()[-1] in TERMINATORS:
        return False
    if final == ',':
        return FLIP_TRAILING_COMMA
    if is_abbreviation(body):
        return False
    if has_internal_break(body):
        return False
    if after.strip()[:1].islower():
        return False
    return prefix_kind(line[:open_idx]) in ('lead', 'inline')

def fix_line(index):
    global candidate_count, flipped_count
    line = lines[index]
    pairs = find_pairs(line)
    if pairs is None:
        bad_lines.append(index + 1)
        return
    chars = list(line)
    for open_idx, close_idx in pairs:
        if not is_candidate(line, open_idx, close_idx):
            continue
        candidate_count += 1
        if not should_flip(line, open_idx, close_idx):
            continue
        chars[close_idx - 1], chars[close_idx] = chars[close_idx], chars[close_idx - 1]
        flipped_count += 1
        start = max(0, open_idx - 30)
        end = min(len(line), close_idx + 15)
        changes.append(f"{index + 1}: {line[start:end]}\n{' ' * len(str(index + 1))}  {''.join(chars[start:end])}")
    lines[index] = ''.join(chars)

def report():
    if SHOW_CHANGES:
        for change in changes:
            print(change)
            print()
    print(f"Candidates with punctuation before the closing quote: {candidate_count}")
    print(f"Moved outside: {flipped_count}")
    print(f"Left unchanged: {candidate_count - flipped_count}")
    if bad_lines:
        shown = ', '.join(str(n) for n in bad_lines[:20])
        more = '' if len(bad_lines) <= 20 else f" and {len(bad_lines) - 20} more"
        print(f"Skipped {len(bad_lines)} line(s) with unbalanced or misordered quotes: {shown}{more}")

def run(path):
    global candidate_count, flipped_count
    candidate_count = 0
    flipped_count = 0
    changes.clear()
    bad_lines.clear()
    lines[:] = load_lines(path)
    for index in range(len(lines)):
        fix_line(index)
    write_lines(path, lines)
    report()

def main():
    run(prompt_path())

if __name__ == '__main__':
    main()
