from datetime import datetime

from django.db import models


# Create your models here.
class Volunteer(models.Model):
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=15, blank=True)

    is_member = models.BooleanField(default=True)
    is_active_member = models.BooleanField(default=True)

    adherence_date = models.DateField(default=datetime.today)

    BACHELORS = 'Bachelors'
    MASTERS = 'Masters'
    PHD = 'PhD'

    EDUCATION_CHOICES = [
        (BACHELORS, 'Bachelors'),
        (MASTERS, 'Masters'),
        (PHD, 'PhD'),
    ]

    education_level = models.CharField(
        max_length=20,
        choices=EDUCATION_CHOICES,
        default=BACHELORS,
    )

    education_year = models.PositiveSmallIntegerField()

    last_active_date = models.DateField(null=True, blank=True)

    DEPARTMENT_IT = 'IT'
    DEPARTMENT_HR = 'HR'
    DEPARTMENT_PR = 'PR'
    DEPARTMENT_FINANCE = 'FINANCE'

    DEPARTMENT_CHOICES = [
        (DEPARTMENT_IT, 'IT'),
        (DEPARTMENT_HR, 'HR'),
        (DEPARTMENT_PR, 'PR'),
        (DEPARTMENT_FINANCE, 'FINANCE'),
    ]

    department = models.CharField(
        max_length=50,
        choices=DEPARTMENT_CHOICES,
        blank=True,
    )

    def update_last_active_date(self):
        # Get the latest participation date for the volunteer
        latest_participation = self.participation_set.order_by('-event__start_date').first()

        if latest_participation:
            self.last_active_date = latest_participation.event.end_date
            self.save()

    def __str__(self):
        return f'{self.last_name} {self.first_name}'


class Event(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    start_date = models.DateField(default=datetime.today)
    end_date = models.DateField(default=datetime.today)
    done_reporting = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name}'


class Participation(models.Model):
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    worked_hours = models.PositiveSmallIntegerField()
    notes = models.TextField()

    def __str__(self):
        return f'{self.volunteer} {self.event}'
