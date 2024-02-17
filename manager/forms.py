# forms.py
from django import forms
from .models import Volunteer, Event, Participation


class VolunteerForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields = '__all__'


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'


class ParticipationForm(forms.ModelForm):
    class Meta:
        model = Participation
        fields = '__all__'


class VolunteerEditForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields = '__all__'