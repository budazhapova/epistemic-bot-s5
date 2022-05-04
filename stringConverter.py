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
def translate_formula(root_node):
    stroutput = []
    operator = None
    if root_node.is_leaf:
        return list(str(root_node.name))

    # TODO: add handling for "neg-atom" and brackets for nested binary operators
    if "NEG_" in root_node.name:
        stroutput.append(0)
        stroutput.append('\xac(')
        # TODO: if list starts with 0, pop it and add a bracket in the end
    elif root_node.name == "DOUBLE_NEG":
        stroutput.append(0)
        stroutput.append('\xac\xac(')

    if "AND" in root_node.name:
        operator = '\u2227'
    elif "OR" in root_node.name:
        operator = '\u2228'
    elif root_node.name == "IMP" or root_node.name == "NEG_IMP":
        operator = '\u2192'
    elif "BI_IMP" in root_node.name:
        operator = '\u2194'
    left_part = translate_formula(root_node.children[0])
    if operator:
        right_part = translate_formula(root_node.children[1])
    # replaces string agent identifiers with appropriate subscript unicode characters
    if "K" in root_node.name or "M" in root_node.name:
        # maximum of 2 agents
        if left_part == ['1']:
            left_part = ['\u2081']
        elif left_part == ['2']:
            left_part = ['\u2082']
    
    # now add parts together
    stroutput.extend(left_part)
    if operator:
        stroutput.append(operator)
        stroutput.extend(right_part)
    if stroutput[0] == 0:
        stroutput.pop(0)
        stroutput.append(')')

    return stroutput