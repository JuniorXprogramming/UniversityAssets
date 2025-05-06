from django import forms
from uassetsapp.models import *
from django.contrib.auth.models import User

class frmUser(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            "username": forms.TextInput(attrs={'class':'form-control', 'placeholder':'ชื่อผู้ใช้'}),
            "password": forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'รหัสผ่าน'}),
        }

class frmAsset(forms.ModelForm):
    class Meta:
        model = Uas_assets_set
        fields = '__all__'
        widgets = {
            "set_name": forms.TextInput(attrs={'class':'form-control'}),
            "set_purchase": forms.TextInput(attrs={'class':'form-control', 'type':'date', 'id':'d1'}),
            "on_faculty": forms.Select(attrs={'class':'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        user_faculty = kwargs.pop('user_faculty', None)
        super(frmAsset, self).__init__(*args, **kwargs)
        self.fields['on_faculty'].initial = Faculty.objects.get(id=user_faculty)
        self.fields['on_faculty'].disabled = True
        
class frmListAsset(forms.ModelForm):
    RADIO_CHOICES = [
        ('1', 'เพิ่มทีละชิ้น'),
        ('2', 'เพิ่มอัตโนมัติ'),
    ]

    radio_field = forms.ChoiceField(
        choices=RADIO_CHOICES,  # ใช้ choices ไม่ใช่ queryset
        widget=forms.RadioSelect,  # ใช้ RadioSelect widget
        required=True  # ไม่จำเป็นต้องกรอก เพราะไม่เก็บในฐานข้อมูล
    )
    class Meta:
        model = Uas_assets
        fields = ['asset_code', 'asset_name', 'asset_value', 'asset_expire', 'on_status', 'on_location', 'asset_purchase']
        widgets = {
            "asset_code": forms.TextInput(attrs={'class':'form-control', 'required': 'required'}),
            "asset_name": forms.TextInput(attrs={'class':'form-control', 'required': 'required'}),
            "asset_value": forms.NumberInput(attrs={'class':'form-control', 'required': 'required'}),
            "asset_purchase": forms.TextInput(attrs={'class':'form-control', 'type':'date', 'required': 'required', "id":'d1'}),
            "asset_expire": forms.TextInput(attrs={'class':'form-control', 'type':'number', 'required': 'required'}),
            "on_status": forms.Select(attrs={'class':'form-control', 'required': 'required'}),
            "on_location": forms.Select(attrs={'class':'form-control', 'required':'required'}),
        }
        
    def __init__(self, *args, **kwargs):
        department_id = kwargs.pop('department_id', None)
        super(frmListAsset, self).__init__(*args, **kwargs)
        self.fields['on_location'].queryset = Uas_location.objects.filter(on_department=department_id)
        
        
class frmListAssetEdit(forms.ModelForm):
    class Meta:
        model = Uas_assets
        fields = ['asset_code', 'asset_name', 'asset_value', 'asset_expire', 'on_status', 'on_location', "asset_img", 'asset_purchase']
        widgets = {
            "asset_code": forms.TextInput(attrs={'class':'form-control', 'required': 'required'}),
            "asset_name": forms.TextInput(attrs={'class':'form-control', 'required': 'required'}),
            "asset_value": forms.NumberInput(attrs={'class':'form-control', 'required': 'required'}),
            "asset_purchase": forms.TextInput(attrs={'class':'form-control', 'type':'date', 'required': 'required', "id":'d1'}),
            "asset_expire": forms.TextInput(attrs={'class':'form-control', 'type':'number', 'required': 'required'}),
            "on_status": forms.Select(attrs={'class':'form-control', 'required': 'required'}),
            "on_location": forms.Select(attrs={'class':'form-control', 'required':'required'}),
            "asset_img": forms.FileInput(attrs={'class':'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        department_id = kwargs.pop('department_id', None)
        super(frmListAssetEdit, self).__init__(*args, **kwargs)
        self.fields['on_location'].queryset = Uas_location.objects.filter(on_department=department_id)
        
class frmLocation(forms.ModelForm):
    class Meta:
        model = Uas_location
        fields = '__all__'
        widgets = {
            "location_name": forms.TextInput(attrs={'class':'form-control', 'required': 'required'}),
            "on_department": forms.Select(attrs={'class':'form-control', 'required': 'required'}),
        }
        
    def __init__(self, *args, **kwargs):
        user_department = kwargs.pop('user_department', None)
        super(frmLocation, self).__init__(*args, **kwargs)
        self.fields['on_department'].initial = Department.objects.get(id=user_department)
        self.fields['on_department'].disabled = True
        
class frmSemester(forms.ModelForm):
    class Meta:
        model = Uas_Semester
        fields = '__all__'
        widgets = {
            "semester_name": forms.TextInput(attrs={'class':'form-control', 'required': 'required'}),
            "semester_year": forms.TextInput(attrs={'class':'form-control', 'required': 'required'}),
            "semester_start": forms.TextInput(attrs={'class':'form-control', 'type':'date', 'required': 'required', 'id':'d1'}),
            "semester_end": forms.TextInput(attrs={'class':'form-control', 'type':'date', 'required': 'required', 'id':'d2'}),
            "semester_number": forms.TextInput(attrs={'class':'form-control', 'required': 'required'}),
        }
        
class frmStatus(forms.ModelForm):
    class Meta:
        model = Uas_status
        fields = '__all__'
        widgets = {
            "status_name": forms.TextInput(attrs={'class':'form-control', 'required': 'required'}),
        }
        
class frmActivity(forms.ModelForm):
    class Meta:
        model = Uas_activity
        fields = '__all__'
        widgets = {
            "activity_name": forms.TextInput(attrs={'class':'form-control', 'required': 'required'}),
            "activity_start_date": forms.TextInput(attrs={'class':'form-control', 'type':'date', 'required': 'required', 'id':'d1'}),
            'activity_end_date': forms.TextInput(attrs={'class':'form-control', 'type':'date', 'required': 'required', 'id':'d2'}),
            'activity_start_time': forms.TextInput(attrs={'class':'form-control', 'type':'time', 'disabled': 'disabled'}),
            'activity_end_time': forms.TextInput(attrs={'class':'form-control', 'type':'time', 'disabled': 'disabled'}),
            'allday': forms.CheckboxInput(attrs={'class':'form-check-input', 'checked': 'checked'}),
            'recur': forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'typerecur': forms.Select(attrs={'class':'form-control', 'disabled': 'disabled'}),
            "activity_responsible": forms.Select(attrs={'class':'form-control', 'required': 'required'}),
            "on_department": forms.Select(attrs={'class':'form-control', 'required': 'required'}),
            "on_location": forms.Select(attrs={'class':'form-control', 'required': 'required'}),
            'on_semester': forms.Select(attrs={'class':'form-control', 'required': 'required'}),
        }
        
    def __init__(self, *args, **kwargs):
        date = kwargs.pop('date', None)
        super(frmActivity, self).__init__(*args, **kwargs)
        if date:
            spl_date = date.split(',')
            self.fields['activity_start_date'].initial = spl_date[0]
            self.fields['on_semester'].queryset = Uas_Semester.objects.filter(status='1')
            self.fields['on_location'].queryset = Uas_location.objects.filter(on_department__id=spl_date[1])
            self.fields['on_department'].initial = Department.objects.get(id=spl_date[1])
            self.fields['on_department'].disabled = True
            self.fields['activity_responsible'].queryset = UserBio.objects.filter(department__id=spl_date[1])
            
class frmEditActivity(forms.ModelForm):
    class Meta:
        model = Uas_activity
        fields = '__all__'
        widgets = {
            "activity_name": forms.TextInput(attrs={'class':'form-control', 'required': 'required'}),
            "activity_start_date": forms.TextInput(attrs={'class':'form-control', 'type':'date', 'required': 'required', 'id':'d1'}),
            'activity_end_date': forms.TextInput(attrs={'class':'form-control', 'type':'date', 'required': 'required', 'id':'d2'}),
            'activity_start_time': forms.TextInput(attrs={'class':'form-control', 'type':'time', 'disabled': 'disabled'}),
            'activity_end_time': forms.TextInput(attrs={'class':'form-control', 'type':'time', 'disabled': 'disabled'}),
            'allday': forms.CheckboxInput(attrs={'class':'form-check-input', 'checked': 'checked'}),
            'recur': forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'typerecur': forms.Select(attrs={'class':'form-control', 'disabled': 'disabled'}),
            "activity_responsible": forms.Select(attrs={'class':'form-control', 'required': 'required'}),
            "on_department": forms.Select(attrs={'class':'form-control', 'required': 'required'}),
            "on_location": forms.Select(attrs={'class':'form-control', 'required': 'required'}),
            'on_semester': forms.Select(attrs={'class':'form-control', 'required': 'required'}),
        }
        
    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop('user_id', None)
        super(frmEditActivity, self).__init__(*args, **kwargs)
        self.fields['on_semester'].queryset = Uas_Semester.objects.filter(status='1')
        self.fields['on_location'].queryset = Uas_location.objects.filter(on_department__id=user_id)
        self.fields['on_department'].initial = Department.objects.get(id=user_id)
        self.fields['on_department'].disabled = True
        self.fields['activity_responsible'].queryset = UserBio.objects.filter(department__id=user_id)

        
class frmDepartmentActivity(forms.ModelForm):
    class Meta:
        model = Uas_department_activity
        fields = '__all__'
        widgets = {
            'on_department': forms.Select(attrs={'class':'form-control'}),
            'participants': forms.NumberInput(attrs={'class':'form-control'}),
            'on_activity': forms.Select(attrs={'class':'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        activity_id = kwargs.pop('activity_id', None)
        super(frmDepartmentActivity, self).__init__(*args, **kwargs)
        self.fields['on_activity'].initial = Uas_activity.objects.get(id=activity_id)
        self.fields['on_activity'].disabled = True
        
