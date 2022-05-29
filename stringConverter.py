from anytree import Node, PreOrderIter

symbol_codes = {
    "NEG" : '\xac',
    "AND" : '\u2227',
    "OR" : '\u2228',
    "IMP" : '\u2192',
    "BI_IMP" : '\u2194',
    1 : '\u2081',
    2 : '\u2082'
}

# recursively traverses the 
def convert(root_node):
    stroutput = []
    operator = None
    if root_node.is_leaf:
        return list(str(root_node.name))

    # alternative nesting
    # if children nodes have children themselves

    if "NEG" in root_node.name:
        # stroutput.append(0)
        stroutput.append('\xac')
        if root_node.name == "DOUBLE_NEG":
            # stroutput.append(0)
            stroutput.append('\xac')
    # if not the true root/main connective and it's not an atomic negation
    if root_node.depth > 0 and len(root_node.children) > 1:
        # if root_node is one of binary connectives (priority tiers 2 and 5), put brackets around the expression
        if root_node.priority in [2, 5]:
            stroutput.append(0)
            stroutput.append('(')
    elif "NEG_" in root_node.name:
        stroutput.append(0)
        stroutput.append('(')
    # elif root_node.name == "NEG":
    #     stroutput.append('\xac')

    if "AND" in root_node.name:
        operator = '&&'
    elif "OR" in root_node.name:
        operator = '||'
    elif root_node.name == "IMP" or root_node.name == "NEG_IMP":
        operator = '\u2192'
    elif "BI_IMP" in root_node.name:
        operator = '\u2194'
    elif "K" in root_node.name or "M" in root_node.name:
        left_part = root_node.children[0].name
        if "K" in root_node.name:
            operator = "K"
        elif "M" in root_node.name:
            operator = "M"
        # replaces string agent identifiers with appropriate subscript unicode characters
        # maximum of 2 agents
        # FIXME: change if more agents used
        if left_part == 1:
            left_part = '\u2081'
        elif left_part == 2:
            left_part = '\u2082'
        # TODO: rework conversion for epistemic operators
    if not operator == "K" and not operator == "M":
        left_part = convert(root_node.children[0])
    if operator:
        right_part = convert(root_node.children[1])
    
    
    
    # now add parts together
    # left-operator-right order unless operator is epistemic
    if not operator == "K" and not operator == "M":
        stroutput.extend(left_part)
    if operator:
        stroutput.append(operator)
        # if epistemic operator, left child (agent) needs to be after the epist. op.
        if operator == "K" or operator == "M":
            stroutput.append(left_part)
        stroutput.extend(right_part)
    # put closing brackets everywhere
    while 0 in stroutput:
        stroutput.remove(0)
        stroutput.append(')')

    return stroutput

def translate_formula(root_node):
    final_formula = convert(root_node)
    final_formula = ' '.join(final_formula)
    
    return final_formula