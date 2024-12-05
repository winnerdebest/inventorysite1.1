# myapp/forms.py
from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from .models import Purchase

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        empty_label="Select Role",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "group"]
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            user.groups.add(self.cleaned_data["group"])  # Assign the user to the selected group
        return user




class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['vendor', 'quantity_received']  # Adjust fields as necessary
