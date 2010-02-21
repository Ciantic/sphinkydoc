Sphinkydoc |version|
====================

This is Sphinx documentation generator helper script and extension. Main purpose
is to leverage Sphinx power for small Python projects. Similar idea as in EpyDoc
where all documentation is embedded in docstrings.

Licensed under FreeBSD license, see :ref:`COPYING`.

Usage example
=============
Go to directory where you want the HTML documentation to appear, and run the 
main script `sphinkydoc.py`:

::

	$ sphinkydoc.py yourmodule 
	
It is usually good idea to create ``docs`` directory in your project directory.
This also enables the sphinkydoc script to find out the `README`, `COPYING`,
`INSTALL` magic files your project may have.

