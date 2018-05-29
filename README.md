# Django Megamacros

Template macros for Django's templating language.

## Overview

megamacros is a set of templatetags which allows you define reusable chunks of 
HTML in Django templates which can be customised when used. These reusable chunks
are called "components". 

When you instantiate a component you can customise the instantiation in two ways:

 - Via keyword arguments passed into the `{% usecomponent %}` tag.
 - By filling in "slots" which are defined when the component is defined.
 
Components can use other components allowing you to rapidly generate a library of components
for your website.


## Examples

Imagine that you are defining a set of form components using a custom style guide, you could potentially
define a button component like this:

```
{% definecomponent button flat=False cta=False %}
<div class="input-field">
    <button class="btn {% if flat %}btn-flat {% endif %}{% if cta %}btn-primary{% endif %}">
    {% defineslot button_content %}Click me!{% enddefineslot %}
    </button>
</div>
{% enddefinecomponent %}
```

You could then put this component in a shared include, and use it in various ways:

```
{% include "buttons.html" %}

{% usecomponent button flat=True %}{% endusecomponent %}
{% usecomponent button cta=True flat=True %}{% endusecomponent %}
{% usecomponent button cta=True flat=True %}
    {% fillslot button_content %}Some replacement text {% endfillslot %}
{% endusecomponent %}
```

For those occasions when there will only ever be one slot defined in a component you can use a 
simplified definition which uses the 'content' placeholder:

```
{% definecomponent button %}
<button>{{content}}</button>
{% enddefinecomponent %}

...

{% usecomponent button %}My content{% endusecomponent %}
```

## Running Tests

If you'd like to contribute to megamacros you can run the tests as follows:

 - Set up a virtualenv, and pip install django
 - cd to the "tests" folder
 - Run `python runtests.py`