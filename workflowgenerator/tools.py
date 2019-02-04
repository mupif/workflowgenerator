

def generate_indents(n):
    return "\t"*n


def push_indents_before_each_line(code_lines, indent):
    new_code_lines = []
    for line in code_lines:
        new_code_lines.append(generate_indents(indent) + line)
    return new_code_lines


def replace_tabs_with_spaces_for_each_line(code_lines):
    new_code_lines = []
    for line in code_lines:
        new_code_lines.append(line.replace("\t", " "*4))
    return new_code_lines


def formatCodeToText(code, level=-1):
    text_code = ""
    if isinstance(code, str):
        text_code += "%s%s\n" % ('\t' * level, code)
    else:
        for line in code:
            text_code += formatCodeToText(line, level + 1)
    return text_code
