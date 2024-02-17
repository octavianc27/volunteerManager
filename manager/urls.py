from django.urls import path

from . import views
from .views import add_volunteer, view_volunteer, events_list, view_event, add_event, delete_event, add_participation, \
    edit_volunteer, edit_event, generate_report

urlpatterns = [
    path("", views.index, name="index"),
    path('add', add_volunteer, name='add_volunteer'),
    path('view_volunteer/<int:user_id>/', view_volunteer, name='view_volunteer'),
    path('edit_volunteer/<int:user_id>/', edit_volunteer, name='edit_volunteer'),

    path('events/', events_list, name='events_list'),
    path('events/add/', add_event, name='add_event'),
    path('events/<int:event_id>/', view_event, name='view_event'),
    path('events/<int:event_id>/delete/', delete_event, name='delete_event'),
    path('events/<int:event_id>/edit/', edit_event, name='edit_event'),

    path('add_participation/', add_participation, name='add_participation'),

    path('generate_report/<int:user_id>/', generate_report, name='generate_report'),
]
