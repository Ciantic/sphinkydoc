:mod:`{{ fullname }}`
==================================================

.. automodule:: {{ fullname }}

{% block modules %}
{% if all_modules %}	

.. rubric:: Submodules

.. sphinkydoc::
	:no-gen:
	:modules: {% for submodule in all_modules %}{{ fullname }}.{{ submodule }} {% endfor %}

{% endif %}
{% endblock %}