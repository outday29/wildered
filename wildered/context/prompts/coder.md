I am writing a Python project and I need your help as a code assistant.
Below are the functions or classes that I am working on:

```python
{{ code_context }}
```

Below are the tasks you need to accomplish:
'''
{{ requirement }}
'''

{%- if additional_context|length > 0 %}
{{ additional_context }}
{% endif -%}

{%- if manual == False %}
Do not change functions that you are not told to implement or modify.
Most importantly, return only Python code, nothing but the Python code. No explanation needed.
{% endif %}

Your answer should only have the functions or class that you are told to implement. Do not repeat other code in your answer