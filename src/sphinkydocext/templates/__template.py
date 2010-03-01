"""Magic template additions."""
from sphinkydocext import log

def indent(num, text):
    """Indents the string by given number."""
    s = text.split('\n')
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


def cmdoption(opt):
    """Tries to turn :obj:`optparser.Option` to cmdoption.
    
    :param opt: :obj:`optparser.Option`.
    :returns: rst cmdoption directive.
    
    """
    opts = []
    for o in (opt._short_opts + opt._long_opts):
        if opt.metavar or opt.nargs:
            opts.append('%s <%s>' % (o, opt.metavar or opt.dest.upper()))
        else:
            opts.append(o)
            
    head = ", ".join(opts)
    help = indent(4, opt.help or "")
    
    return """
.. cmdoption:: %(head)s

%(help)s
""" % {'head' : head, 'help' : help }


def pre_template(env):
    env.globals['module_split'] = module_split
    env.globals['indent'] = indent
    env.globals['repr'] = repr    
    env.globals['cmdoption'] = cmdoption