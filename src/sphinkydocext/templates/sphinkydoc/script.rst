{% block head %}
.. _{{ script_name }}:

{{ script_name|length * "~" }}
{{ script_name }}
{{ script_name|length * "~" }}
{% endblock %}

{% block content %}
{% if help %}
::

{{ indent(4, help) }}
{% endif %}
{% endblock %}