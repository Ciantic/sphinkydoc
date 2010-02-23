Sphinkydoc |release|
====================

This is `Sphinx documentation generator`_ helper script and extension. Main purpose
is to leverage the power of Sphinx for small Python projects. For those it is 
usually sufficient to document the code in docstrings.

Also Sphinkydoc tries to address the problem that no documentation should be 
written twice. This is why system also tries to look for magic files in your 
project, such as `INSTALL`, `README`, `COPYING`, which also contain bits for the 
documentation.

Licensed under rather permissive :ref:`FreeBSD license<LICENSE>`

Usage example
=============
Go to directory where you want the HTML documentation to appear, and run the 
main script :ref:`sphinkydoc.py`::

	$ sphinkydoc.py yourmodule 
	
It is usually good idea to create ``docs`` directory in your project directory.
This also enables the sphinkydoc script to find out the `README`, `COPYING`,
`INSTALL`, etc. magic files your project may have. The script looks the magic 
files by default from directory upwards from the execution directory, you can
also specify the directory of magic files.

Here is another example, executed inside ``docs`` directory of sphinkydoc 
project, this is used to generate documentation for Sphinkydoc itself::

	$ sphinkydoc.py -s"../src/sphinkydoc.py" examplepackage sphinkydocext
	
Little bit of explanation, `-s` means the next argument is some sort of 
script or executable, not necessarily Python script. Sphinkydoc tries to call your 
scripts using `--help` and generating documentation page according to that. 
You can read more about the main script :ref:`sphinkydoc.py from the 
documentation<sphinkydoc.py>`.


.. _Sphinx documentation generator: http://sphinx.pocoo.org/