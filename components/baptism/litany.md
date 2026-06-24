---
data: data
---

Priest:  Blessed is the Kingdom of the Father and of the Son and of the Holy Spirit, now and ever and unto ages of ages.

People/Choir: Amen

## Litany for Holy Baptism

{% with petitions=ref('baptism-litany', 'petitions'), prayer=None %}
{% include '_includes/litany.md' %}
{% endwith %}
