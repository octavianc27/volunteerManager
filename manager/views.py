# views.py
import base64
import calendar
import json
from datetime import datetime, timedelta
from io import BytesIO

from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Value
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from reportlab.lib.pagesizes import letter

from .forms import VolunteerForm, EventForm, ParticipationForm, VolunteerEditForm
from .models import Volunteer, Event, Participation

from reportlab.pdfgen import canvas

import matplotlib.pyplot as plt
from collections import Counter


@login_required
def volunteers_list(request):
    volunteers = Volunteer.objects.all()

    for volunteer in volunteers:
        volunteer.total_hours = Participation.objects.filter(volunteer=volunteer).aggregate(Sum('worked_hours'))[
                                    'worked_hours__sum'] or 0

    return render(request, 'volunteers_list.html', {'volunteers': volunteers})


@login_required
def add_volunteer(request):
    if request.method == 'POST':
        form = VolunteerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('volunteers_list')  # Redirect to a page displaying the list of volunteers
    else:
        form = VolunteerForm()

    return render(request, 'add_volunteer.html', {'form': form})


@login_required
def view_volunteer(request, user_id):
    volunteer = get_object_or_404(Volunteer, pk=user_id)
    participations = Participation.objects.filter(volunteer=volunteer)
    total_hours = participations.aggregate(Sum('worked_hours'))['worked_hours__sum'] or 0

    if request.method == 'POST' and 'delete' in request.POST:
        volunteer.delete()
        return redirect('/')

    if request.method == 'POST' and 'delete_participation' in request.POST:
        participation_id = request.POST.get('delete_participation')
        if participation_id:
            participation = get_object_or_404(Participation, pk=participation_id)
            participation.delete()
            return redirect('view_volunteer', user_id=user_id)

    return render(request, 'view_volunteer.html',
                  {'volunteer': volunteer, 'participations': participations, 'total_hours': total_hours})


@login_required
def events_list(request):
    events = Event.objects.annotate(
        total_hours=Coalesce(Sum('participation__worked_hours'), Value(0)),
        total_participants=Count('participation__volunteer', distinct=True)
    )

    return render(request, 'events_list.html', {'events': events})


@login_required
def view_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    participations = Participation.objects.filter(event=event)
    total_hours = participations.aggregate(Sum('worked_hours'))['worked_hours__sum'] or 0

    return render(request, 'view_event.html',
                  {'event': event, 'participations': participations, 'total_hours': total_hours})


@login_required
def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('events_list')
    else:
        form = EventForm()

    return render(request, 'add_event.html', {'form': form})


@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if request.method == 'POST' and 'delete' in request.POST:
        event.delete()
        return redirect('events_list')

    return render(request, 'delete_event.html', {'event': event})


@login_required
def add_participation(request):
    if request.method == 'POST':
        form = ParticipationForm(request.POST)

        if form.is_valid():
            volunteers = form.cleaned_data["volunteers"]

            for volunteer in volunteers:
                participation = Participation.objects.create(volunteer=volunteer, event=form.cleaned_data['event'],
                                                             worked_hours=form.cleaned_data['worked_hours'],
                                                             notes=form.cleaned_data['notes'])
                volunteer.update_last_active_date()

            return redirect('volunteers_list')
    else:
        form = ParticipationForm()

    return render(request, 'add_participation.html', {'form': form})


@login_required
def edit_volunteer(request, user_id):
    volunteer = get_object_or_404(Volunteer, pk=user_id)

    if request.method == 'POST':
        form = VolunteerEditForm(request.POST, instance=volunteer)
        if form.is_valid():
            form.save()
            return redirect('view_volunteer', user_id=user_id)
    else:
        form = VolunteerEditForm(instance=volunteer)

    return render(request, 'edit_volunteer.html', {'form': form, 'volunteer': volunteer})


@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('view_event', event_id=event_id)
    else:
        form = EventForm(instance=event)

    return render(request, 'edit_event.html', {'form': form, 'event': event})


@login_required
def generate_report(request, user_id):
    volunteer = get_object_or_404(Volunteer, pk=user_id)
    participations = Participation.objects.filter(volunteer=volunteer)
    total_hours = participations.aggregate(Sum('worked_hours'))['worked_hours__sum'] or 0

    # Create a PDF buffer and draw on it
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    # Add a title to the document
    title_text = f"Volunteer Report"
    p.setFont("Helvetica-Bold", 17)
    p.drawCentredString(letter[0] / 2, 720, title_text)

    p.setFont("Helvetica-Bold", 12)
    # Add an image as a header (replace 'your_image_path.png' with the actual image path)
    image_path = 'static/images/logo_asf.png'
    p.drawImage(image_path, 50, 700, width=60, height=60, mask="auto")

    # Draw the volunteer's name on the PDF
    name_text = f"Volunteer Name: {volunteer.first_name} {volunteer.last_name}"
    p.drawString(100, 650, name_text)

    # Draw education level and year
    education_text = f"Education Level: {volunteer.get_education_level_display()} | Education Year: {volunteer.education_year}"
    p.drawString(100, 630, education_text)

    # Draw the list of participations
    p.drawString(100, 600, "Participations:")
    y_position = 580  # Starting Y position for participations

    for participation in participations:
        if participation.event.start_date != participation.event.end_date:
            date_range = f"{participation.event.start_date} - {participation.event.end_date}"
        else:
            date_range = str(participation.event.start_date)

        participation_text = f"Event: {participation.event.name} | Date: {date_range} | Worked Hours: {participation.worked_hours} hours"
        p.drawString(100, y_position, participation_text)

        # Handle longer notes by manually wrapping text
        notes_text = participation.notes
        max_width = 400  # Adjust the maximum width as needed

        lines = []
        current_line = ""
        for word in notes_text.split():
            if p.stringWidth(current_line + word, 'Helvetica', 12) < max_width:
                current_line += word + " "
            else:
                lines.append(current_line)
                current_line = word + " "

        if current_line:
            lines.append(current_line)

        # Draw notes
        for line in lines:
            p.drawString(120, y_position - 15, line)
            y_position -= 15  # Adjust for the next line

        y_position -= 20  # Adjust for the next participation

    # Add other PDF content as needed, e.g., total hours, etc.
    p.drawString(100, y_position - 20, f"Total Hours: {total_hours} hours")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response[
        'Content-Disposition'] = f'attachment; filename="{volunteer.first_name}_{volunteer.last_name}_report.pdf"'
    return response


@login_required()
def view_dashboard(request):
    # Retrieve counts of volunteers, active volunteers, and total events
    num_volunteers = Volunteer.objects.filter(is_member=True).count()
    num_active_volunteers = Volunteer.objects.filter(is_active_member=True).filter(is_member=True).count()
    num_events = Event.objects.count()

    # Retrieve upcoming events within the next 30 days
    today = datetime.now().date()
    thirty_days_later = today + timedelta(days=30)
    upcoming_events = Event.objects.filter(start_date__range=[today, thirty_days_later]).order_by("start_date")

    # Calculate worked hours per month in the last year and create a bar chart
    today = datetime.now().date()
    last_year = today - timedelta(days=365)

    # Calculate the last day of the current month
    last_day_of_month = today.replace(day=1) + relativedelta(months=1, days=-1)

    monthly_worked_hours = Participation.objects.filter(
        event__start_date__gte=last_year,
        event__start_date__lte=last_day_of_month
    ).values('event__start_date__month').order_by('event__start_date__month').annotate(total_hours=Sum('worked_hours'))

    # Extract data for monthly totals and create a bar chart
    monthly_totals_dict = {result['event__start_date__month']: result['total_hours'] for result in monthly_worked_hours}
    current_month = today.month
    ordered_months = [(current_month + i - 1) % 12 + 1 for i in range(1, 13)]
    month_names = [calendar.month_abbr[month] for month in ordered_months]
    monthly_totals = [monthly_totals_dict.get(month, 0) for month in ordered_months]

    # Generate a bar chart image and convert it to base64 for rendering in the template
    plt.figure(figsize=(8, 5))
    plt.bar(month_names, monthly_totals)
    plt.xlabel('Month', fontsize=14)
    plt.ylabel('Total Hours', fontsize=14)
    plt.title('Volunteering Hours per Month in the Last Year', fontsize=16)
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    plt.close()
    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')

    # Retrieve event data for the calendar
    events = Event.objects.all()
    events_data = []
    for event in events:
        end_date = event.end_date if event.end_date == event.start_date else event.end_date + timedelta(days=1)
        events_data.append({
            'id': event.id,
            'title': event.name,
            'start': event.start_date.isoformat(),
            'end': end_date.isoformat(),
        })

    # Get all volunteers by department and create a pie chart
    departments = Volunteer.objects.filter(is_member=True).values('department')
    departments = [item['department'] for item in departments]
    department_counts = Counter(departments)

    plt.figure(figsize=(8, 5))
    plt.pie(department_counts.values(), labels=department_counts.keys(), autopct='%1.1f%%', textprops={'fontsize': 18})
    plt.title('Volunteers Distribution by Department', fontsize=16)

    department_chart_stream = BytesIO()
    plt.savefig(department_chart_stream, format='png')
    plt.close()

    department_chart_base64 = base64.b64encode(department_chart_stream.getvalue()).decode('utf-8')

    # Prepare the context with relevant data for rendering in the template
    context = {
        'num_volunteers': num_volunteers,
        'num_active_volunteers': num_active_volunteers,
        'num_events': num_events,
        'upcoming_events': upcoming_events,
        'chart_image': image_base64,
        'department_chart_image': department_chart_base64,
        'events_calendar': events_data
    }

    # Render the 'dashboard.html' template with the context data
    return render(request, 'dashboard.html', context)
