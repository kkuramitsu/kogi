try:
    import pegtree as pg
    from pegtree.visitor import ParseTreeVisitor
except ModuleNotFoundError:
    import os
    os.system('pip3 install pegtree')
    import pegtree as pg
    from pegtree.visitor import ParseTreeVisitor


def fix(tree):
    a = [tree.epos_]
    for t in tree:
        a.append(fix(t).epos_)
    for key in tree.keys():
        a.append(fix(tree.get(key)).epos_)
    #print(repr(tree), a)
    tree.epos_ = max(a)
    return tree


def fix2(s):
    if not isinstance(s, str):
        s = str(fix(s))
    open = s.count('(')
    close = s.count(')')
    if open > 0 and open > close:
        return s+(')' * (open-close))
    open = s.count('[')
    close = s.count(']')
    if open > 0 and open > close:
        return s+(']' * (open-close))
    return s


parser = pg.generate(pg.grammar('inspect.pegtree'))


class Flatten(ParseTreeVisitor):
    def __init__(self):
        ParseTreeVisitor.__init__(self)

    def parse(self, s: str, bufs=None):
        tree = parser(s)
        self.bufs = [] if bufs is None else bufs
        self.visit(tree)
        return self.bufs

    def acceptName(self, tree):
        self.bufs.append(dict(
            cname=str(tree),
            ctype='var',
        ))

    def acceptInfix(self, tree):
        self.bufs.append(dict(
            cname=str(tree.name).strip(),
            ctype='infix',
            infix_left=str(fix2(tree.left)),
            infix_right=str(fix2(tree.right)),
        ))
        self.visit(tree.left)
        self.visit(tree.right)

    def acceptApplyExpr(self, tree):
        self.bufs.append(dict(
            cname=fix2(tree.name),
            ctype='app',
        ))
        self.visit(tree.params)

    def acceptGetExpr(self, tree):
        self.bufs.append(dict(
            cname=str(tree.name),
            ctype='field',
            recv=fix2(tree.recv),
        ))

    def acceptMethodExpr(self, tree):
        self.bufs.append(dict(
            cname=str(tree.name),
            ctype='method',
            recv=fix2(tree.recv),
        ))
        self.visit(tree.params)

    def acceptIndexExpr(self, tree):
        self.bufs.append(dict(
            ctype='index',
            recv=fix2(tree.recv),
            index=fix2(tree.index),
        ))
        self.visit(tree.recv)
        self.visit(tree.index)

    def acceptUndefined(self, tree):
        for t in tree:
            self.visit(t)
        for key in tree.keys():
            self.visit(tree.get(key))


f = Flatten()


def parse_find(line, ctype=None, cname=None, defined_key=None, ctype_key='ctype', cname_key='cname'):
    rs = f.parse(line.strip())
    ss = []
    for r in rs:
        if defined_key is not None and defined_key not in r:
            continue
        if cname is not None and r.get(cname_key, None) != cname:
            continue
        if ctype is not None and r.get(ctype_key, None) != ctype:
            continue
        r['code'] = line.strip()
        ss.append(r)
    return ss


def parse_find_name(lines, name, defined_key='cname'):
    ss = []
    for line in lines:
        ss.extend(parse_find(line, defined_key=defined_key, cname=name))
    return ss

def parse_find_app(lines):
    ss = []
    for line in lines:
        ss.extend(parse_find(line, ctype='app'))
    return ss

def parse_find_infix(lines, infix):
    ss = []
    for line in lines:
        ss.extend(parse_find(line, ctype='infix', cname=infix))
    return ss


def parse_find_index(lines):
    ss = []
    for line in lines:
        ss.extend(parse_find(line, ctype='index'))
    return ss


if __name__ == '__main__':
    print(parse_find_name('a+b', 'a'))
    print(parse_find_name('a()+b', 'a'))
    print(parse_find_name('o.a+b', 'a'))
    print(parse_find_name('o.a()+b', 'a'))
    print(parse_find_name('a.f+b', 'a'))
    print(parse_find_name('a[1]+b', 'a'))
    print(parse_find_name('s[a]+b', 'a'))
    print('infix')
    print(parse_find_infix('a+b+c', '+'))
    print(parse_find_infix('a()+b', '+'))
    print(parse_find_infix('o.a+b', '+'))
    print(parse_find_infix('o.a()+b', '+'))
    print(parse_find_infix('a.f+b', '+'))
    print(parse_find_infix('a[b+1]+b', '+'))
    print(parse_find_infix('s[a]+b', '+'))
    print('index')
    print(parse_find_index('a[b+1]+b'))
    print(parse_find_index('s[a]+b'))
    print(parse_find_index('a[b+1:]+b'))
    print(parse_find_index('s[a:x]+b'))
