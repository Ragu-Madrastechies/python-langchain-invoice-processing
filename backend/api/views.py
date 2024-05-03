import jwt, datetime
from django.db.models import Q
from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import EmployeeSerializer, AttendanceSerializer, LeaveSerializer, TimesheetSerializer,Employee_detailsSerializer
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .models import Employee, Attendance, Leave, timesheet, Employee_Details
from rest_framework import status
from datetime import datetime as dt
from django.shortcuts import get_object_or_404
from django.utils import timezone

class register_api(APIView):
    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class login_api(APIView):
    def post(self, request):
        employee_email = request.data['employee_email']
        password = request.data['password']
        user = Employee.objects.filter(employee_email=employee_email).first()
        if user is None:
            return Response({'result': False, 'message': 'Invalid Email'})
        if password != user.password:
            return Response({'result': False, 'message': 'Invalid Password'})
        payload = {
            'employee_id': user.employee_id,
            'exp': (datetime.datetime.utcnow() + datetime.timedelta(minutes=300)),
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256')
        response = Response()
        response.set_cookie(key='jwt', value=token)
        response.data = {
            'result':True,
            'jwt': token,
        }
        return response

class employee_details(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        employee_id = payload.get('employee_id')
        if not employee_id:
            raise AuthenticationFailed('Invalid token!')
        user = Employee.objects.filter(employee_id=employee_id).first()
        if not user:
            raise AuthenticationFailed('User not found!')
        serializer = EmployeeSerializer(user)
        response_data = serializer.data
        return Response(response_data)

class clockin_api(APIView):
    def post(self, request):
        serializer = AttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee_id = serializer.validated_data['employee_id']
        clockin_date = serializer.validated_data['clockin_date']
        existing_clockin = Attendance.objects.filter(
            employee_id=employee_id,
            clockin_date=clockin_date
        ).exclude(clockout_time=None).first()
        if existing_clockin:
            return Response({'error': 'Clock-in time already recorded for this date.'}, status=400)
        existing_clockout = Attendance.objects.filter(
            employee_id=employee_id,
            clockin_date=clockin_date
        ).exclude(clockout_time=None).first()
        if existing_clockout:
            return Response({'error': 'Clockout time already recorded for this date.'}, status=400)
        clockin_time = serializer.validated_data['clockin_time']
        day_present = 1
        leave = 0
        month = clockin_date.strftime('%B')
        year = clockin_date.year
        attendance_status = 'Late Arrival' if clockin_time.hour >= 11 else ''
        serializer.validated_data['day_present'] = day_present
        serializer.validated_data['leave'] = leave
        serializer.validated_data['month'] = month
        serializer.validated_data['year'] = year
        serializer.validated_data['attendance_status'] = attendance_status
        serializer.save()
        return Response(serializer.data)
    
class clockout_api(APIView):
    def post(self, request):
        serializer = AttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee_id = serializer.validated_data['employee_id']
        clockout_date = serializer.validated_data['clockout_date']
        clockout_time = serializer.validated_data['clockout_time']
        existing_clockout = Attendance.objects.filter(
            employee_id=employee_id,
            clockin_date=clockout_date
        ).exclude(clockout_time=None).first()
        if existing_clockout:
            return Response({'error': 'Clock-in time already recorded for this date.'}, status=400)
        try:
            clockin_record = Attendance.objects.get(employee_id=employee_id, clockin_date=clockout_date)
        except Attendance.DoesNotExist:
            return Response({"error": "Clock-in record not found for the specified date and employee"})
        clockin_datetime = dt.combine(clockin_record.clockin_date, clockin_record.clockin_time)
        clockout_datetime = dt.combine(clockout_date, clockout_time)
        hours_worked_timedelta = clockout_datetime - clockin_datetime
        hours_worked_seconds = int(hours_worked_timedelta.total_seconds())
        hours, remainder = divmod(hours_worked_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        hours_worked = "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))
        serializer.validated_data['hour_worked'] = hours_worked
        status_values = [clockin_record.attendance_status]
        if 17 <= clockout_time.hour < 19 :
            status_values.append('')
        elif clockout_time.hour < 17 :
            status_values.append('Early Departure')
        elif clockout_time.hour >= 19 or not clockin_record.clockout_time:
            status_values.append('Late Exit')
        elif hours_worked.hour > 8:
            status_values.append('Overtime')
        status_values = list(filter(None, status_values))
        status_string = ', '.join(status_values)
        attendance_status = f"'{status_string}'"
        serializer.validated_data['attendance_status'] = attendance_status
        clockin_record.clockout_time = clockout_time
        clockin_record.hour_worked = hours_worked
        clockin_record.attendance_status = attendance_status
        clockin_record.save()
        return Response(serializer.data)
    
class attendance_api(APIView):
    def get(self, request, employee_id=None, month=None, clockin_date=None, attendance_status=None):
        employee_id = request.query_params.get('employee_id')
        month = request.query_params.get('month')
        clockin_date = request.query_params.get('clockin_date')
        attendance_status = request.query_params.get('attendance_status')
        employee_name = request.query_params.get('employee_name')
        attendance_records = Attendance.objects.all()
        filter_conditions = Q()
        if employee_id is not None and employee_id != '':
            filter_conditions &= Q(employee_id=employee_id)
        if month is not None and month != '':
            filter_conditions &= Q(month=month)
        if clockin_date is not None and clockin_date != '':
            filter_conditions &= Q(clockin_date=clockin_date)
        if attendance_status is not None and attendance_status != '':
            filter_conditions &= Q(attendance_status__contains=attendance_status)
        if employee_name is not None and employee_name != '':
            employee_ids = Employee.objects.filter(employee_name__contains=employee_name).values_list('employee_id', flat=True)
            filter_conditions &= Q(employee_id__in=employee_ids)
        attendance_records = attendance_records.filter(filter_conditions).order_by('-clockin_date')
        serialized_data = []
        for attendance_record in attendance_records:
            employee_name = Employee.objects.get(employee_id=attendance_record.employee_id).employee_name
            serialized_data.append({
                'employee_id': attendance_record.employee_id,
                'employee_name': employee_name,
                'clockin_time': attendance_record.clockin_time,
                'clockout_time': attendance_record.clockout_time,
                'clockin_date': attendance_record.clockin_date,
                'clockout_date': attendance_record.clockout_date,
                'month': attendance_record.month,
                'year': attendance_record.year,
                'hour_worked': attendance_record.hour_worked,
                'day_present': attendance_record.day_present,
                'leave': attendance_record.leave,
                'attendance_status': attendance_record.attendance_status,
            })
        return Response(serialized_data, status=status.HTTP_200_OK)

class five_entries_api(APIView):
    def get(self, request):
        employee_id = request.query_params.get('employee_id')
        clockin_date = request.query_params.get('clockin_date')
        filter_conditions = Q()
        if employee_id is not None:
            filter_conditions &= Q(employee_id=employee_id)
        if clockin_date is not None:
            filter_conditions &= Q(clockin_date=clockin_date)
        attendance_records = Attendance.objects.filter(filter_conditions).order_by('-clockin_date')[:5]
        sorted_records = sorted(attendance_records, key=lambda x: x.clockin_date)
        serializer = AttendanceSerializer(sorted_records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class piechart_api(APIView):
    def get(self, request):
        employee_id = request.query_params.get('employee_id', None)
        month = request.query_params.get('month',None)
        if not month:
            current_month = dt.now().strftime('%B')
            month = current_month
        if not employee_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        employee = get_object_or_404(Employee, employee_id=employee_id)
        attendances = Attendance.objects.filter(employee_id=employee_id,month=month)
        working_days_info = self.get_working_days_info(month)
        total_days_worked = sum(attendance.day_present for attendance in attendances)
        total_hours_worked = sum(int(attendance.hour_worked.split(':')[0]) for attendance in attendances)
        attendance_percentage = round((total_days_worked / working_days_info['working_days']) * 100, 2) if working_days_info['working_days'] != 0 else 0
        leaves_taken = working_days_info['working_days'] - total_days_worked
        response_data = {
            'employee_id': employee.employee_id,
            'employee_name': employee.employee_name,
            'no_of_days_worked': total_days_worked,
            'total_no_of_hours_worked': total_hours_worked,
            'attendance_percentage': attendance_percentage,
            'no_of_leaves_taken': leaves_taken,
            'total_working_days': working_days_info['working_days'],
            'total_working_hours': working_days_info['total_working_hours'],
            'month': month,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    def get_working_days_info(self, month):
        working_days_mapping = {
           'January': {'working_days': 20, 'total_working_hours': 160},
            'February': {'working_days': 21, 'total_working_hours': 168},
            'March': {'working_days': 20, 'total_working_hours': 160},
            'April': {'working_days': 21, 'total_working_hours': 168},
            'May': {'working_days': 22, 'total_working_hours': 176},
            'June': {'working_days': 19, 'total_working_hours': 152},
            'July': {'working_days': 23, 'total_working_hours': 184},
            'August': {'working_days': 21, 'total_working_hours': 168},
            'September': {'working_days': 21, 'total_working_hours': 168},
            'October': {'working_days': 21, 'total_working_hours': 168},
            'November': {'working_days': 21, 'total_working_hours': 168},
            'December': {'working_days': 21, 'total_working_hours': 168},
            }
        return working_days_mapping.get(month, {'working_days': 0, 'total_working_hours': 0})
        
class leave_list(APIView):
    def post(self,request):
        serializer = LeaveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee_id = serializer.validated_data['employee_id']
        employee_email = serializer.validated_data['employee_email']
        request_status = 'Approval Pending'
        serializer.validated_data['request_status'] = request_status
        serializer.save()
        return Response(serializer.data)
    def get(self,request, request_status=None, employee_id=None, id=None, submit_date=None, leave_type=None, employee_name=None):
        request_status = request.query_params.get('request_status')
        employee_id = request.query_params.get('employee_id')
        id = request.query_params.get('id')
        submit_date = request.query_params.get('submit_date')
        leave_type = request.query_params.get('leave_type')
        employee_name = request.query_params.get('employee_name')
        leave_record = Leave.objects.all()
        filter_conditions = Q()
        if request_status is not None and request_status != '':
            filter_conditions &= Q(request_status=request_status)
        if employee_id is not None and employee_id != '':
            filter_conditions &= Q(employee_id=employee_id)
        if id is not None and id != '':
            filter_conditions &= Q(id=id)
        if submit_date is not None and submit_date != '':
            filter_conditions &= Q(submit_date=submit_date)
        if leave_type is not None and leave_type != '':
            filter_conditions &= Q(leave_type=leave_type)
        if employee_name is not None and employee_name != '':
            filter_conditions &= Q(employee_name=employee_name)
        leave_record = leave_record.filter(filter_conditions).order_by('-submit_date')
        serializer = LeaveSerializer(leave_record, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def put(self,request, *args, **kwargs):
        id = request.data.get('id', None)
        employee_id = request.data.get('employee_id', None)
        submit_date = request.data.get('submit_date', None)
        new_request_status = request.data.get('request_status', None)
        leaves_to_update = Leave.objects.filter(id=id, employee_id=employee_id, submit_date=submit_date)
        leaves_to_update.update(request_status=new_request_status)
        updated_leaves = Leave.objects.filter(id=id, employee_id=employee_id, submit_date=submit_date)
        serializer = LeaveSerializer(updated_leaves, many=True)
        return Response(serializer.data)
    
class timesheet_list(APIView):
    def post(self, request):
        serializer = TimesheetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee_id = serializer.validated_data['employee_id']
        timesheet_status = 'Approval Pending'
        serializer.validated_data['timesheet_status'] = timesheet_status
        serializer.save()
        return Response(serializer.data)
    def get(self, request,employee_id=None,employee_name=None,submitdate=None, id=None, timesheet_status=None, project_name=None):
        timesheet_status = request.query_params.get('timesheet_status')
        employee_id = request.query_params.get('employee_id')
        id = request.query_params.get('id')
        submitdate_from = request.query_params.get('submitdate_from')
        submitdate_to = request.query_params.get('submitdate_to')
        project_name = request.query_params.get('project_name')
        employee_name = request.query_params.get('employee_name')
        timesheet_record = timesheet.objects.all()
        filter_conditions = Q()
        if timesheet_status is not None and timesheet_status != '':
            filter_conditions &= Q(timesheet_status=timesheet_status)
        if employee_id is not None and employee_id != '':
            filter_conditions &= Q(employee_id=employee_id)
        if id is not None and id != '':
            filter_conditions &= Q(id=id)
        if submitdate_from is not None and submitdate_from != '' and submitdate_to is not None and submitdate_to != '':
            filter_conditions &= Q(submitdate__range=[submitdate_from, submitdate_to])
        else:
            if submitdate_from is not None and submitdate_from != '':
                filter_conditions &= Q(submitdate=submitdate_from)
            if submitdate_to is not None and submitdate_to != '':
                filter_conditions &= Q(submitdate=submitdate_to)
        if project_name is not None and project_name != '':
            filter_conditions &= Q(project_name=project_name)
        if employee_name is not None and employee_name != '':
            filter_conditions &= Q(employee_name=employee_name)
        timesheet_record = timesheet_record.filter(filter_conditions).order_by('-submitdate')
        serializer = TimesheetSerializer(timesheet_record, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def put(self, request, *args, **kwargs):
        id = request.data.get('id', None)
        employee_id = request.data.get('employee_id', None)
        submitdate = request.data.get('submitdate', None)
        new_timesheet_data = request.data  
        try:
            timesheet_to_update = timesheet.objects.get(id=id, employee_id=employee_id, submitdate=submitdate)
            serializer = TimesheetSerializer(timesheet_to_update, data=new_timesheet_data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except timesheet.DoesNotExist:
            return Response("Timesheet does not exist", status=status.HTTP_404_NOT_FOUND)
        
class project_name(APIView):
    def get(self,request):
        project_data = timesheet.objects.values_list('project_name', flat=True).distinct()
        return Response(list(project_data))
    
class employee_name(APIView):
    def get(self,request):
        employee_data = Employee.objects.values_list('employee_name',flat=True)
        return Response(list(employee_data))
    
class employee_details_api(APIView):
    def post(self,request):
        serializer = Employee_detailsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    def get(self,request,employee_id=None, employee_name=None):
        employee_id = request.query_params.get('employee_id') 
        employee_name = request.query_params.get('employee_name')
        employee_details_record = Employee_Details.objects.all()
        filter_conditions = Q()
        if employee_id is not None and employee_id != '':
            filter_conditions &= Q(employee_id=employee_id)
        if employee_name is not None and employee_name != '':
            filter_conditions &= Q(employee_name=employee_name)
        employee_details_record = employee_details_record.filter(filter_conditions).order_by('employee_name')
        serializer = Employee_detailsSerializer(employee_details_record,many=True)
        return Response(serializer.data,status.HTTP_200_OK)
    def put(self,request, *args, **kwargs):
        employee_id = request.data.get('employee_id', None)
        new_employee_details = request.data
        try:
            employee_details_update = Employee_Details.objects.get(employee_id=employee_id)
            serializer = Employee_detailsSerializer(employee_details_update,data=new_employee_details,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response (serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Employee_Details.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
