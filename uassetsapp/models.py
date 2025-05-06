from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Faculty(models.Model):
    facultyname = models.CharField(max_length=200)
    email = models.CharField(max_length=100, null=True, blank=True)
    tel = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self) -> str:
        return self.facultyname

class Department(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    departmentname = models.CharField(max_length=200)
    email = models.CharField(max_length=100, null=True, blank=True)
    tel = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ('faculty__facultyname', 'departmentname',)

    def __str__(self) -> str:
        return self.faculty.facultyname + ' __> ' + self.departmentname
    
class UserBio(models.Model):
    userid = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=200, null=True, blank=True);
    last_name = models.CharField(max_length=200, null=True, blank=True);
    birthdate = models.DateField(null=True, blank=True)
    citizenid = models.CharField(max_length=20, null=True, blank=True)
    sex = models.CharField(max_length=2, choices=(('1','ชาย'), ('2','หญิง'), ('3','ไม่ระบุ')), default = 3)
    tel = models.CharField(max_length=100, null=True, blank=True)
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    startdate = models.DateField(null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, default=1)
    profile = models.ImageField(upload_to='media/members/', default='/media/members/avatar.png')
    
    def __str__(self):
        return self.first_name if self.first_name else self.userid.username
    
class Uas_assets_set(models.Model):
    set_name = models.CharField(max_length=255, null=True, blank=True)
    set_purchase = models.DateField(null=True, blank=True)
    on_faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=(('1', 'แสดงผล'), ('2', 'ไม่แสดงผล')) ,default='1')
    
    def __str__(self):
        return self.set_name


class Uas_location(models.Model):
    location_name = models.CharField(max_length=255, null=True, blank=True)
    on_department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return self.location_name


class Uas_status(models.Model):
    status_name = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return self.status_name

class Uas_assets(models.Model):
    asset_code = models.CharField(max_length=255, null=True, blank=True)
    asset_name = models.CharField(max_length=255, null=True, blank=True)
    asset_money = models.CharField(max_length=255, null=True, blank=True)
    asset_group = models.CharField(max_length=255, null=True, blank=True)
    asset_class = models.CharField(max_length=255, null=True, blank=True)
    asset_type = models.CharField(max_length=255, null=True, blank=True)
    asset_amount = models.CharField(max_length=255, null=True, blank=True)
    asset_number = models.CharField(max_length=255, null=True, blank=True)
    asset_purchase = models.DateField(null=True, blank=True)
    asset_value = models.FloatField(null=True, blank=True)
    asset_expire = models.IntegerField(null=True, blank=True)
    asset_img = models.ImageField(upload_to='assets/', null=True, blank=True)
    on_status = models.ForeignKey(Uas_status, on_delete=models.CASCADE)
    on_location = models.ForeignKey(Uas_location, on_delete=models.CASCADE)
    on_set = models.ForeignKey(Uas_assets_set, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.id) + self.asset_name
    
class Uas_Semester(models.Model):
    semester_name = models.CharField(max_length=255, null=True, blank=True)
    semester_year = models.CharField(max_length=255, null=True, blank=True)
    semester_start = models.DateField(null=True, blank=True)
    semester_end = models.DateField(null=True, blank=True)
    semester_number = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=1, choices=(('1', 'แสดงผล'), ('2', 'ไม่แสดงผล')) ,default='1')

    def __str__(self):
        return self.semester_name


class Uas_activity(models.Model):
    activity_name = models.CharField(max_length=255, null=True, blank=True)
    activity_start_date = models.DateField(null=True, blank=True)
    activity_end_date = models.DateField(null=True, blank=True)
    activity_start_time = models.TimeField(null=True, blank=True)
    activity_end_time = models.TimeField(null=True, blank=True)
    allday = models.BooleanField(default=False)
    recur = models.BooleanField(default=False)
    typerecur = models.CharField(max_length=1, choices=(('1', 'ไม่เกิดซ้ำ'), ('2', 'วันละครั้ง'), ('3', 'สัปดาห์ละครั้ง')) ,default='1')
    activity_responsible = models.ForeignKey(UserBio, on_delete=models.CASCADE)
    on_department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    on_location = models.ForeignKey(Uas_location, on_delete=models.CASCADE)
    on_semester = models.ForeignKey(Uas_Semester, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=1, choices=(('1', 'แสดงผล'), ('2', 'ไม่แสดงผล')) ,default='1')

    def __str__(self):
        return self.activity_name

class Uas_department_activity(models.Model):
    on_department = models.ForeignKey(Department, on_delete=models.CASCADE)
    participants = models.IntegerField(null=True, blank=True)
    on_activity = models.ForeignKey(Uas_activity, on_delete=models.CASCADE, null=True, blank=True)
    
class log(models.Model):
    log_date = models.DateTimeField(auto_now_add=True)
    log_user = models.ForeignKey(UserBio, on_delete=models.CASCADE)
    log_detail = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.log_date.strftime('%Y-%m-%d %H:%M:%S') + self.log_user.first_name + ' ' + self.log_user.last_name+ " " + self.log_detail