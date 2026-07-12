from django import forms

class ErrataForm(forms.ModelForm):
    class Media:
        js = ('errata/errata-admin-ui.js', )

    def add_post_render_callback(self):
        pass
