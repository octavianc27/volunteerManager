from django.contrib import admin
from .models import Volunteer, Event, Participation


@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = (
    'last_name', 'first_name', 'email', 'phone_number', 'is_member', 'is_active_member', 'adherence_date',
    'education_level', 'education_year', 'last_active_date', 'department')
    list_filter = ('is_member', 'is_active_member', 'education_level', 'department')
    search_fields = ('last_name', 'first_name', 'email', 'phone_number', 'department')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', "done_reporting")
    list_filter = ("done_reporting",)
    search_fields = ('name', 'description')


@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('volunteer', 'event', 'worked_hours', 'notes')
    search_fields = ('volunteer__last_name', 'volunteer__first_name', 'event__name', 'notes')
