# forms.py
from django import forms
from .models import Volunteer, Event, Participation


class VolunteerForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['adherence_date'].widget.attrs['class'] = 'datepicker'


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_date'].widget.attrs['class'] = 'datepicker'
        self.fields['end_date'].widget.attrs['class'] = 'datepicker'


class ParticipationForm(forms.ModelForm):
    class Meta:
        model = Participation
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Override the queryset for the participant field
        self.fields['volunteer'].queryset = Volunteer.objects.order_by('last_name')
        self.fields['event'].queryset = Event.objects.order_by('-end_date')

        # Make the dropdown searchable
        self.fields['volunteer'].widget.attrs['class'] = 'select2'
        self.fields['event'].widget.attrs['class'] = 'select2'


class VolunteerEditForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields = '__all__'
