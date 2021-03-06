import datetime
import calendar


from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from .models import Department, Record, Person, Profile
from .forms import ProfileForm, RecordForm, TimesheetForm, BaseOfRecords
from xhtml2pdf import pisa
from .time_classes import Report, Timesheet, TimeTrack
from django.contrib.auth.decorators import login_required
from .consts import TYPE_CHOICES, ID_NONE
from django.template.loader import get_template


def home_view(request):
    return redirect('login')


@login_required
def base_of_records_view(request):
    return redirect('login')


@login_required
def record_view(request):
    if request.method == "POST":
        print(request.POST)
        form = RecordForm(request.POST)

        if form.is_valid():
            print(f'!!!!!!!!!!!!!!!!!!!!!!!choice = {ID_NONE}; type = {request.POST["type"]}')
            person, personnel_number = request.POST['person'].split('; ')

            if request.POST['type'] is not ID_NONE:
                Record.objects.create(type=TYPE_CHOICES[int(request.POST['type'])][1],
                                      person=Person.objects.get(personnel_number=personnel_number),
                                      date_from=request.POST['date_from'],
                                      date_to=request.POST['date_to'] if request.POST['date_to'] != '' else request.POST['date_from'],
                                      created_by=request.user)

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'filename="report.pdf"'
            report = Report(request.POST)

            if report.pdf_needed():
                pisa.CreatePDF(report.make_html().encode('UTF-8'), dest=response, encoding='UTF-8')
                # return HttpResponse(html)
                return response
            else:
                profile = Profile.objects.get(user=request.user)
                current_department = profile.person.department
                context = {
                           'confirmed': True,
                           'alert': report.alert(),
                           'form': form,
                           'department': current_department,
                           'departments': Department.objects.all(),
                           'persons': Person.objects.filter(department=current_department),
                           }
                return render(request, 'manager/record.html', context=context)
    else:
        form = RecordForm()

    profile, department = get_profile_department(request)
    context = {
        'form': form,
        'department': department,
        'departments': Department.objects.all(),
        'persons': Person.objects.filter(department=department),
    }
    return render(request, 'manager/record.html', context=context)


@login_required
def timesheet_view(request):
    profile, department = get_profile_department(request)
    if request.method == "POST":
        timesheet = Timesheet(request=request.POST, department=department)

        template = get_template('manager/timesheet_pdf.html')
        context = timesheet.context()
        html = template.render({'pdf': context})
        return HttpResponse(html)

        # response = HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = 'filename="timesheet.pdf"'
        # pisa.CreatePDF(html.encode('UTF-8'), dest=response, encoding='UTF-8')
        # return response
    else:
        form = TimesheetForm()

    context = {
        'form': form,
        'department': department,
        'departments': Department.objects.all(),
    }
    return render(request, 'manager/timesheet.html', context=context)


@login_required
def time_track_view(request):
    profile, department = get_profile_department(request)
    if request.method == 'POST':
        time_track = TimeTrack(request.POST, department=department)
        html = time_track.make_html()
        return HttpResponse(html)

        # response = HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = 'filename="timesheet.pdf"'
        # pisa.CreatePDF(html.encode('UTF-8'), dest=response, encoding='UTF-8')
        # return response
    else:
        form = TimesheetForm()
        context = {
            'department': department,
            'departments': Department.objects.all(),
            'form': form,
        }
        return render(request, 'manager/time_track.html', context=context)


@login_required
def record_base_view(request):

    profile, department = get_profile_department(request)
    records = Record.objects.filter(person__department=department)

    if request.method == "POST":
        print(request.POST)
        print(f'date = {request.POST["date"]}')
        form = BaseOfRecords(request.POST)
        date = request.POST['date']

        if 'kill' in request.POST:
            kill_id = request.POST["kill"]
            Record.objects.get(id=kill_id).delete()

        if request.POST['type'] is not TYPE_CHOICES[0][0]:
            records = records.filter(type=TYPE_CHOICES[int(request.POST["type"])][1])

        if request.POST['name'] is not '':
            records = records.filter(person__name__contains=request.POST['name'])

        if request.POST['date'] is not '':
            this_month = datetime.datetime.strptime(request.POST['date'], '%Y-%m')
            next_month = datetime.datetime(year=this_month.year, month=this_month.month,
                                           day=calendar.monthrange(this_month.year, this_month.month)[1])
            date_range = [this_month, next_month]
            print(f'date_range = {date_range}')
            records = records.filter(date_from__range=date_range)

        if request.POST['per_num'] not in ['', None]:
            per_num = request.POST['per_num']
            records = records.filter(person__personnel_number__contains=per_num)
        else:
            per_num = ''
    else:
        print(f'GET{request.GET}')
        date = ''
        per_num = ''
        form = BaseOfRecords()

    context = {
        'department': department,
        'departments': Department.objects.all(),
        'form': form,
        'records': records.order_by('id').reverse(),
        'date': date,
        'per_num': per_num,
    }
    print(f'context = {context}')

    return render(request, 'manager/record_base.html', context)


@login_required
def my_profile_view(request):
    profile, department = get_profile_department(request)
    form = ProfileForm(instance=profile)

    if form.is_valid():
        form.save()
        confirm = True
    else:
        confirm = False

    context = {
        'profile': profile,
        'form': form,
        'confirm': confirm,
        'department': department,
        'departments': Department.objects.all(),
    }
    return render(request, 'manager/my_profile.html', context=context)


@login_required
def import_view(request):
    if request.method == 'POST':
        print(request.POST)
        if 'IMPORT_PERSONS' in request.POST:
            from .import_from_old import get_persons
            persons = get_persons()
            department = Department.objects.get(name='????????????')

            for person in persons:
                Person.objects.create(
                    name=person[1],
                    name2=person[2],
                    job=person[5],
                    job2=person[6],
                    personnel_number=person[3],
                    pass_number=person[4],
                    department=department,
                    is_boss=False,
                )
        elif 'IMPORT_RECORDS' in request.POST:
            from .import_from_old import get_records
            records = get_records()
            print(records)

            for record in records:
                Record.objects.create(
                    person=Person.objects.get(name=record[1]),
                    type=record[2],
                    date_from=record[3],
                    date_to=record[4],
                    created_by='?????????????? ??.??.',
                )
        return render(request, 'manager/import.html', {'ok': 'OK!!'})
    else:
        print(request.GET)
        return render(request, 'manager/import.html', {})


def get_profile_department(request):
    profile = Profile.objects.get(user=request.user)
    department = profile.department
    return profile, department


def records_dep_change(request, dep_name):
    profile = Profile.objects.get(user=request.user)
    department = Department.objects.get(name=dep_name)
    profile.department = department
    profile.save()
    persons = Person.objects.filter(department=department)
    response = [f"{person.name}; {person.personnel_number}---" for person in persons]
    return HttpResponse(response)


def base_dep_change(request, dep_name):
    profile = Profile.objects.get(user=request.user)
    department = Department.objects.get(name=dep_name)
    profile.department = department
    profile.save()
    records = Record.objects.filter(person__department=department).order_by('id')
    response = [f"{record.id}--{record.type}--{record.person.name}--{record.person.personnel_number}--{record.date_from}--{record.date_to}---" for record in records]
    response.reverse()
    return HttpResponse(response)
