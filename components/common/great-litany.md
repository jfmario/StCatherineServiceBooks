---
data: data
---

## Enarxis

Priest:  Blessed is the Kingdom of the Father and of the Son and of the Holy Spirit, now and ever and unto ages of ages.

People/Choir: Amen

## The Litany of Peace

{% with petitions=ref('great-litany', 'petitions'), prayer=ref('great-litany', 'prayer') %}
{% include '_includes/litany.md' %}
{% endwith %}