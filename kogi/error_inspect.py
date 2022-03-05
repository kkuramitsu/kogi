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
            type='var',
            name=str(tree),
        ))

    def acceptInfix(self, tree):
        self.bufs.append(dict(
            type='infix',
            name=str(tree.name).strip(),
            left=str(fix2(tree.left)),
            right=str(fix2(tree.right)),
        ))
        self.visit(tree.left)
        self.visit(tree.right)

    def acceptApplyExpr(self, tree):
        self.bufs.append(dict(
            name=fix2(tree.name),
            type='app',
        ))
        self.visit(tree.params)

    def acceptGetExpr(self, tree):
        if tree.recv == 'Name':
            self.bufs.append(dict(
                name=str(tree.recv),
                property=str(tree.name),
                type='module',
            ))
        self.bufs.append(dict(
            name=str(tree.name),
            callee=fix2(tree.recv),
            type='prop',
        ))

    def acceptMethodExpr(self, tree):
        if tree.recv == 'Name':
            self.bufs.append(dict(
                name=str(tree.recv),
                prop=str(tree.name),
                type='module',
            ))
        self.bufs.append(dict(
            name=str(tree.name),
            callee=fix2(tree.recv),
            type='app',
        ))
        self.visit(tree.params)

    def acceptIndexExpr(self, tree):
        self.bufs.append(dict(
            sub=fix2(tree.index),
            callee=fix2(tree.recv),
            type='sub',
        ))
        self.visit(tree.recv)
        self.visit(tree.index)

    def acceptUndefined(self, tree):
        for t in tree:
            self.visit(t)
        for key in tree.keys():
            self.visit(tree.get(key))


f = Flatten()


def filter(results, type='sub', name=None):
    rs = []
    if name is None:
        for r in results:
            if r['type'] == type:
                rs.append(r)
    else:
        for r in results:
            if r['type'] == type and r['name'] == name:
                rs.append(r)
    return rs


def filter2(results, name, defined='callee'):
    rs = []
    for r in results:
        if defined in r and r['name'] == name:
            rs.append(r)
    return rs


def find_infix(lines, infix='+'):
    if lines is not None:
        for line in lines:
            results = filter(f.parse(line), type='infix', name=infix)
            if len(results) > 0:
                return results
    return []


def find_sub(lines):
    if lines is not None:
        for line in lines:
            results = filter(f.parse(line), type='sub')
            if len(results) > 0:
                return results
    return []


def find_app(lines):
    if lines is not None:
        for line in lines:
            results = filter(f.parse(line), type='app')
            if len(results) > 0:
                return results
    return []


def find_callee(lines, name):
    if lines is not None:
        for line in lines:
            results = filter2(f.parse(line), name=name)
            if len(results) > 0:
                return results
    return []


def find_name(lines, name):
    if lines is not None:
        for line in lines:
            results = filter2(f.parse(line), name=name, defined='name')
            if len(results) > 0:
                return results
    return []


def inspect_name(code, lines, slots):
    if lines is None:
        return ''
    return ''


def inspect_callee(code, lines, slots):
    if lines is None:
        return ''

    results = find_callee(lines, slots['name'])
    # print(slots)
    # print(results, 'callee' in results)
    for result in results:
        if 'callee' in result:
            slots['callee'] = result['callee']
            if result.get('type', 'prop') == 'prop':
                slots['pyname'] = 'プロパティ'
            else:
                slots['pyname'] = '関数' if 'module' in slots['error'] else 'メソッド'
            # print(slots)
            return '_ext'
    return ''


def inspect_infix(code, lines, slots):
    if lines is None:
        return ''
    results = find_infix(lines, slots['name'])
    # print(slots)
    # print(results)
    for result in results:
        if 'left' in result:
            slots['left'] = result['left']
            slots['right'] = result['right']
            # print(slots)
            return '_ext'
    return ''


def inspect_funcname(code, lines, slots):
    if lines is None:
        return ''
    results = find_app(lines)
    # print(slots)
    # print(results)
    for result in results:
        if 'name' in result:
            slots['name'] = result['name']
            # print(slots)
            return '_ext'
    return ''


def inspect_index(code, lines, slots):
    if lines is None:
        return ''
    results = find_sub(lines)
    print(slots)
    print(results)
    for result in results:
        if 'sub' in result:
            slots['index'] = result['sub']
            slots['callee'] = result['callee']
            # print(slots)
            return '_ext'
    return ''


if __name__ == '__main__':
    print(find_sub(['a(df["A"])+a[0]']))
    print(find_app(['a(2)+b()']))
    print(find_infix(['a()+a[0]-1'], infix='-'))
    print(find_callee(['math.sin(math.pi)'], name='sin'))
    print(find_callee(['math.sin(math.pi)'], name='pi'))
    print(find_name(['pd.read_csv()'], name='pd'))
    print(find_name(['int()'], name='int'))
