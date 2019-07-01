from django import forms
from .models import Errata, ERRATA_RESOLUTIONS, ERRATA_STATUS, ERRATA_ERROR_TYPES, ERRATA_RESOURCES

class ErrataForm(forms.ModelForm):
    class Media:
        js = ('errata/errata-admin-ui.js', )


class ErrataModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ErrataModelForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

        self.fields['archived'].widget.attrs.update({'class': 'css-control-input'})

        # textareas
        self.fields['detail'].widget.attrs.update({'class': 'textarea_editor form-control', 'style': 'height:250px'})
        self.fields['resolution_notes'].widget.attrs.update({'class': 'textarea_editor form-control', 'style': 'height:250px'})
        self.fields['internal_notes'].widget.attrs.update({'class': 'textarea_editor form-control', 'style': 'height:250px'})

        # radio selects
        self.fields['status'].widget.attrs.update({'class': 'btn-group btn-group-toggle'})
        self.fields['resolution'].widget.attrs.update({'class': 'btn-group btn-group-toggle'})
        self.fields['error_type'].widget.attrs.update({'class': 'btn-group btn-group-toggle'})
        self.fields['resource'].widget.attrs.update({'class': 'btn-group btn-group-toggle'})

    duplicate_id = forms.CharField(help_text="Enter internal errata ID of duplicate.", required=False)
    resource_other = forms.CharField(required=False)
    error_type_other = forms.CharField(required=False)

    corrected_date = forms.CharField(widget=forms.TextInput(attrs={'type': 'date'}))
    resolution_date = forms.CharField(widget=forms.TextInput(attrs={'type': 'date'}))

    status = forms.ChoiceField(choices=ERRATA_STATUS, widget=forms.RadioSelect())
    resolution = forms.ChoiceField(choices=ERRATA_RESOLUTIONS, widget=forms.RadioSelect())
    error_type = forms.ChoiceField(choices=ERRATA_ERROR_TYPES, widget=forms.RadioSelect())
    resource = forms.ChoiceField(choices=ERRATA_RESOURCES, widget=forms.RadioSelect())

    def clean_duplicate_id(self):
        if self.cleaned_data['duplicate_id']:
            data = self.cleaned_data['duplicate_id']
            return Errata.objects.get(pk=data)

    class Meta:
        model = Errata
        #fields = '__all__'
        exclude = ['openstax_book', 'submitted_by', 'submitter_email_address']