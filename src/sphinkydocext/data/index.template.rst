.. include:: ../../README.rst

Documentation
=============

{% if modules %}
.. rubric:: Modules and packages

.. sphinkydoc::
	:modules: {% for module in modules %}{{ module }} {% endfor %}
{% endif %}

  
{% if scripts %}
.. rubric:: Scripts

.. sphinkydoc::
	:scripts: sphinkydoc.py second.py "third script.py"
{% endif %}


.. toctree::
   :maxdepth: 2

   copying
