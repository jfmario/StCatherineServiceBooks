
{% for petition in petitions %}
Deacon/Priest: {{ petition.text }}

People/Choir: {% if 'response' in petition and petition.response %}{{ petition.response }}{% else %}Lord, have mercy.{% endif %}
{% endfor %}

{% if prayer %}
Priest: {{ prayer.text }}

People/Choir: Amen.
{% endif %}