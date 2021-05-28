import datetime
import calendar


from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from .models import Department, Record, Person, Profile
from .forms import ProfileForm, RecordForm, TimesheetForm, BaseOfRecords
from xhtml2pdf import pisa
from .utils import Report, Timesheet, TimeTrack
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

    profile = Profile.objects.get(user=request.user)
    current_department = profile.person.department
    context = {
        'form': form,
        'department': current_department,
        'departments': Department.objects.all(),
        'persons': Person.objects.filter(department=current_department),
    }
    return render(request, 'manager/record.html', context=context)


@login_required
def timesheet_view(request):
    if request.method == "POST":
        profile = Profile.objects.get(user=request.user)
        user_department = profile.person.department
        persons = Person.objects.filter(department=user_department)
        timesheet = Timesheet(request=request.POST, department=user_department)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="timesheet.pdf"'

        template = get_template('manager/timesheet_pdf.html')
        context = timesheet.context()
        html = template.render({'pdf': context})
        # html = timesheet.make_html()

        pisa.CreatePDF(html.encode('UTF-8'), dest=response, encoding='UTF-8')

        # return response
        return HttpResponse(html)
    else:
        form = TimesheetForm()

    return render(request, 'manager/timesheet.html', context={'form': form})


@login_required
def time_track_view(request):
    if request.method == 'POST':
        department = Department.objects.get(id=1)
        time_track = TimeTrack(request.POST, department=department)
        html = time_track.make_html()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="timesheet.pdf"'
        pisa.CreatePDF(html.encode('UTF-8'), dest=response, encoding='UTF-8')

        return HttpResponse(html)
        # return response
    else:
        form = TimesheetForm()
        context = {
            'form': form,
        }
        return render(request, 'manager/time_track.html', context=context)


@login_required
def record_base_view(request):

    records = Record.objects.all()

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
    profile = Profile.objects.get(user=request.user)
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)

    confirm = False

    if form.is_valid():
        form.save()
        confirm = True

    context = {
        'profile': profile,
        'form': form,
        'confirm': confirm,
    }
    return render(request, 'manager/my_profile.html', context=context)


@login_required
def import_view(request):
    if request.method == 'POST':
        print(request.POST)
        if 'IMPORT_PERSONS' in request.POST:
            from .import_from_old import get_persons
            persons = get_persons()
            department = Department.objects.get(name='ЛОЦСиА')

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
                    created_by='Поляков А.Е.',
                )
        return render(request, 'manager/import.html', {'ok': 'OK!!'})
    else:
        print(request.GET)
        return render(request, 'manager/import.html', {})



