"""Magic template additions."""

def indent(num, str):
    """Indents the string by given number."""
    s = str.split('\n')
    s = [(num * ' ') + line for line in s]
    s = "\n".join(s)
    return s

def module_split(module_name):
    """Splits the module name and formats as rst."""
    
    ms = []
    m = []
    
    for subm in module_name.split("."):
        m.append(subm)
        ms.append(":mod:`%s<%s>`" % (subm, ".".join(m)))
        
    return ". ".join(ms) 

def pre_template(env):
    env.globals['module_split'] = module_split
    env.globals['indent'] = indent