"""Magic template file.

:func:`pre_template` function can be defined which is executed *before* any templating
on this directory is done. :func:`pre_template` should be in format:

    pre_template(env, file_substs=None, substs=None)

Where `env` is templating environment, `file_substs` are file based template
context substitions, and `substs` are global template context substitions.

"""

import os

INCLUDED_FILES = ['README']
ABOUT_FILES = ['COPYING', 'COPYING.LESSER', 'LICENSE', 'AUTHORS']

def topic_files(files):
    return list(filter((lambda f: f not in (ABOUT_FILES + INCLUDED_FILES)), 
                       files))

def about_files(files):
    return list(filter((lambda f: f in ABOUT_FILES), files))

def docs_files(path):
    """Docs files, relative to path.
    
    :returns: List of .rst files in path.
    
    """
    pass

def pre_template(env):
    env.globals['topic_files'] = topic_files
    env.globals['about_files'] = about_files        
    # Remove me!
    os.remove("__template.py")