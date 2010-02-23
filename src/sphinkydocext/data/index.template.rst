.. include:: README.rst


Documentation
=============

{% if topic_files(magic_files) %}
.. rubric:: Topics

.. toctree::
   :maxdepth: 2
   {% for topic_file in topic_files(magic_files) %}
   {{ topic_file }}
   {% endfor %}
{% endif %}
  
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


{% if about_files(magic_files) %}
.. rubric:: About

.. toctree::

   {% for about_file in about_files(magic_files) %}
   {{ about_file }}
   {% endfor %}
{% endif %}