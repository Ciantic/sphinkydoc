Sphinkydoc |version|
====================

This is Sphinx documentation generator helper script and extension. Main purpose
is to leverage the power of Sphinx for small Python projects. Similar idea as in
EpyDoc where all documentation is embedded in docstrings.

Licensed under FreeBSD license, see :ref:`COPYING`.

Usage example
=============
Go to directory where you want the HTML documentation to appear, and run the 
main script `sphinkydoc.py`:

::

	$ sphinkydoc.py yourmodule 
	
It is usually good idea to create ``docs`` directory in your project directory.
This also enables the sphinkydoc script to find out the `README`, `COPYING`,
`INSTALL` magic files your project may have. The script looks the magic 
files from directory upwards from the ``docs`` directory.

Here is another example, this is used to generate documentation for Sphinkydoc 
itself. (Executed inside ``docs`` directory of sphinkydoc project)

::

	$ sphinkydoc.py -s"../src/sphinkydoc.py" examplepackage sphinkydocext
	
Little bit of explanation, -s means the next argument is some sort of 
script or executable, not necessarily Python script. Sphinkydoc tries to call your 
scripts using ``--help`` and generating documentation page according to that. 
You can read more about :ref:`sphinkydoc.py` in the documentation.