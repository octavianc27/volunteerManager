# forms.py
from django import forms
from .models import Volunteer, Event, Participation
from django_select2.forms import Select2MultipleWidget


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
    volunteers = forms.ModelMultipleChoiceField(
        queryset=Volunteer.objects.order_by("last_name"),
        widget=Select2MultipleWidget(attrs={'data-maximum-selection-length': 100}),
        required=False)

    class Meta:
        model = Participation
        fields = ['volunteers', 'event', 'worked_hours', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Override the queryset for the participant field
        self.fields['event'].queryset = Event.objects.order_by('-end_date')

        # Make the dropdown searchable
        self.fields['volunteers'].widget.attrs['class'] = 'select2'
        self.fields['volunteers'].widget.attrs['multiple'] = 'multiple'
        self.fields['event'].widget.attrs['class'] = 'select2'


class VolunteerEditForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields = '__all__'
