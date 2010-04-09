"""Utils for sphinkydoc"""
from distutils.dir_util import mkpath
from pkgutil import iter_modules
import optparse
import inspect
import logging
import posixpath
import os
import re
import sys
from sphinkydocext import log


def truncate_path(path, directory=None, extension=None):
    """Truncates given path.
    
    :param path: Path to be truncated.
    :param directory: Truncates the directory from beginning.
    :param extension: Truncates the extension from end.
    
    :returns: Path truncated.
    
    >>> truncate_path("C:\\somedirectory\\mydocs\\some file.rst", "C:\\somedirectory", "rst")
    mydocs\some_file.rst
     
    """
    truncpath = path
    
    if directory is not None:
        if truncpath.startswith(directory):
            truncpath = truncpath[len(directory)+1:]
            
    if extension is not None:
        if truncpath.endswith(".%s" % extension):
            truncpath = truncpath[:-len(extension)-1]
            
    return truncpath


def directory_slash_suffix(str):
    """Add the directory slash suffix.
    
    Converts the directory to posixpath if not already. Slashes are not added to
    empty strings.
    
    :param str: Path to slashes.
    :returns: Path representing directory.
    
    """
    str = posixpath.normpath(str)
    
    # Empty strings are not added slashes
    if not str:
        return str
    
    # Add slashes to the end of path
    if not str.endswith('/'):
        return str + "/"
    
    # Return unchanged, the path had slash already
    return str


def multi_matcher(patterns):
    """Returns multi matcher for several patterns.
    
    If pattern contains a string, it is treated as direct comparsion with 
    equivalence. In case the pattern has match function, it is used to matching.
    
    :param patterns: Sequence of either string or matcher objects.
    
    """
    def matcher(item):
        for pat in patterns:
            if hasattr(pat, 'match'):
                if pat.match(item):
                    return True
            else:
                if pat == item:
                    return True
        return False
    return matcher


def path_to_posix(filepath):
    """Converts path to posix path."""
    return filepath.replace("\\", "/")


def quote_split(text):
    """Splits the string by quotes.
    
    :param text: String to be split.
    
    >>> quote_split('something test "something awesome"')
    ['something', 'test', 'something awesome']
    
    """
    return [p.strip("\" ") for p in re.split("( |[\\\"'].*[\\\"'])", text) 
            if p.strip("\" ")]


def copy_tree(src, dst, preserve_mode=1, preserve_times=1, preserve_symlinks=0, 
    update=0, verbose=0, skip_dirs=None, log=None, dry_run=0):
    """Copy an entire directory tree 'src' to a new location 'dst'.
    
    Modified copy_tree, taken from distutils.dir_util.
      
    Both 'src' and 'dst' must be directory names.  If 'src' is not a directory,
    raise DistutilsFileError.  If 'dst' does not exist, it is created with
    'mkpath()'.  The end result of the copy is that every file in 'src' is
    copied to 'dst', and directories under 'src' are recursively copied to
    'dst'.  Return the list of files that were copied or might have been copied,
    using their output name.
    
    The return value is unaffected by 'update' or 'dry_run': it is simply the
    list of all files under 'src', with the names changed to be under 'dst'.
    
    'preserve_mode' and 'preserve_times' are the same as for
    'copy_file'; note that they only apply to regular files, not to
    directories.  If 'preserve_symlinks' is true, symlinks will be copied as
    symlinks (on platforms that support them!); otherwise (the default), the
    destination of the symlink will be copied.
    
    'update' and 'verbose' are the same as for 'copy_file'.
    
    """
    from distutils.file_util import copy_file
    
    if log is None:
        #logging.basicConfig()
        log = logging.getLogger("sphinkydoc")
    
    skip_dirs = skip_dirs or []
    
    if not dry_run and not os.path.isdir(src):
        log.error("cannot copy tree '%s': not a directory", src)
        sys.exit(0)
    try:
        names = os.listdir(src)
    except os.error, (_errno, errstr):
        if dry_run:
            names = []
        else:
            log.error("error listing files in '%s': %s", src, errstr)
            sys.exit(0)
    if not dry_run:
        mkpath(dst)
    outputs = []
    for n in names:
        src_name = os.path.join(src, n)
        dst_name = os.path.join(dst, n)
        # pylint: disable-msg=E1101
        if preserve_symlinks and os.path.islink(src_name):
            link_dest = os.readlink(src_name) #@UndefinedVariable
            log.info("linking %s -> %s", dst_name, link_dest)
            if not dry_run:
                os.symlink(link_dest, dst_name) #@UndefinedVariable
            outputs.append(dst_name)
            # pylint: enable-msg=E1101
        elif os.path.isdir(src_name):
            if n in skip_dirs:
                continue
            
            outputs.extend(
                copy_tree(src_name, dst_name, preserve_mode, 
                    preserve_times, preserve_symlinks, update, 
                    dry_run=dry_run))
        else:
            copy_file(src_name, dst_name, preserve_mode, 
                preserve_times, update, dry_run=dry_run)
            outputs.append(dst_name)
    
    return outputs


def is_python_script(script_path):
    """Determine if given script path is python script.
    
    :param script_path: Path to script
    :rtype: bool
    
    """
    if script_path.endswith(".py") or script_path.endswith(".pyw"):
        return True
    
    # TODO: !# python test.
    
    return False


def script_get_optparser(script_path):
    """Gets first :obj:`~optparse.OptionParser` from script, if possible.
    
    Idea is to loop all globals after :func:`execfile` and look for
    :obj:`optparse.OptionParser` instances.
    
    :param script_path: Path to the script.
    :returns: :const:`None`, or :obj:`optparse.OptionParser`
    
    """
    globs = {}
    log.info("Looking for optparser, by execfile script: %s" % script_path)
    try:
        execfile(script_path, globs)
    except:
        log.info("Script %s cannot be executed using execfile" % script_path)
        return
    
    for _n, val in globs.iteritems():
        # TODO: LOW: We could probably do more duck-typing friendly check here
        # too, but that is low priority.
        if isinstance(val, optparse.OptionParser):
            return val
        

def all_filterer(module, use_all=True):
    """All filterer for module.
    
    :param use_all: Use `__all__` of module, if true.
    
    """
    # Explicitely defined public members
    if use_all and hasattr(module, "__all__"):
        has_all = True
        custom_all = lambda m,n: n in module.__all__
    else:
        has_all = False
        
        if use_all:
            log.info("Module %s is missing __all__, falling back to "
                     "public members" % module.__name__)
        
        custom_all = lambda _m,n: not n.startswith("_")
    return has_all, custom_all


def get_submodules(module, use_all=True, custom_all=None):
    """Generator that get submodules of module.
    
    :param use_all: Use `__all__` of module, if true.
    :param custom_all: Overrides any all settings with own all filter function.
    
    """
    if custom_all is None:
        _has_all, custom_all = all_filterer(module, use_all=use_all)
        
    # Retrieve all submodules
    if hasattr(module, "__path__"): 
        for _imp, modname, _isp in iter_modules(module.__path__):
            if custom_all(module, modname):
                yield modname
    
    
def get_module_members(module, use_all=True, custom_all=None):
    """Return module members.
    
    :param use_all: Use `__all__` of module, if true.
    :param custom_all: Overrides any all settings with own all filter function.
    
    """
    
    if custom_all is None:
        has_all, custom_all = all_filterer(module, use_all=use_all)
    
    all_submodules = list(get_submodules(module))
    modules = all_submodules
    
    all_classes = []
    all_exceptions = []
    all_functions = []
    all_datas = []
    all_members = []
    
    for name in dir(module):
        obj = getattr(module, name)
        
        # Filter out the members that are not defined in this module, except
        # those that are listed in __all__ if any.
        if hasattr(obj, "__module__"):
            if not (has_all and custom_all(module, name)) and \
                obj.__module__ != module.__name__:
                continue
        
        if inspect.isclass(obj):
            if issubclass(obj, Exception):
                all_exceptions.append(name)
            else:
                all_classes.append(name)
        elif inspect.isfunction(obj):
            all_functions.append(name)
        elif inspect.ismodule(obj):
            continue # Not added as member either!
        else:
            all_datas.append(name)
            
        all_members.append(name)
        
    classes = [x for x in all_classes if custom_all(module, x)]
    exceptions = [x for x in all_exceptions if custom_all(module, x)]
    functions = [x for x in all_functions if custom_all(module, x)]
    datas = [x for x in all_datas if custom_all(module, x)]
    members = [x for x in all_members if custom_all(module, x)]
            
    return {'all_modules': all_submodules, 'modules' : modules,
            'all_exceptions' : all_exceptions, 'exceptions' : exceptions,
            'all_classes' : all_classes, 'classes' : classes,
            'all_functions' : all_functions, 'functions' : functions,
            'all_datas' : all_datas, 'datas' : datas,
            'all_members' : all_members, 'members' : members,}


def import_by_name(name):
    """Light import wrapper"""
    try:
        __import__(name)
        return sys.modules[name], sys.modules[name].__name__
    except (ImportError, KeyError, ValueError):
        raise ImportError("Unable to import %s " % name)
    
     