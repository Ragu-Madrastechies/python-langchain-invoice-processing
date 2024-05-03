from rest_framework import serializers
from .models import Employee, Attendance, Leave, timesheet, Employee_Details

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['employee_id', 'employee_name', 'employee_email','password', 'employee_photo', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class AttendanceSerializer(serializers.ModelSerializer): 
    class Meta :
        model = Attendance
        fields = ['employee_id','clockin_time','clockout_time','clockin_date','clockout_date','month','year','hour_worked','day_present','leave','attendance_status']

class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = ['id','employee_id','employee_name','employee_email','leave_type','start_date','end_date','reason','no_of_days','submit_date','request_status']

class TimesheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = timesheet
        fields = ['id','employee_id','employee_name','project_name','clockin_time','clockout_time','submitdate','hour_worked','comments','tasks','timesheet_status']

class Employee_detailsSerializer(serializers.ModelSerializer):
    class Meta:
        model =Employee_Details
        fields = ['employee_id','employee_name','gender','date_of_birth','nationality','marital_status','address','phone','employee_email','emergencycontact_name','emergencycontact_relationship','emergencycontact_phone',
                  'date_of_joining','employee_type','department','job_title','position_supervisor','employment_status','salary','pay_frequency','account_holder_name','account_number','bank_name','bank_ifsc_code','benefits_enrollment','pan_number','uan_number',
                  'tax_filling_status','work_authorization','visa_status','educational_qualification','certifications','skills','performance_reviews','training_history','notes']
    
        