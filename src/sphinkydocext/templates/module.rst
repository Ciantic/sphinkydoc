:mod:`{{ fullname }}`
========================

.. automodule:: {{ fullname }}

{% block modules %}
{% if all_modules %}	

.. rubric:: Submodules

.. sphinkydoc::
	:modules: {% for submodule in all_modules %}{{ fullname }}.{{ submodule }} {% endfor %}


{% for submodule in all_modules %}{{ submodule }} {% endfor %}
{% endif %}
{% endblock %}