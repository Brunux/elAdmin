from django import forms


class TablerFormMixin:
    """Adds Tabler CSS classes to all form widgets automatically."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.TextInput, forms.EmailInput, forms.NumberInput,
                                   forms.URLInput, forms.PasswordInput, forms.DateInput,
                                   forms.DateTimeInput, forms.TimeInput, forms.Textarea)):
                widget.attrs.setdefault('class', 'form-control')
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault('class', 'form-select')
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault('class', 'form-check-input')
