import ast


def stringfy(node, inner=True):
    if isinstance(node, ast.Name):
        return str(node.id)
    if isinstance(node, ast.Attribute):
        return stringfy(node.value) + '.' + str(node.attr)
    if isinstance(node, ast.Call):
        return stringfy(node.func) + '()'
    if isinstance(node, ast.Subscript):
        return stringfy(node.value)+'['+stringfy(node.slice)+']'
    if isinstance(node, ast.Slice):
        if not inner:
            return '@'
        base = stringfy(node.lower)+':'+stringfy(node.upper)
        if node.step is None:
            return base
        return base + ':' + stringfy(node.step)
    if isinstance(node, ast.Index):
        return stringfy(node.value)
    if inner:
        if isinstance(node, ast.Constant):
            return str(node.value)
        if isinstance(node, ast.Num):
            return str(node.n)
        if isinstance(node, ast.Str):
            return str(node.s)
        if node is None:
            return ''
    return '@'


def traverse(node, ss: set):
    #print(ast.dump(node), stringfy(node, inner=False))
    snipet = stringfy(node, inner=False)
    if '@' not in snipet:
        ss.add(snipet)
    for sub_node in ast.iter_child_nodes(node):
        traverse(sub_node, ss)
    return ss


def extract_vars(code):
    try:
        node = ast.parse(code)
        ss = traverse(node, set())
        return [s for s in ss if (not s.endswith('()')) and (s+'()' not in ss)]
    except SyntaxError:
        return []
