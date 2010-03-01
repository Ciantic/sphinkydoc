{{ module_split(fullname)|length * "~" }}
{{ module_split(fullname) }}
{{ module_split(fullname)|length * "~" }}
{# Every document has only *one* header, and I assume when I put it with over #}
{# ~~~~~ and under ~~~~~ I can pretty safely assume that *no* docstring does #}
{# that, so they cannot collide with H1 header. #}

.. automodule:: {{ fullname }}

{% if all_modules or members %}
Members
=======
{% endif %}

{% block modules %}
{% if all_modules %}

.. rubric:: Submodules	

.. sphinkydoc-modules::
	:maxdepth: 1
	{% for submodule in all_modules %}
	{{ fullname }}.{{ submodule }}
	{% endfor %}

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

{% block datas %}
{% if datas %}	

{# datas are confusing name, I decided to call them Attributes #}
.. rubric:: Data definitions

{% for data in datas %}
.. autodata:: {{ fullname }}.{{ data }}
{% endfor %}
{% endif %}
{% endblock %}


{% block functions %}
{% if functions %}
.. rubric:: Function definitions

{% for item in functions %}
.. autofunction:: {{ item }}
{%- endfor %}
{% endif %}
{% endblock %}


{% block classes %}
{% if classes %}

.. rubric:: Class definitions

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