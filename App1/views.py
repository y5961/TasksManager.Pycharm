from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from App1.forms import SignUpForm, SignInForm, AddTeamForm, JoinTeamForm, AddTaskForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth import get_user_model
from App1.models import Team, Task, User
from django.db import transaction
from django.core.exceptions import PermissionDenied


# Create your views here.
def home(request):
    return render(request, 'home.html')


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
        form = AddTeamForm(request.POST)
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
        form = AddTeamForm()
    return render(request, 'teams/manage/create_team.html', {'form': form})


def team_management(request):
    tasks = Task.objects.filter(team=request.user.team)
    team = request.user.team
    status_filter = request.GET.get('status')
    if status_filter: tasks = tasks.filter(status=status_filter)

    now = timezone.now().date()

    for task in tasks:
        if task.end_date < now and task.status != 'EXPIRED' and task.status != 'DONE':
                task.status = 'EXPIRED'
                task.save()

    query = request.GET.get('q')  # כאן אנחנו תופסים את מה שהמשתמש כתב


    if query:
            # מסנן לפי שם פרטי או שם משפחה של המבצע
        tasks = tasks.filter(owner__first_name__icontains=query)

    context = {
        'tasks': tasks,
        'team': team,
        'users': User.objects.filter(team=team),
    }

    return render(request, 'teams/team_management.html', context)


def assign_tasks(request):
    return render(request, 'teams/manage/assign_tasks.html')


@login_required
def add_task(request):
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


@login_required
def delete_task(request, task_id):
    if request.user.role != 'Manager':
        raise PermissionDenied

    if request.method == 'POST':
        task = Task.objects.get(id=task_id)
        task.delete()
        return redirect('team_management')

# return render(request, 'teams/manage/add_task.html')
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.user.role != 'Manager':
        raise PermissionDenied
    if request.method == 'POST':
        form = AddTaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('team_management')
    else:
        form = AddTaskForm(instance=task)

    return render(request, 'teams/manage/add_task.html', {
        'form': form,
        'is_edit': True  # עוזר לנו לשנות את הכותרת ב-HTML במידת הצורך
    })


@login_required
def update_owner(request, task_id):

    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id, team=request.user.team)
        new_owner_id = request.POST.get('user_id')
        if new_owner_id:
            new_owner = get_object_or_404(User, id=new_owner_id)
            task.owner = new_owner
            task.status = "ON_PROCESS"
            task.save()


        return redirect('team_management')

    return redirect('team_management')

@login_required
def update_status(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id, team=request.user.team)
        new_owner_id = request.POST.get('user_id')
        if new_owner_id:
            task.status = "DONE"
            task.save()
        return redirect('team_management')
    return redirect('team_management')

