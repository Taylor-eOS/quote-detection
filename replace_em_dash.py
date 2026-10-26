from utils import prompt_path, load_lines, write_lines, is_abbreviation, TERMINATORS, TRAILING_CLOSERS

SHOW_CHANGES = True
DASH = '\u2014'
REPLACEMENT = '; '
PAREN_LIMIT = 40
RIGHT_OK_STARTS = '"\u201c\u2018\'([{'
OPENERS = '\u201c\u2018([{'
lines = []
changes = []
counts = {'converted': 0, 'parenthesized': 0, 'skipped': 0, 'multi': 0}

def find_sentence_spans(line):
    spans = []
    start = 0
    i = 0
    n = len(line)
    while i < n:
        if line[i] in TERMINATORS:
            j = i + 1
            while j < n and line[j] in TRAILING_CLOSERS:
                j += 1
            at_boundary = j == n or line[j].isspace()
            if at_boundary and not (line[i] == '.' and is_abbreviation(line[start:i])):
                spans.append((start, j))
                start = j
                i = j
                continue
        i += 1
    if start < n:
        spans.append((start, n))
    return spans

def can_convert(left, right):
    if not left or not right:
        return False
    if not (left[-1].isalnum() or left[-1] in TRAILING_CLOSERS):
        return False
    if not (right[0].isalnum() or right[0] in RIGHT_OK_STARTS):
        return False
    if right[0] in '"\'' and (len(right) < 2 or right[1].isspace()):
        return False
    return any(ch.isalnum() for ch in right)

def convert_pair(sentence):
    first = sentence.index(DASH)
    second = sentence.index(DASH, first + 1)
    left = sentence[:first].rstrip()
    inner = sentence[first + 1:second].strip()
    right = sentence[second + 1:].lstrip()
    if not any(ch.isalnum() for ch in left):
        return None
    if not any(ch.isalnum() for ch in inner):
        return None
    if len(inner) >= PAREN_LIMIT:
        return None
    gap = '' if not right or right[0] in TRAILING_CLOSERS + TERMINATORS + ',;:' else ' '
    return left + ' (' + inner + ')' + gap + right, (first, len(left) + 2)

def convert_sentence(sentence):
    count = sentence.count(DASH)
    if count == 0:
        return sentence, None
    if count > 1:
        if count == 2:
            result = convert_pair(sentence)
            if result is not None:
                counts['parenthesized'] += 1
                return result
        counts['multi'] += 1
        return sentence, None
    idx = sentence.index(DASH)
    left = sentence[:idx].rstrip()
    right = sentence[idx + 1:].lstrip()
    if not can_convert(left.lstrip(), right):
        counts['skipped'] += 1
        return sentence, None
    counts['converted'] += 1
    return left + REPLACEMENT + right, (idx, len(left))

def snippet(text, center):
    return text[max(0, center - 30):center + 30].strip()

def fix_line(index):
    line = lines[index]
    if DASH not in line:
        return
    parts = []
    for start, end in find_sentence_spans(line):
        old = line[start:end]
        new, info = convert_sentence(old)
        parts.append(new)
        if info is not None:
            label = str(index + 1)
            changes.append(f"{label}: {snippet(old, info[0])}\n{' ' * len(label)}  {snippet(new, info[1])}")
    lines[index] = ''.join(parts)

def space_dashes(line):
    result = []
    i = 0
    n = len(line)
    while i < n:
        if line[i] != DASH:
            result.append(line[i])
            i += 1
            continue
        j = i
        while j < n and line[j] == DASH:
            j += 1
        s = len(result)
        while s > 0 and result[s - 1] in ' \t':
            s -= 1
        if s > 0 and (s < len(result) or result[s - 1] not in OPENERS):
            del result[s:]
            result.append(' ')
        result.append(line[i:j])
        k = j
        while k < n and line[k] in ' \t':
            k += 1
        if k == n or line[k] == '\r':
            result.append(line[j:])
            break
        if k > j or line[k] not in TRAILING_CLOSERS + TERMINATORS:
            result.append(' ')
        i = k
    return ''.join(result)

def report():
    if SHOW_CHANGES:
        for change in changes:
            print(change)
            print()
    print(f"Single em dash converted: {counts['converted']}")
    print(f"Short em dash pair turned into parentheses: {counts['parenthesized']}")
    print(f"Single em dashes left unchanged (interruption, fragment, or edge position): {counts['skipped']}")
    print(f"Other em dash combinations left unchanged: {counts['multi']}")

def run(path):
    changes.clear()
    for key in counts:
        counts[key] = 0
    lines[:] = load_lines(path)
    for index in range(len(lines)):
        fix_line(index)
    for index in range(len(lines)):
        lines[index] = space_dashes(lines[index])
    write_lines(path, lines)
    report()

def main():
    run(prompt_path())

if __name__ == '__main__':
    main()
