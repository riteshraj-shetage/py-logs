from django import forms
from .models import Tenant
from django.utils.text import slugify


class OrganizationRegistrationForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['name', 'plan']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Organization name'}),
            'plan': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        slug = slugify(name)
        if Tenant.objects.filter(slug=slug).exists():
            raise forms.ValidationError('An organization with this name already exists.')
        return name
