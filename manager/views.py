# views.py
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from reportlab.lib.pagesizes import letter

from .forms import VolunteerForm, EventForm, ParticipationForm, VolunteerEditForm
from .models import Volunteer, Event, Participation

from reportlab.pdfgen import canvas


@login_required
def index(request):
    volunteers = Volunteer.objects.all()

    for volunteer in volunteers:
        volunteer.total_hours = Participation.objects.filter(volunteer=volunteer).aggregate(Sum('worked_hours'))[
                                    'worked_hours__sum'] or 0

    return render(request, 'index.html', {'volunteers': volunteers})


@login_required
def add_volunteer(request):
    if request.method == 'POST':
        form = VolunteerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/manager')  # Redirect to a page displaying the list of volunteers
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
    events = Event.objects.all()
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
            participation = form.save()
            participation.volunteer.update_last_active_date()
            return redirect('index')
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
    p.drawImage(image_path, 50, 700, width=140, height=50, mask="auto")

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
        participation_text = f"Event: {participation.event.name} | Date: {participation.date} | Worked Hours: {participation.worked_hours} hours"
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
    # ... add more content as needed

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