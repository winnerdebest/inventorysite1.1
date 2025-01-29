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
    
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already in use.")
        return email

    def clean_group(self):
        group = self.cleaned_data.get("group")
        if not group:
            raise forms.ValidationError("Please select a role.")
        return group

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
