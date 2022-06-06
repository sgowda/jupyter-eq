import re
from IPython.core.display import HTML

def parse_math(html):
    # Parse any in-line math by converting the dollar sign to the appropriate \( or \)
    pattern = r"(.*)(\$)(.*?)(\$)(.*)"

    html_repl = re.sub(pattern, r"\1\(\3\)\5", html)

    while html_repl != html:
        html = html_repl
        html_repl = re.sub(pattern, r"\1\(\3\)\5", html)

    return html_repl


def parse_eq_block_into_lines(eq_block):
    #eq_block = eq_block.replace('\n', '')
    eq_lines = []

    # find all of the newlines and amperstands which are not array/case environments
    newline_inds = [0]
    col_inds = []
    state = 'eq' ## TODO should actually be a stack (eq -> array -> cases -> array etc so you can check for matching)
    pattern = r'\\'

    ARRAY_START_TOKEN = r'\begin{array}'
    ARRAY_END_TOKEN = r'\end{array}'
    NEWLINE_TOKEN = r'\\'
    COL_TOKEN = '&'

    def _match(idx, token):
        return eq_block[idx-len(token):idx] == token

    for k in range(len(pattern), len(eq_block)):
        if state == 'eq':
            if _match(k, ARRAY_START_TOKEN):
                state = 'array'
            elif _match(k, NEWLINE_TOKEN):
                newline_inds.append(k)
            elif _match(k, COL_TOKEN):
                col_inds.append(k)
        elif state == 'array':
            if _match(k, ARRAY_END_TOKEN):
                state = 'eq'

    newline_inds.append(len(eq_block) + len(NEWLINE_TOKEN))

    for idx1, idx2 in zip(newline_inds[:-1], newline_inds[1:]):
        eq_line = eq_block[idx1:idx2 - len(NEWLINE_TOKEN)]

        all_whitespace = re.match('^\w*$', eq_line)
        if all_whitespace:
            continue

        amp_inds = filter(lambda x: x >= idx1 and x <= idx2, col_inds)
        amp_inds = [x - idx1 for x in amp_inds]

        amp_inds = [0] + amp_inds + [len(eq_line) + len(COL_TOKEN)]
        eq_line_cols = []
        for c1, c2 in zip(amp_inds[:-1], amp_inds[1:]):
            eq_col = eq_line[c1:c2 - len(COL_TOKEN)]
            eq_col.replace('\n', '')
            eq_line_cols.append(eq_col)


        eq_lines.append(eq_line_cols)
    return eq_lines

def generate_html(lines):
    idx = 0
    html = ""
    for k,line_cols in enumerate(lines):
        line_html = "<tr id='block-{}-row-{}'>".format(idx, k)
        for k,col in enumerate(line_cols):
            if k == 0 or k == 2:
                text_align = 'right'
            else:
                text_align = 'left'

            m_col_text = re.match("\s+\text{(.*)}\s+", col)
            if m_col_text:
                line_html += r"<td style='text-align:{}'>{}</td>".format(text_align, m_col_text.group(1))
            else:
                col = parse_math(col)
                line_html += r"<td style='text-align:{}'>\({}\)</td>".format(text_align, col)
        line_html += "</tr>\n"
        html += line_html

    html = "<table id='block-0-proof' style='width:100%'>\n{}\n</table>".format(html)

    elem_names = []
    for k in range(len(lines)):
        elem_names += ["block-{}-row-{}".format(idx, k)]


    # add script
    # html += """
    # <script>
    #     # IterableView({}, 'block-0-proof')


    # </script>

    # """.format("[" + ", ".join(elem_names) + "]")

    return html

def render_latex_eq_block(latex_eq_block):
    eq_lines = parse_eq_block_into_lines(latex_eq_block)
    return HTML(generate_html(eq_lines))
