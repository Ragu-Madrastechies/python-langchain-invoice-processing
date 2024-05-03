from django.urls import path
from .views import register_api,login_api,employee_details_api,project_name,five_entries_api,piechart_api,employee_details,clockin_api,clockout_api,attendance_api,leave_list,timesheet_list,employee_name
urlpatterns = [
    path('login', login_api.as_view()),
    path('register', register_api.as_view()),
    path('employee', employee_details.as_view()),
    path('clockin', clockin_api.as_view()),
    path('clockout', clockout_api.as_view()),
    path('attendance', attendance_api.as_view()),
    path('five_entries',five_entries_api.as_view()),
    path('piechart',piechart_api.as_view()),
    path('leave_list', leave_list.as_view()),
    path('timesheet_list',timesheet_list.as_view()),
    path('project_name', project_name.as_view()),
    path('employee_name',employee_name.as_view()),
    path('employee_details_api',employee_details_api.as_view())
]