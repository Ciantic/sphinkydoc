.. include:: ../../README.rst

Documentation
=============
  
{% if scripts %}
.. rubric:: Scripts and executables

.. sphinkydoc::
	:scripts: {% for script in scripts %}"{{ script }}" {% endfor %}
{% endif %}


{% if modules %}
.. rubric:: Modules and packages

.. sphinkydoc::
	:modules: {% for module in modules %}{{ module }} {% endfor %}
{% endif %}




.. rubric:: About

.. toctree::
   :maxdepth: 2

   copying
   glossary
