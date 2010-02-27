"""Magic template file.

:func:`pre_template` function can be defined which is executed *before* any
templating on this directory is done. :func:`pre_template` should be in format:

    pre_template(env, file_substs=None, substs=None)

Where `env` is templating environment, `file_substs` are file based template
context substitions, and `substs` are global template context substitions.

"""

import os


def pre_template(env):
    env.globals['repr'] = repr        
    # Remove me!
    os.remove("__template.py")