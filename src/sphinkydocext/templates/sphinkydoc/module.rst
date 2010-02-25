{{ module_split(fullname) }}
{{ module_split(fullname)|length*"=" }}

.. automodule:: {{ fullname }}

{% block modules %}
{% if all_modules %}	

.. rubric:: Submodules

.. sphinkydoc::
	:no-gen:
	:modules: {% for submodule in all_modules %}{{ fullname }}.{{ submodule }} {% endfor %}

{% endif %}
{% endblock %}

{% block members %}
{% if members %}
.. rubric:: Members

.. autosummary::
	:nosignatures:
	
	{% for item in members %}
	{{ item }}
	{% endfor %}
{% endif %}
{% endblock %}

{% block attributes %}
{% if attributes %}	
.. rubric:: Attributes

{% for attr in attributes %}
.. autoattribute:: {{ fullname }}.{{ attr }}
{% endfor %}
{% endif %}
{% endblock %}


{% block datas %}
{% if datas %}	
.. rubric:: Attributes

{% for data in datas %}
.. autodata:: {{ fullname }}.{{ data }}
{% endfor %}
{% endif %}
{% endblock %}


{% block functions %}
{% if functions %}
.. rubric:: Functions

{% for item in functions %}
.. autofunction:: {{ item }}
{%- endfor %}
{% endif %}
{% endblock %}


{% block classes %}
{% if classes %}

.. rubric:: Classes

{% for item in classes %}
.. autoclass:: {{ item }}()
	:members:
	:show-inheritance:
{%- endfor %}
{% endif %}
{% endblock %}


{% block exceptions %}
{% if exceptions %}
.. rubric:: Exceptions
    
{% for item in exceptions %}
.. autoexception:: {{ item }}
{%- endfor %}
{% endif %}
{% endblock %}