input_path = "input.txt"
output_path = "output.txt"
SHOW_CHANGES = True
DASH = '\u2014'
REPLACEMENT = '; '
TERMINATORS = '.!?'
TRAILING_CLOSERS = '"\u201d\u2019\')]}'
RIGHT_OK_STARTS = '"\u201c\u2018\'([{'
ABBREVIATIONS = {
    'mr', 'mrs', 'ms', 'dr', 'prof', 'sr', 'jr', 'st', 'mt', 'vs', 'etc',
    'inc', 'ltd', 'co', 'no', 'fig', 'approx', 'gen', 'col', 'capt', 'lt',
    'sgt', 'rev', 'hon', 'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug',
    'sep', 'sept', 'oct', 'nov', 'dec',
}
lines = []
changes = []
converted_count = 0
multi_count = 0
skipped_count = 0

def load_lines():
    global lines
    with open(input_path, 'r', encoding='utf-8', newline='') as f:
        lines = f.read().split('\n')

def write_lines():
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        f.write('\n'.join(lines))

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

def convert_sentence(sentence):
    global converted_count, multi_count, skipped_count
    count = sentence.count(DASH)
    if count == 0:
        return sentence, None
    if count > 1:
        multi_count += 1
        return sentence, None
    idx = sentence.index(DASH)
    left = sentence[:idx].rstrip()
    right = sentence[idx + 1:].lstrip()
    if not can_convert(left.lstrip(), right):
        skipped_count += 1
        return sentence, None
    converted_count += 1
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

def report():
    if SHOW_CHANGES:
        for change in changes:
            print(change)
            print()
    print(f"Sentences with a single em dash converted: {converted_count}")
    print(f"Single em dashes left unchanged (interruption, fragment, or edge position): {skipped_count}")
    print(f"Sentences with multiple em dashes left unchanged: {multi_count}")

def main():
    load_lines()
    for index in range(len(lines)):
        fix_line(index)
    write_lines()
    report()

if __name__ == '__main__':
    main()
