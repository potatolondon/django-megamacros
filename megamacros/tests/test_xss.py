from django.test import TestCase
from django.template import Template, Context


def render(template, context):
    t = Template(template)
    return t.render(context)


class XSSTests(TestCase):

    def test_use_component_doesnt_allow_xss(self):

        TEMPLATE = "" \
            "{% load megamacros %}" \
            "{% definecomponent xss_test %}" \
            "<div>" \
            "{% defineslot slot1 %}{% enddefineslot %}" \
            "</div>" \
            "{% enddefinecomponent %}" \
            "{% usecomponent xss_test %}" \
            "{% fillslot slot1 %}{{somevar}}{% endfillslot %}" \
            "{% endusecomponent %}"


        ctx = {
            "somevar": "<script>alert(0);</script>"
        }

        content = render(TEMPLATE, Context(ctx))

        self.assertEqual(content, "<div>&lt;script&gt;alert(0);&lt;/script&gt;</div>")