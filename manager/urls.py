from django.urls import path
from .views import home_view, record_view, timesheet_view, time_track_view, my_profile_view, \
    record_base_view, import_view, records_dep_change, base_dep_change

app_name = 'manager'

urlpatterns = [
    path('', home_view, name='home'),
    path('record/', record_view, name='record'),
    path('timesheet/', timesheet_view, name='timesheet'),
    path('time_track/', time_track_view, name='time_track'),
    path('my_profile/', my_profile_view, name='my_profile'),
    path('record_base/', record_base_view, name='record_base'),
    path('import/', import_view, name='import'),
    path('records_dep_change/<str:dep_name>', records_dep_change, name='records_dep_change'),
    path('base_dep_change/<str:dep_name>', base_dep_change, name='base_dep_change'),
]