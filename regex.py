import collections
import string

class Regex(object):
    """
    Basic implementation of regular expression matcher. It provides
    one feature not found in common existing implementations: support
    for wildcard characters in matched text. The interactions between
    back-references matching and wildcards in text are iffy, but this
    is good enough for solving regexp crosswords.

    The implementation is based on non-deterministic finite automata
    with back-references support bolted on top.
    
    Supported features:
    - wildcards in both regex and text
    - repetitions - ?, *, +
    - groups - ()
    - alternatives - |
    - character ranges - [...], [^...]
      Note: using "-" to specify contiguous ranges is not supported
    - back-references
    """
    
    def __init__(self, begin_node, match_node, group_count):
        self.begin_node = begin_node
        self.match_node = match_node
        self.group_count = group_count

    @classmethod
    def compile(cls, input):
        return RegexBuilder().compile(input)

    def match(self, input):
        seen = set()            # set((RegexNode, pos, groups))
        queue = collections.deque()              # deque((RegexNode, pos, groups))

        def visit(node, pos, groups):                
            tripple = (node, pos, groups)
            if tripple not in seen:
                seen.add(tripple)
                queue.append(tripple)

        visit(self.begin_node, 0, tuple(['' for x in range(self.group_count)]))

        # print "match_node: ", match_node
        # print "len(input):", len(input)
        
        while queue:
            node, pos, groups = queue.popleft()

            # print(node, pos)
            if node.begins_group is not None and not groups[node.begins_group - 1]:
                groups = self._extendGroup(groups, node.begins_group, '^')
            if node.ends_group is not None and '$' not in groups[node.ends_group - 1]:
                groups = self._extendGroup(groups, node.ends_group, '$')
                
            if node == self.match_node and pos == len(input):
                return True

            for nxt in node.implied:
                visit(nxt, pos, groups)
                
            if pos >= len(input):
                continue
                
            c = input[pos]
            # match wildcard in regex
            for nxt in node.edges.get('.') or []:
                visit(nxt, pos + 1, self._extendGroups(groups, c))
            # match wildcard in input
            if c == '.':
                for ec, edges in node.edges.iteritems():
                    for nxt in edges:
                        visit(nxt, pos + 1, self._extendGroups(groups, c))
            else:
                for nxt in node.edges.get(c) or []:
                    visit(nxt, pos + 1, self._extendGroups(groups, c))
            # match groups
            for gr, edges in node.matchGroupEdges.iteritems():
                group = groups[gr - 1]                
                group_match = (pos + len(group) - 2 <= len(input))
                cur_groups = groups
                if not group_match:
                    continue
                for i in range(len(group) - 2):
                    if group[i + 1] != '.' and input[pos + i] != '.' and group[i + 1] != input[pos + i]:
                        group_match = False
                        break
                    else:
                        cur_groups = self._extendGroups(cur_groups, input[pos + i])
                if group_match:
                    for nxt in edges:
                        visit(nxt, pos + len(group) - 2, cur_groups)
            
        return False

    def _extendGroups(self, groups, c):
        groups = list(groups)
        for i, g in enumerate(groups):
            if g and g[-1] != '$':
                groups[i] = g + c
        return tuple(groups)

    def _extendGroup(self, groups, index, c):
        groups = list(groups)
        groups[index - 1] += c
        return tuple(groups)

    def walk(self, visit_node, visit_edge):
        seen = set()    
        queue = collections.deque()

        def visit(node):                
            if node not in seen:
                seen.add(node)
                queue.append(node)

        visit(self.begin_node)

        while queue:
            node = queue.popleft()
            visit_node(node)
            for nxt in node.implied:
                visit_edge(node, '<implies>', nxt)
                visit(nxt)
            for c, nodes in sorted(node.edges.items()):
                for nxt in nodes:
                    visit_edge(node, str(c), nxt)
                    visit(nxt)
            for group, nodes in sorted(node.matchGroupEdges.items()):
                for nxt in nodes:
                    visit_edge(node, '\\%d' % group, nxt)
                    visit(nxt)

    def display(self):
        """
        Print regex state graph to stdout
        """
        def visit_node(node):
            group_str = ''
            if node.begins_group is not None:
                group_str = '(begins group %d)' % node.begins_group
            if node.ends_group is not None:
                group_str = '(ends group %d)' % node.ends_group
            print '%s %s %s' % (
                node,
                "- match" if node == self.match_node else "",
                group_str,
                )
        def visit_edge(node, edge_descr, nxt):
            print "  %s => %s" % (edge_descr, nxt)
            
        self.walk(visit_node, visit_edge)
        
class RegexBuilder(object):
    def __init__(self):
        self.node_count = 0
        self.group_count = 0
        self.used_groups = {}

    def _createNode(self):
        self.node_count += 1
        return RegexNode(str(self.node_count))
        
    def compile(self, input):
        begin_node, end_node = self._compileRegex(input)
        self.used_groups[0] = False
        regex = Regex(begin_node, end_node, max(self.used_groups.keys()))

        def clear_unused_groups(node):
            if not self.used_groups.get(node.begins_group):
                node.begins_group = None
            if not self.used_groups.get(node.ends_group):
                node.ends_group = None
        regex.walk(clear_unused_groups, lambda x, y, z: None)

        return regex

    def _firstToken(self, regex):
        """
        """
        token = ''
        repeat = ''
        if regex[0] == '[':
            for i, c in enumerate(regex):
                if c == ']':
                    break
        elif regex[0] == '(':
            open_brackets = 0
            in_range = False
            for i, c in enumerate(regex):
                if in_range and c != ']':
                    continue
                elif c == '(':
                    open_brackets += 1
                elif c == ')':
                    open_brackets -= 1
                    if open_brackets == 0:
                        break
                elif c == '[':
                    in_range = True
                elif c == ']':
                    in_range = False
        elif regex[0] == '\\':
            i = 1
            while i < len(regex) and regex[i].isdigit():
                i += 1
            i -= 1
        else:
            i = 0
        i += 1
        token = regex[0:i]
        regex = regex[i:]
        return token, regex

    def _compileToken(self, token):
        if token[0] == '(':
            compiled = self._compileRegex(token[1:-1])
            self.group_count += 1
            compiled[0].begins_group = self.group_count
            compiled[1].ends_group = self.group_count
            return compiled

        beg_node = self._createNode()
        match_node = self._createNode()

        if token[0] == '[':
            # TODO: handle dashes
            to_match = []
            for c in token[1:-1]:
                to_match.append(c)
            if token[1] == '^':
                to_match.remove('^')
                to_match = [x for x in string.ascii_uppercase if x not in to_match]            
            for c in to_match:
                beg_node.addNext(c, match_node)
        elif token[0] == '\\':
            group = int(token[1:])
            self.used_groups[group] = True
            beg_node.addMatchGroup(group, match_node)
        else:
            to_match = [token[0]]
            beg_node.addNext(token[0], match_node)
        
        return beg_node, match_node

    def _joinSequence(self, seq):            
        for i in range(len(seq) - 1):
            seq[i][1].addImplied(seq[i + 1][0])
        return (seq[0][0], seq[-1][1])

    def _compileRegex(self, regex):
        terms = []           # terms are separated by OR
        term = []            # current sequence of tokens
        while regex:
            if regex[0] == '|':
                # handle OR
                regex = regex[1:]
                terms.append(self._joinSequence(term))
                term = []
                continue
            elif regex[0] == '?':
                token = term[-1]
                token[0].addImplied(token[1])
                regex = regex[1:]
            elif regex[0] == '+':                
                token = term[-1]
                token[1].addImplied(token[0])
                regex = regex[1:]
            elif regex[0] == '*':
                token = term[-1]
                token[0].addImplied(token[1])
                token[1].addImplied(token[0])
                regex = regex[1:]
            else:
                token, regex = self._firstToken(regex)
                term.append(self._compileToken(token))
                
        if term:
            terms.append(self._joinSequence(term))
                    
        if len(terms) == 0:
            node = self._createNode()
            return node, node
        elif len(terms) == 1:
            return terms[0]
        else:
            beg_node = self._createNode()
            match_node = self._createNode()
            for term_beg, term_match in terms:
                beg_node.addImplied(term_beg)
                term_match.addImplied(match_node)
            return beg_node, match_node
        

class RegexNode(object):
    
    def __init__(self, name):
        self.edges = {}
        self.implied = []       # epsilon-move edges
        self.matchGroupEdges = {}
        self.begins_group = None
        self.ends_group = None
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def addNext(self, char, node):
        self.edges.setdefault(char, []).append(node)

    def addImplied(self, node):
        if node != self and node not in self.implied:
            self.implied.append(node)

    def addMatchGroup(self, group, node):
        self.matchGroupEdges.setdefault(group, []).append(node)
