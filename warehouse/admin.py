from django.contrib import admin
from .models import Operation, CustomUser, DayAlert
# Register your models here.


admin.site.register(Operation)
admin.site.register(CustomUser)
admin.site.register(DayAlert)