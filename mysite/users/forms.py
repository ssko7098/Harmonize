import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(max_length=255, help_text="Required add a valid email address.")

    class Meta:
        model = User
        fields = ("full_name", "username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.full_name = self.cleaned_data['full_name']
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username']
        if commit:
            user.save()
        return user

    def clean_email(self):
        email = self.cleaned_data["email"].lower()

        # simple uni email validation
        try:
            pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.fullmatch(pattern, email):
                raise forms.ValidationError(("Please provide a valid email"))
        except Exception:
            raise forms.ValidationError(("Please provide a valid email"))

        # email uniqueness verification
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:  # Model-level exception
            return email
        raise forms.ValidationError(("A user with that email already exists."))

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(("The two password fields didn't match."))
        return password2

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar_url']  # Fields to allow editing

    def save(self, commit=True):
        profile = super(ProfileForm, self).save(commit=False)
        if commit:
            profile.save()
        return profile