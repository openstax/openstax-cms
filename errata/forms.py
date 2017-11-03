from django import forms


class ErrataForm(forms.ModelForm):
    class Media:
        js = ('errata-admin.js', )
