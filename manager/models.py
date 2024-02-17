from datetime import datetime

from django.db import models


# Create your models here.
class Volunteer(models.Model):
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    email = models.EmailField()
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

    def update_last_active_date(self):
        # Get the latest participation date for the volunteer
        latest_participation = self.participation_set.order_by('-date').first()

        if latest_participation:
            self.last_active_date = latest_participation.date
            self.save()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Event(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    start_date = models.DateField(default=datetime.today)
    end_date = models.DateField(default=datetime.today)

    def __str__(self):
        return f'{self.name}'


class Participation(models.Model):
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.today)
    worked_hours = models.PositiveSmallIntegerField()
    notes = models.TextField()

    def __str__(self):
        return f'{self.volunteer} {self.event} {self.date}'

