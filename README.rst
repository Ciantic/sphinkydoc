Sphinkydoc |release|
====================

This is `Sphinx documentation generator`_ helper script and extension. Main purpose
is to leverage the power of Sphinx for small Python projects. For those it is 
usually sufficient to document the code in docstrings.

Also Sphinkydoc tries to address the problem that no documentation should be 
written twice. This is why system also tries to look for magic files, such as
INSTALL, README, COPYING, which also contain bits for the documentation.

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
	
Little bit of explanation, :opt:`-s` means the next argument is some sort of 
script or executable, not necessarily Python script. Sphinkydoc tries to call your 
scripts using ``--help`` and generating documentation page according to that. 
You can read more about :ref:`sphinkydoc.py` in the documentation.

.. _Sphinx documentation generator: http://sphinx.pocoo.org/