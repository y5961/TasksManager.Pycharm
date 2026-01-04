from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
from django.core.validators import MinLengthValidator


class User(AbstractUser):
    role = models.CharField(choices=[("Manager","Manager"),("TeamMember","TeamMember")])
    team = models.ForeignKey("Team", on_delete=models.CASCADE, null=True)
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Team(models.Model):
    name = models.CharField(max_length=100,unique=True)
    def __str__(self):
        return self.name

def start_date_validator(value):
    if value < timezone.now().date():
        raise ValidationError("the date can not be in the past")

def end_date_validator(value):
    if value < timezone.now().date():
        raise ValidationError("please enter a future date")

class Task(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField(validators=[ start_date_validator])
    end_date = models.DateField(validators=[ end_date_validator])
    status = models.CharField(
        max_length=20,
        choices=[
            ("NEW_TASK", "New Task"),
            ("ON_PROCESS", "On Process"),
            ("DONE", "Done")
        ],
        default="NEW_TASK"
    )
    team = models.ForeignKey("Team", on_delete=models.CASCADE)
    owner = models.ForeignKey("User", on_delete=models.SET_NULL, null=True,blank=True)
    def clean(self):
        if self.start_date>self.end_date:
            raise ValidationError("End date cannot be earlier than start date")


    def __str__(self):
        return self.name


