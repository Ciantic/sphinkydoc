{% extends "sphinkydoc/script.rst" %}
{# Python that has optparser #}
{% block content %}

.. program:: {{ script_name }}

{{ optparser.usage }}

{# Non groupped options #}
{% for opt in optparser.option_list %}

{{ cmdoption(opt) }}
	
{% endfor %}


{# Groupped options, TODO: Not implemented #}
{% for grp in optparser.option_groups %}
	Grouppe!
	{{ grp.title }}
{% endfor %}

{% endblock %}