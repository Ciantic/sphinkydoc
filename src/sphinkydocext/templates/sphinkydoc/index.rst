.. include:: README.inc

Documentation
=============

{% if topic_files %}
.. rubric:: Topics

.. toctree::
   {% for topic_file in topic_files %}
   {{ topic_file }}
   {% endfor %}
{% endif %}
  
  
{% if scripts %}
.. rubric:: Scripts and executables

.. sphinkydoc-scripts::
	{% for script in scripts %}
	{{ script }}
	{% endfor %}
{% endif %}


{% if modules %}
.. rubric:: Modules and packages

.. sphinkydoc-modules::
	:maxdepth: 2
	{% for module in modules %}
	{{ module }}
	{% endfor %}
{% endif %}


{% if about_files %}
.. rubric:: About

.. toctree::
   {% for about_file in about_files %}
   {{ about_file }}
   {% endfor %}
{% endif %}