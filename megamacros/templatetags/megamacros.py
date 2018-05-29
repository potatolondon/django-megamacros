import threading

from django import template
from django.template.base import token_kwargs

register = template.Library()


_DEFINE_TAG = "definecomponent"
_USE_TAG = "usecomponent"
_DEFINE_SLOT_TAG = "defineslot"
_USE_SLOT_TAG = "fillslot"


@register.simple_tag(takes_context=True)
def generate_id(context, prefix):
    """
        Usage: {% generate_id 'my-input' as new_id %}
        Returns: my-input-1

        IDs with the same prefix are sequential. The counters
        are stored in the root context so they are sequential across
        includes too.
    """

    COUNTER_KEY = "__id_counters"

    # Use a thread-local as we're manipulating the root context
    # and not using context.render_context (this may not be necessary
    # but I don't want to deal with debugging it if it is!)
    builtins_dict = context.dicts[0]
    if COUNTER_KEY not in builtins_dict:
        builtins_dict[COUNTER_KEY] = threading.local()

    if not hasattr(builtins_dict[COUNTER_KEY], "dict"):
        builtins_dict[COUNTER_KEY].dict = {}

    counter_dict = builtins_dict[COUNTER_KEY].dict

    if prefix not in counter_dict:
        counter_dict[prefix] = 0

    counter_dict[prefix] += 1

    return "{}-{}".format(prefix, counter_dict[prefix])


@register.tag(name=_DEFINE_TAG)
def define_component(parser, token):
    return _get_node(parser, token)


@register.tag(name=_USE_TAG)
def use_component(parser, token):
    return _get_node(parser, token)


def _get_node(parser, token):
    tag_name, component_name, c_kwargs = parse_macro_params(parser, token)
    nodelist = parser.parse(('end{}'.format(tag_name),))
    parser.delete_first_token()
    if tag_name == _DEFINE_TAG:
        return DefineComponent(nodelist, component_name, c_kwargs)
    elif tag_name == _USE_TAG:
        return UseComponent(nodelist, component_name, c_kwargs)


class ComponentException(Exception):
    pass


class ComponentNode(object):
    def resolve_kwargs(self, context):
        # add kwargs
        to_update = {}
        for k, v in self.kwargs.items():
            try:
                to_update[k] = v.resolve(context)
            except template.VariableDoesNotExist:
                # If a variable doesn't exist, render nothing
                to_update[k] = None

        return to_update


class DefineComponent(ComponentNode, template.Node):
    context_key = '__components'

    def __init__(self, nodelist, component_name, kwargs):
        self.nodelist = nodelist
        self.component_name = component_name
        self.kwargs = kwargs or {}

        # Get the child slot nodes
        self.child_slots = self._locate_child_slots(nodelist)

    def _locate_child_slots(self, nodelist):
        # get_nodes_by_type is recursive
        return nodelist.get_nodes_by_type(DefineSlot)

    def add_component(self, context):
        # A bit hacky, but we want components to be global so we
        # store them in the root context dict (which is where builtins like True and False are)
        builtins_dict = context.dicts[0]

        if self.context_key not in builtins_dict:
            builtins_dict[self.context_key] = {}

        builtins_dict[self.context_key][self.component_name] = {
            'name': self.component_name,
            'nodelist': self.nodelist,
            'context': self.resolve_kwargs(context),  # Store the added context from this component
            'slots': {x.name: x for x in self.child_slots}
        }

    def render(self, context):
        self.add_component(context)
        return ''


class UseComponent(ComponentNode, template.Node):
    def __init__(self, nodelist, component_name, kwargs):
        self.nodelist = nodelist
        self.component_name = component_name
        self.kwargs = kwargs or {}

        # Get the child slot nodes
        self.child_slots = [x for x in nodelist if isinstance(x, UseSlot)]

    def get_component(self, context):
        try:
            return context[DefineComponent.context_key][self.component_name]
        except KeyError:
            raise ComponentException("No such component: {}".format(self.component_name))

    def render(self, context):
        component = self.get_component(context)

        for slot in self.child_slots:
            if slot.name not in component['slots']:
                raise ComponentException("Unexpected slot: {} for {}".format(slot.name, self.component_name))

        defined_context = component['context'].copy()
        defined_context.update(self.resolve_kwargs(context))

        content_added = False
        try:
            # Update the context with stuff passed into define_component
            context.update(defined_context)

            # Add the entire context of the usecomponent block for the simple non-slot
            # case
            if not component.get('slots'):
                content_added = True
                new_context = {
                    "content": self.nodelist.render(context),

                    # Add an extraparams context for all things passed in usecomponent that weren't
                    # defined in definecomponent
                    "extraparams": [
                        (k, context[k]) for k in self.kwargs if k not in component['context']
                    ]
                }

                def attrify(value):
                    return value.replace("_", "-").lower()

                # Manipulated version of the extraparams for use in HTML attributes
                new_context["extraattrs"] = [(attrify(k), v) for k, v in new_context["extraparams"]]
                context.update(new_context)

            for slot in self.child_slots:
                context["__slot_{}_content".format(slot.name)] = slot.render(context)

            # Finally render the defined component with the context
            return component['nodelist'].render(context)
        finally:
            if content_added:
                context.pop()
            context.pop()


class DefineSlot(template.Node):
    def __init__(self, slot_name, nodelist):
        self.name = slot_name
        self.nodelist = nodelist

    def render(self, context):
        """
            This is confusing... You'd think defineslot wouldn't need to render
            anything, but actually we need to know *where* to render the content from
            the {% slot X %} tag so the usecomponent tag searches for child slots, renders
            the content from each {% slot %} tag, puts it in the context, and then renders
            the defined component, which renders defineslot, and then we use the stored content.

            Madness.
        """
        try:
            return context["__slot_{}_content".format(self.name)]
        except KeyError:
            return self.nodelist.render(context)


@register.tag(name=_DEFINE_SLOT_TAG)
def define_slot(parser, token):
    try:
        tag_name, slot_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires a single argument" % token.contents.split()[0]
        )

    nodelist = parser.parse(('end{}'.format(_DEFINE_SLOT_TAG),))
    parser.delete_first_token()
    return DefineSlot(slot_name, nodelist)


class UseSlot(template.Node):
    def __init__(self, slot_name, nodelist):
        self.name = slot_name
        self.nodelist = nodelist

    def render(self, context):
        return self.nodelist.render(context)


@register.tag(name=_USE_SLOT_TAG)
def use_slot(parser, token):
    try:
        tag_name, slot_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires a single argument" % token.contents.split()[0]
        )

    nodelist = parser.parse(('end{}'.format(_USE_SLOT_TAG),))
    parser.delete_first_token()
    return UseSlot(slot_name, nodelist)


def parse_macro_params(parser, token):
    """
    Common parsing logic for both use_macro and macro_block
    """
    try:
        bits = token.split_contents()
        tag_name, macro_name, values = bits[0], bits[1], bits[2:]
    except IndexError:
        raise template.TemplateSyntaxError(
            "{0} tag requires at least one argument (macro name)".format(
                token.contents.split()[0]))

    kwargs = token_kwargs(values, parser, False)

    return tag_name, macro_name, kwargs