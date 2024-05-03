from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(self, employee_id, employee_name, employee_email, password=None, **extra_fields):
        user = self.model(
            employee_id=employee_id,
            employee_name=employee_name,
            employee_email=employee_email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
class Employee(AbstractBaseUser, PermissionsMixin):
    employee_id = models.CharField(unique=True, max_length=20)
    employee_name = models.CharField(max_length=255)
    employee_email = models.EmailField(unique=True)
    employee_photo = models.ImageField(upload_to='employee_photos/', null=True, blank=True)
    role = models.CharField(max_length=50)
    objects = CustomUserManager()

    USERNAME_FIELD = 'employee_email'
    REQUIRED_FIELDS = ['employee_id', 'employee_name']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class Attendance(models.Model):
    employee_id = models.CharField(max_length=20)
    clockin_time = models.TimeField(null=True, blank=True, max_length=20)
    clockout_time = models.TimeField(null=True, blank=True, max_length=20)
    clockin_date = models.DateField(null=True, blank=True)
    clockout_date = models.DateField(null=True, blank=True)
    month = models.CharField(null=True, blank=True, max_length=20 )
    year = models.IntegerField(null=True, blank=True)
    hour_worked = models.CharField(max_length=20, default='00:00:00')
    day_present = models.IntegerField(default=0)  
    leave = models.IntegerField(default=1)  
    attendance_status = models.CharField(max_length=20, default='')

class Leave(models.Model):
    employee_id = models.CharField(max_length=20)
    employee_name = models.CharField(max_length=255)
    employee_email = models.EmailField( )
    leave_type = models.CharField(max_length=50)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    reason = models.TextField()
    no_of_days = models.CharField(max_length=20)
    submit_date = models.DateField(null=True, blank=True)
    request_status = models.CharField(max_length=100, default='')

class timesheet(models.Model):
    employee_id = models.CharField(max_length=20)
    employee_name = models.CharField(max_length=255)
    project_name = models.CharField(max_length=1024)
    clockin_time = models.TimeField(null=True, blank=True, max_length=20)
    clockout_time = models.TimeField(null=True, blank=True, max_length=20)
    submitdate = models.DateField(null=True, blank=True)
    hour_worked = models.CharField(max_length=20)
    comments = models.CharField(null=True,blank=True, max_length=2048)
    tasks = models.JSONField(default=list)
    timesheet_status = models.CharField(max_length=100, default='')

class Employee_Details(models.Model):
    employee_id = models.CharField(unique=True,max_length=20)
    employee_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=255)
    marital_status = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    employee_email = models.CharField(max_length=255)
    emergencycontact_name = models.CharField(max_length=255)
    emergencycontact_relationship = models.CharField(max_length=255)
    emergencycontact_phone = models.CharField(max_length=255)
    date_of_joining = models.DateField(null=True, blank=True)
    employee_type = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    position_supervisor = models.CharField(null=True, blank=True, max_length=255)
    employment_status = models.CharField(max_length=255)
    salary = models.CharField(max_length=255)
    pay_frequency = models.CharField(max_length=255)
    account_holder_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255)
    bank_ifsc_code = models.CharField(max_length=255)
    benefits_enrollment = models.CharField(null=True, blank=True,max_length=255)
    pan_number = models.CharField(max_length=255)
    uan_number = models.CharField(null=True, blank=True,max_length=255)
    tax_filling_status = models.CharField(null=True, blank=True,max_length=255)
    work_authorization = models.CharField(null=True, blank=True,max_length=255)
    visa_status = models.CharField(null=True, blank=True,max_length=255)
    educational_qualification = models.JSONField(default=list)
    certifications = models.JSONField(default=list)
    skills = models.CharField(max_length=255)
    performance_reviews = models.CharField(null=True, blank=True,max_length=255)
    training_history = models.CharField(null=True, blank=True,max_length=255)
    notes = models.CharField(null=True, blank=True,max_length=255)


  



    