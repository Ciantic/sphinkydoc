{% extends "sphinkydoc/script.rst" %}
{# Python that has optparser #}
{% block content %}

.. program-usage:: {{ optparser.get_usage() }}

.. program:: {{ script_name }}

{{ optparser.get_description() }}

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