Sphinkydoc |release|
====================

This is `Sphinx documentation generator`_ helper script and extension. Main 
purpose is to leverage the power of Sphinx for small Python projects. For those 
it is usually sufficient to document the code in docstrings.

Sphinkydoc also tries to address the problem that *no documentation should be 
written twice!* This is why system also tries to look for :term:`caps-files 
<caps-file>` in your project, such as `INSTALL`, `README`, `COPYING`, which also
contain bits for the documentation.

Licensed under rather permissive :ref:`FreeBSD license<LICENSE>`

Usage example
=============
Lets assume you have project directory ``myproject/``.

Optional *additional documentation* files are located in ``myproject/docs/``, 
and should have extension ``.rst``. All the rest project files are in 
``myproject/``, if you have :term:`caps-files <caps-file>` such as 
``myproject/README``, ``INSTALL``, ``AUTHORS``, ``CHANGES``, ``LICENSE`` or any 
other file that is written in uppercase, they are treated as reStructuredText
files and included to documentation. By default there is *exception for files 
named*: ``COPYING``, ``COPYING.LESSER``, ``COPYING.LIB`` which are treated as 
:term:`literal-files<literal-file>`, because they most likely contain GPL 
related stuff, which does not convert to reStructuredText. If you instead want 
more or less files treated as literal files you must specify them using 
``--caps-literal``.

Go to directory where you want the HTML documentation -- in this case 
``myproject/docs/`` -- and run the main script :ref:`sphinkydoc.py`::

    $ sphinkydoc.py yourmodule
    
If everything went well it should have created two directories for you 
``myproject/docs/html/`` and ``myproject/docs/_temp/`` (which is deleted before 
each run). The script simply looks the :term:`caps-files<caps-file>` by default 
from directory *upwards from the execution directory*, you can also explicitely 
specify using :option:`--caps-dir` the directory of 
:term:`caps-files<caps-file>`.

Here is another example, executed inside ``docs/`` directory of sphinkydoc 
project, this is used to generate documentation for Sphinkydoc itself::

   $ sphinkydoc.py -s"../src/sphinkydoc.py" sphinkydocext examplepackage
    
Little bit of explanation, :option:`-s` means the next argument is some sort of 
script or executable, not necessarily Python script. First Sphinkydoc tries to
get the :obj:`~optparser.OptionParser` of your script, if it fails it tries to 
call your scripts using ``--help`` and generating documentation page according 
to that. Then are listed modules and packages, these modules are crawled 
recursively for Python docstrings. First of the modules given is a sort of 
primary module of your project, where Sphinkydoc also looks for variables 
``__project__``, ``__version__``, ``__release__``, ``__copyright__``. If you 
type ``|release|`` in e.g. ``README``, it is rendered as same string as in your
module. This way you can maintain version information in *one place*.

.. seealso:: :ref:`Full option listing for sphinkydoc.py <sphinkydoc.py>` in the 
	documentation.

.. _Sphinx documentation generator: http://sphinx.pocoo.org/