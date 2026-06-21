
## The Little Doxology

{% for verse in ref('little-doxology', 'verses') %}
- {{ verse }}
{%- endfor %}