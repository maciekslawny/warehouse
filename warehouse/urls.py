from django.urls import path, include

from . import views

app_name = "warehouse"

urlpatterns = [
    path('', views.home, name='home'),
    path('zaloguj', views.login_view, name='login'),
    path('wyloguj', views.logout_view, name='wyloguj'),
    path('operacje/dzien', views.operations, name='operations'),
    path('operacje/moje', views.my_operations, name='my_operations'),
    path('operacje/wszystkie', views.all_operations, name='all_operations'),
    path('operacje/tydzien', views.operations_week, name='operations'),
    path('operacje/tydzien/<int:input_year>/<int:input_week>', views.operations_week, name='operations-week'),
    path('operacje/wybor', views.operation_select_date, name='operation_select_date'),
    path('operacje/akceptacja/<int:operation_pk>', views.operation_acceptation, name='operation_acceptation'),
    path('operacje/akceptacja-cofniecie/<int:operation_pk>', views.operation_revoke_acceptation, name='operation_revoke_acceptation'),
    path('operacje/dzien/<slug:input_date>', views.operations, name='operations'),
    path('operacje/dodaj', views.operation_add, name='add_operation'),
    path('operacje/edytuj/<int:operation_pk>', views.operation_edit, name='edit_operation'),
    path('operacje/wgraj-zdjecie/<int:operation_pk>', views.upload_photos, name='upload_photos'),
    path('operacje/<int:operation_pk>', views.operation_detail, name='operation_detail'),
    path('zdjecie/usun/<int:photo_pk>', views.delete_photo, name='delete_photo'),
    path('uzytkownicy', views.accounts, name='uzytkownicy'),
    path('generuj-raport', views.generate_pdf, name='generate_pdf'),
    path('komunikaty', views.announcements, name='announcements'),
    path('komunikaty/dodaj', views.announcement_add, name='add_announcement'),
    path('komunikaty/edytuj/<int:announcement_pk>', views.announcement_edit, name='edit_announcement'),
    path('komunikaty/usun/<int:announcement_pk>', views.announcement_delete, name='delete_announcement'),

    path('alerty', views.day_alerts, name='day_alerts'),
    path('alerty/dodaj', views.day_alert_add, name='add_day_alert'),
    path('alerty/edytuj/<int:day_alert_pk>', views.day_alert_edit, name='edit_day_alert'),
    path('alerty/usun/<int:day_alert_pk>', views.day_alert_delete, name='delete_day_alert'),

    path('statystyki', views.statistics, name='statistics'),


]
