from django import forms
from .models import User, Team, Task


class SignUpForm(forms.ModelForm):
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'role']
        labels = {
            'first_name': 'First name',
            'last_name': 'Last name',
        }
        help_texts = {
            "password": "Min length of 8 characters",
            "email": "Email address",
            "first_name": "Only letters",
            "last_name": "Only letters",
            "role": "To open a new team - choose 'Manager'",
        }

    def clean_first_name(self):
        fname = self.cleaned_data["first_name"]
        if not fname.isalpha():
            raise forms.ValidationError("Should contain only letters")
        return fname

    def clean_last_name(self):
        lname = self.cleaned_data["last_name"]
        if not lname.isalpha():
            raise forms.ValidationError("Should contain only letters")
        return lname


class SignInForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'password']
        help_texts = {
            "password": "Min length of 8 characters",
            "email": "Email address",
        }


class AddTeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name']
        labels = {'name': 'Name of the new team'}


class JoinTeamForm(forms.ModelForm):
    team = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        label="Select a team",
        empty_label="-- Choose team to join --",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['team']  # הגדרה יחידה ותקינה של Meta


class AddTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'end_date']
        labels = {
            'name': 'Task name',
            'description': 'Task description',
        }
        help_texts = {
            'name': 'Enter a concise name for the task.',
            'description': 'Provide a detailed explanation of what needs to be done.',
            'end_date': 'Select the final deadline for this task.',
        }
        widgets = {
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


