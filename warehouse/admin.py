from django.contrib import admin
from .models import Operation, CustomUser, DayAlert, Announcement, ManHour
# Register your models here.


admin.site.register(Operation)
admin.site.register(CustomUser)
admin.site.register(DayAlert)
admin.site.register(Announcement)
admin.site.register(ManHour)