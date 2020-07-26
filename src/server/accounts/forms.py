from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Profile


class SignupForm(forms.Form):
    first_name = forms.CharField(label=_('name'),
                                 max_length=30,
                                 widget=forms.TextInput(
                                     attrs={'placeholder':
                                                _('name'), }))
    phone = forms.CharField(label=_('Phone number'),
                            max_length=30,
                            widget=forms.TextInput(
                                attrs={'placeholder':
                                           _('Phone number'), }))

    def signup(self, request, user):
        user.name = self.cleaned_data['name']
        user.save()

        profile = Profile()
        profile.user = user
        profile.phone = self.cleaned_data['phone']
        profile.save()