from django.test import TestCase
from django.template import Template, Context


FAKE_COMPONENT = """
{% load megamacros %}
{% definecomponent button flat=False cta=False %}
<div class="input-field">
<button class="btn {% if flat %}btn-flat{% endif %} {% if cta %}btn-primary{% endif %}">
{% defineslot button_content %}Click me!{% enddefineslot %}
</button>
</div>
{% enddefinecomponent %}
"""


def render(template, context):
    t = Template(template)
    return t.render(Context(context))


class UsageTests(TestCase):
    def test_basic_usage(self):
        TEMPLATE = "%s\n" \
            "{%% usecomponent button flat=True %%}{%% endusecomponent %%}" % (FAKE_COMPONENT,)

        content = render(TEMPLATE, {}).replace("\n", "")

        self.assertEqual(content, '<div class="input-field"><button class="btn btn-flat ">Click me!</button></div>')

    def test_override_slot(self):

        TEMPLATE = "%s\n" \
            "{%% usecomponent button flat=True %%}" \
            "{%% fillslot button_content %%}test{%% endfillslot %%}" \
            "{%% endusecomponent %%}" % (FAKE_COMPONENT,)

        content = render(TEMPLATE, {}).replace("\n", "")

        self.assertEqual(content, '<div class="input-field"><button class="btn btn-flat ">test</button></div>')