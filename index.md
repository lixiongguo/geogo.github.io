---
layout: default
---
{%- assign preface = site.posts | where: "title", "曲面展开前言" | first -%}
{%- if preface -%}
  <meta http-equiv="refresh" content="0; url={{ preface.url | relative_url }}">
  <script>location.href = "{{ preface.url | relative_url }}";</script>
{%- else -%}
  {%- include home.html -%}
{%- endif -%}