from anytree import Node, PreOrderIter

# SUMMARY: this file contains code for recursively translating a tree-format formula into a string with the method translate_formula

symbol_codes = {
    "NEG" : '\xac',
    "AND" : '\u2227',
    "OR" : '\u2228',
    "IMP" : '\u2192',
    "BI_IMP" : '\u2194',
    1 : '\u2081',
    2 : '\u2082',
    3 : '\u2083'
}

double_symbols = " \u2227 \u2228 \u2192 \u27f7 \u2081 \u2082 \u2083"

# recursively traverses the 
def convert(root_node):
    stroutput = []
    operator = None
    if root_node.is_leaf:
        return list(str(root_node.name))

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
    elif root_node.name in ["NEG_AND", "NEG_OR", "NEG_IMP", "NEG_BI_IMP"]:
        stroutput.append(0)
        stroutput.append('(')

    if "AND" in root_node.name:
        operator = ' \u2227 '
    elif "OR" in root_node.name:
        operator = ' \u2228 '
    elif root_node.name == "IMP" or root_node.name == "NEG_IMP":
        operator = ' \u2192 '
    elif "BI_IMP" in root_node.name:
        operator = ' \u27f7 '
    elif "K" in root_node.name or "M" in root_node.name:
        left_part = root_node.children[0].name
        if "K" in root_node.name:
            operator = "K"
        elif "M" in root_node.name:
            operator = "M"
        # replaces string agent identifiers with appropriate subscript unicode characters
        # maximum of 3 agents
        # FIXME: change if more agents used
        if left_part == 1:
            left_part = '\u2081'
        elif left_part == 2:
            left_part = '\u2082'
        elif left_part == 3:
            left_part = 'D'
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
    tweet_length = 0
    final_formula = convert(root_node)

    # count the length of a future tweet with all \u200+ characters counting for two
    tweet_length = sum(len(char)+1 if (char in double_symbols) else 1 for char in final_formula)

    final_formula = ''.join(final_formula)
    
    return final_formula, tweet_length