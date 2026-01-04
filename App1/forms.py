from django import forms
from .models import User, Team


class SignUpForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'role']
        labels= {
        'first_name': 'first name',
        'last_name': 'last name',
               }
        help_texts = {
            "password": "min length of 8 characters",
            "email": "email address",
            "first_name": "only letters",
            "last_name": "only letters",
            "role": "To open a new team- choose a 'manager'",
        }

    def clean_first_name(self):
        fname = self.cleaned_data["first_name"]
        if not fname.isalpha():
            raise forms.ValidationError("Should contains only letters")
        return fname

    def clean_last_name(self):
        lname=self.cleaned_data["last_name"]
        if not lname.isalpha():
            raise forms.ValidationError("Should contains only letters")
        return lname

class SignInForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [ 'email', 'password']
        help_texts = {
            "password": "min length of 8 characters",
            "email": "email address",
        }

class AddTeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name']
        labels = {'name': 'name of the new team'}


#class JoinTeamForm(forms.ModelForm):
#   team = forms.ModelChoiceField(queryset=Team.objects.all(), label="select team")

class JoinTeamForm(forms.ModelForm):
    team = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        label="select a team",
        empty_label="--choose teem to join",
        widget=forms.Select(attrs={'class':'form-control'})
    )
    class Meta:
        model = User
        fields = ['team']