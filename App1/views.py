from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from App1.forms import SignUpForm, SignInForm, AddTeamForm, JoinTeamForm, AddTaskForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth import get_user_model
from App1.models import Team, Task
from django.db import transaction
from django.core.exceptions import PermissionDenied

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

            return redirect('select_team')
    else:
        form = SignUpForm()
    return render(request, 'auth/sign_up.html', {'form': form})


def sign_in(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            print("Success1 - המשתמש אומת ומתבצע ניתוב")
            return redirect('team_management')
        else:
            print("שגיאה: פרטי התחברות לא נכונים")
            print(form.errors)
    else:
        form = AuthenticationForm()
        form.fields['username'].label = "Email"

    return render(request, 'auth/sign_in.html', {'form': form})
def select_team(request):
    User = get_user_model()
    # 1. שליפת הנתונים מהסשן כבר בהתחלה
    user_data = request.session.get('temp_user_data')

    # 2. הגנה: אם המשתמש הגיע לדף בלי לעבור ב-Sign Up
    if not user_data:
        return redirect('sign_up')

    if request.method == 'POST':
        form = JoinTeamForm(request.POST)
        if form.is_valid():
            try:
                selected_team = form.cleaned_data['team']

                with transaction.atomic():
                    if User.objects.filter(email=user_data['email']).exists():
                        form.add_error(None, "משתמש עם אימייל זה כבר נרשם במערכת")
                        return render(request, 'teams/select_team.html', {'form': form})

                    user = User.objects.create_user(
                        username=user_data['email'],
                        email=user_data['email'],
                        password=user_data['password'],
                        first_name=user_data.get('first_name', ''),
                        last_name=user_data.get('last_name', ''),
                        role=user_data.get('role'),
                        team=selected_team
                    )

                    request.session.pop('temp_user_data', None)
                    login(request, user)

                    return redirect('team_management')  # ודאי שזה תואם לשם ה-URL שלך

            except Exception as e:
                form.add_error(None, f"אירעה שגיאה בתהליך הרישום: {str(e)}")
    else:
        # טעינת טופס ריק במידה וזה GET
        form = JoinTeamForm()

    return render(request, 'teams/select_team.html', {'form': form})


def create_team(request):
    User = get_user_model()
    user_data = request.session['temp_user_data']

    if not user_data:
        return redirect('sign_up')
    if request.method == 'POST':
        form=AddTeamForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                  team_name = form.cleaned_data['name']

                if Team.objects.filter(name=team_name).exists():
                    form.add_error('name', 'This team name already exists')
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
            except Exception as e:
                # אם קרתה תקלה כלשהי, שום דבר לא יישמר ב-DB
                form.add_error(None, "error, try again!!")
    else:
        form=AddTeamForm()
    return render(request, 'teams/manage/create_team.html', {'form': form})

def team_management(request):
    tasks = Task.objects.filter(team=request.user.team)
    return render(request, 'teams/team_management.html', {'tasks': tasks})


def assign_tasks(request):
    return render(request, 'teams/manage/assign_tasks.html')

@login_required
def add_task(request):
    # בדיקה האם המשתמש הוא מנהל
    if request.user.role != 'Manager':
        raise PermissionDenied

    if request.method == 'POST':
        form = AddTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)

            task.team = request.user.team
            task.save()
            return redirect('team_management')
    else:
        form = AddTaskForm()

    return render(request, 'teams/manage/add_task.html', {'form': form})


# return render(request, 'teams/manage/add_task.html')


"""
def create_team(request):
    User = get_user_model()
    user_data = request.session.get('temp_user_data')

    if not user_data:
        return redirect('sign_up')

    if request.method == 'POST':
        form = AddTeamForm(request.POST)
        if form.is_valid():
            try:
                # ההזחה מתחילה כאן - כל מה שקורה בתוך הבלוק הזה הוא יחידה אחת
                with transaction.atomic():
                    team_name = form.cleaned_data['name']

                    if Team.objects.filter(name=team_name).exists():
                        form.add_error('name', 'This team name already exists')
                        # כאן לא צריך raise כי אנחנו רוצים לחזור לטופס עם השגיאה
                    else:
                        # 1. יצירת הקבוצה
                        new_team = Team.objects.create(name=team_name)

                        # 2. יצירת המשתמש ושיוכו לקבוצה החדשה
                        user = User.objects.create_user(
                            username=user_data['email'],
                            email=user_data['email'],
                            password=user_data['password'],
                            first_name=user_data['first_name'],
                            last_name=user_data['last_name'],
                            role=user_data['role'],
                            team=new_team
                        )

                        # 3. ניקוי הסשן וביצוע התחברות
                        del request.session['temp_user_data']
                        login(request, user)

                        return redirect('team_management')

            except Exception as e:
                # אם משהו השתבש בתוך ה-atomic, נגיע לכאן
                print(f"Error during team/user creation: {e}")
                form.add_error(None, "An error occurred, please try again.")
    else:
        form = AddTeamForm()

    return render(request, 'create_team.html', {'form': form})
    """
# def select_team(request):
#     if request.method == 'POST':
#         form = JoinTeamForm(request.POST)
#         if form.is_valid():
#             selected_team = form.cleaned_data['team']
#             # כאן את שומרת את הקבוצה שנבחרה בסשן או יוצרת את המשתמש
#             user_data = request.session.get('temp_user_data')
#             if user_data:
#                 User = get_user_model()
#                 user = User.objects.create_user(
#                     username=user_data['email'],
#                     email=user_data['email'],
#                     password=user_data['password'],
#                     first_name=user_data['first_name'],
#                     last_name=user_data['last_name'],
#                     role=user_data['role'],
#                     team=selected_team
#                 )
#                 login(request, user)
#                 del request.session['temp_user_data']
#                 return redirect('home')
#     else:
#         form = JoinTeamForm()
#
#     return render(request, 'select_team.html', {'form': form})
