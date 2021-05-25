from django.contrib import admin
from .models import Department, Person, Record, Profile, ExceptionDay


admin.site.register(Department)
admin.site.register(Person)
admin.site.register(Record)
admin.site.register(Profile)
admin.site.register(ExceptionDay)


# Register your models here.
