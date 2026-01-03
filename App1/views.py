from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from App1.forms import SignUpForm, SignInForm, AddTeamForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth import get_user_model
from App1.models import Team


# Create your views here.
def home(request):
    return render(request,'home.html')


def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user_data = form.cleaned_data
            request.session['temp_user_data'] = user_data
            if user_data['role'] == 'Manager':
                return redirect('create_team')
            return redirect('register_final')
    else:
        form = SignUpForm()
    return render(request, 'SignUp.html', {'form': form})


def sign_in(request):
    if request.method == 'POST':
        # 1. יצירת הטופס עם הנתונים שהמשתמש הזין
        form = AuthenticationForm(request, data=request.POST)

        # 2. Django בודק כאן אם השדות מלאים ואם המשתמש קיים במערכת
        if form.is_valid():
            # 3. במקום authenticate ידני, הטופס כבר מצא את המשתמש עבורנו!
            user = form.get_user()
            login(request, user)
            print("Success1 - המשתמש אומת ומתבצע ניתוב")
            return redirect('home')
        else:
            print("שגיאה: פרטי התחברות לא נכונים")
            print(form.errors)
    else:
        form = AuthenticationForm()
        form.fields['username'].label = "Email"

    return render(request, 'SignIn.html', {'form': form})

def create_team(request):
    User = get_user_model()
    user_data = request.session['temp_user_data']

    if not user_data:
        return redirect('sign_up')
    if request.method == 'POST':
        form=AddTeamForm(request.POST)
        if form.is_valid():
            team_name = form.cleaned_data['name']

            if Team.objects.filter(name=team_name).exists():
                form.add_error('name', 'שם הקבוצה כבר תפוס.')
            else:
                new_team = Team.objects.create(name=team_name)
                user = User.objects.create_user(
                    username=user_data['email'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    role=user_data['role'],
                    team=new_team
                )
                del request.session['temp_user_data']
                login(request, user)
                return redirect('team_management')
    else:
        form=AddTeamForm()
    return render(request, 'create_team.html', {'form': form})


