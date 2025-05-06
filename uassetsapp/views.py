from django.shortcuts import render, redirect
from django.http import HttpResponse
from uassetsapp.models import *
from django.db.models import Sum
from uassetsapp.forms import *
from django.http import JsonResponse
import datetime
import math
import csv
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from io import BytesIO, StringIO
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.templatetags.static import static
import os
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404


# Create your views here.
month_th_set = ['มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน', 'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม']
#Additional Function
def context_data(request):
    fullpath = request.get_full_path()
    abs_uri = request.build_absolute_uri()
    abs_uri = abs_uri.split(fullpath)[0]
    context = {
        'system_host' : abs_uri,
        'page_name' : 'Home',
        'page_title' : 'Rims',
        'system_name' : 'RIMS:ระบบจัดการข้อมูลวิจัยและนวัตกรรม',
        'topbar' : True,
        'footer' : True,
    }
    return context

def check_permission(user):
    if user.is_superuser:
        return redirect('/admin/')
    return redirect('asset_page')

def add_years(date, years):
    try:
        # พยายามเพิ่มปีให้กับวันที่
        return date.replace(year=date.year + years)
    except ValueError:
        # ถ้าปีใหม่มีวันที่ไม่ถูกต้อง (เช่น 29 กุมภาพันธ์ในปีที่ไม่ใช่ปีอธิกสุรทิน)
        return date.replace(year=date.year + years, day=date.day - 1)

#end Additional Function
def homepage(request):
    if request.user.is_authenticated:
        return check_permission(request.user)
    
    if request.method == 'POST':
        form = frmUser(request.POST)
        username = request.POST.get('username') 
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back {username}")
            return check_permission(user)
        else:
            messages.error(request, "Invalid username or password.")
                
    form = frmUser()
    context = context_data(request)
    context['form'] = form
    return render(request, 'homepage.html', context)

def logout_request(request):
    if request.user.is_authenticated:  # ✅ ตรวจสอบก่อนว่าผู้ใช้ล็อกอินอยู่
        try:
            user_bio = get_object_or_404(UserBio, userid=request.user.id)
            log.objects.create(log_user=user_bio, log_detail='logout success')
        except UserBio.DoesNotExist:
            pass  # หรือจะ log ข้อผิดพลาดก็ได้
    
    logout(request)  # ✅ ทำ logout หลังจาก log
    return redirect("homepage")


#Asset Function
@login_required
def asset_page(request):
    context = context_data(request)
    try:
        userid = request.user.id
        user_bio = UserBio.objects.get(userid=userid)
        user_faculty, user_department = user_bio.department.faculty, user_bio.department.departmentname
        asset_set_count, asset_data, total_value = Uas_assets_set.objects.filter(status='1').count(), Uas_assets_set.objects.filter(on_faculty=user_faculty, status='1'), 0
        total_value = sum([Uas_assets.objects.filter(on_set=row.id).aggregate(Sum('asset_value')).get('asset_value__sum') or 0 for row in asset_data])
        asset_final_data = [
            {
                "data": row,
                "asset_value": Uas_assets.objects.filter(on_set=row).aggregate(Sum('asset_value')).get('asset_value__sum') or 0,
                "asset_purchase" : row.set_purchase.strftime('%d') + ' ' + month_th_set[int(row.set_purchase.strftime('%m'))-1] + ' ' + str(int(row.set_purchase.strftime('%Y'))+543)
            } 
            for row in asset_data]
        context['asset_set_count'] = asset_set_count
        context['asset_value'] = total_value
        context['asset_data'] = asset_final_data
        context['permission'] = 0 if user_department.strip() != "สำนักงานคณบดี" else 1
        log.objects.create(log_user=UserBio.objects.get(userid=userid), log_detail='access asset page')
    except ObjectDoesNotExist:
        messages.error(request, "ไม่พบข้อมูลของผู้ใช้")
        return redirect('homepage')
    return render(request, 'asset_page.html', context)

@login_required
def asset_add(request):
    try:
        user_bio = UserBio.objects.get(userid=request.user.id)
        user_department = user_bio.department.departmentname
        user_faculty_id = user_bio.department.faculty.id
        if user_department.strip() != "สำนักงานคณบดี":
            messages.error(request, "คุณไม่มีสิทธิ์การเข้าถึง")
            return redirect('asset_page')
        if request.method == 'POST':
            data = request.POST.copy()
            data['status'] = '1'
            frm = frmAsset(data, user_faculty=user_faculty_id)
            if frm.is_valid():
                frm.save()
                log.objects.create(log_user=user_bio, log_detail='add asset')
                return redirect('asset_page')
        context = context_data(request)
        context['frm'] = frmAsset(user_faculty=user_faculty_id)
        log.objects.create(log_user=user_bio, log_detail='access add asset page')
    except ObjectDoesNotExist:
        messages.error(request, "User data does not exist.")
        return redirect('homepage')
    return render(request, 'asset_add.html', context)

@login_required
def asset_edit(request, id):
    try:
        user_bio = UserBio.objects.get(userid=request.user.id)
        user_department = user_bio.department.departmentname
        user_faculty_id = user_bio.department.faculty.id
        if user_department.strip() != "สำนักงานคณบดี":
            messages.error(request, "คุณไม่มีสิทธิ์การเข้าถึง")
            return redirect('asset_page')
        asset = Uas_assets_set.objects.get(id=id)
        if request.method == 'POST':
            data = request.POST.copy()
            data['status'] = '1'
            frm = frmAsset(data, instance=asset, user_faculty=user_faculty_id)
            if frm.is_valid():
                frm.save()
                log.objects.create(log_user=user_bio, log_detail='edit asset')
                return redirect('asset_page')
        context = context_data(request)
        context['frm'] = frmAsset(instance=asset, user_faculty=user_faculty_id)
        log.objects.create(log_user=user_bio, log_detail='access edit asset page')
    except ObjectDoesNotExist:
        messages.error(request, "ข้อมูลผู้ใช้ไม่มีอยู่ หรือ ข้อมูลครุภัณฑ์ไม่มีอยู่")
        return redirect('asset_page')
    return render(request, 'asset_edit.html', context)

@login_required
def asset_delete(request, id):
    try:
        user_bio = UserBio.objects.get(userid=request.user.id)
        user_department = user_bio.department.departmentname
        if user_department.strip() != "สำนักงานคณบดี":
            messages.error(request, "คุณไม่มีสิทธิ์ลบข้อมูล")
            return redirect('asset_page')
        asset = Uas_assets_set.objects.get(id=id)
        asset.status = '2'
        asset.save()
        log.objects.create(log_user=user_bio, log_detail='delete asset')
    except ObjectDoesNotExist:
        messages.error(request, "ข้อมูลผู้ใช้ไม่มีอยู่ หรือ ข้อมูลครุภัณฑ์ไม่มีอยู่")
    return redirect('asset_page')

#end Asset Function

#List Asset Function
@login_required
def list_asset(request, id):
    try:
        user_bio = UserBio.objects.get(userid=request.user.id)
        department = user_bio.department.departmentname
        list_asset = Uas_assets.objects.filter(on_set=id, on_location__on_department__departmentname=department)
        for asset in list_asset:
            asset.date_expire = add_years(asset.asset_purchase, int(asset.asset_expire))
            asset.asset_purchase = asset.asset_purchase.strftime('%d') + ' ' + month_th_set[int(asset.asset_purchase.strftime('%m')) - 1] + ' ' + str(int(asset.asset_purchase.strftime('%Y'))+543)
            asset.date_expire = asset.date_expire.strftime('%d') + ' ' + month_th_set[int(asset.date_expire.strftime('%m')) - 1] + ' ' + str(int(asset.date_expire.strftime('%Y'))+543)
        context = context_data(request)
        context['list_asset'] = list_asset
        context['asset_id'] = id
        log.objects.create(log_user=user_bio, log_detail='access list asset')
    except ObjectDoesNotExist:
        messages.error(request, "ข้อมูลผู้ใช้ไม่มีอยู่ หรือ ข้อมูลครุภัณฑ์ไม่มีอยู่")
        return redirect('asset_page')
    except Exception as e:
        messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
        return redirect('asset_page')
    return render(request, 'list_asset.html', context)

@login_required
def list_asset_add(request, id):
    try:
        row = Uas_assets_set.objects.get(id=id)
        department_id = UserBio.objects.get(userid=request.user.id).department.id
        if request.method == 'POST':
            if request.POST.get('radio_field') == "1":
                data = request.POST.copy()
                frm = frmListAsset(data, department_id=department_id)
                if frm.is_valid():
                    asset_code = request.POST.get('asset_code').split('/')
                    asset_money, asset_group, asset_class, asset_type, asset_amount, asset_number = asset_code[0].split(" ")[0], asset_code[0].split(" ")[1].split("-")[0][0:2], asset_code[0].split(" ")[1].split("-")[0][2:], asset_code[0].split(" ")[1].split("-")[1], asset_code[1].split("-")[0], asset_code[1].split("-")[1]
                    asset_purchase, on_set = data['asset_purchase'], Uas_assets_set.objects.get(id=id)
                    asset_instance = frm.save(commit=False)
                    asset_instance.asset_money, asset_instance.asset_group, asset_instance.asset_class, asset_instance.asset_type, asset_instance.asset_amount, asset_instance.asset_number, asset_instance.asset_purchase, asset_instance.on_set = asset_money, asset_group, asset_class, asset_type, asset_amount, asset_number, asset_purchase, on_set
                    asset_instance.save()
                    log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='add list asset')
                    return redirect('list_asset', id=id)
            else:
                asset_code = request.POST.get('asset_code').split('/')
                asset_amount, asset_number = int(asset_code[1].split("-")[0]), int(asset_code[1].split("-")[1])
                for i in range(int(asset_amount)):
                    data = request.POST.copy()
                    frm = frmListAsset(data, department_id=department_id)
                    if frm.is_valid():
                        asset_code = request.POST.get('asset_code').split('/')
                        asset_money, asset_group, asset_class, asset_type, asset_amount, asset_number = asset_code[0].split(" ")[0], asset_code[0].split(" ")[1].split("-")[0][0:2], asset_code[0].split(" ")[1].split("-")[0][2:], asset_code[0].split(" ")[1].split("-")[1], asset_code[1].split("-")[0], asset_code[1].split("-")[1]
                        asset_purchase, on_set = data['asset_purchase'], Uas_assets_set.objects.get(id=id)
                        asset_instance = frm.save(commit=False)
                        asset_code_to_save = f'{asset_money} {asset_group}{asset_class}-{asset_type}-{asset_code[0].split(" ")[1].split("-")[2]}/{asset_amount}-{int(asset_number)+i}-{asset_code[1].split("-")[2]}'
                        asset_instance.asset_code, asset_instance.asset_money, asset_instance.asset_group, asset_instance.asset_class, asset_instance.asset_type, asset_instance.asset_amount, asset_instance.asset_number, asset_instance.asset_purchase, asset_instance.on_set = asset_code_to_save, asset_money, asset_group, asset_class, asset_type, asset_amount, int(asset_number)+i, asset_purchase, on_set
                        asset_instance.save()
                        log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='add list asset')
                return redirect('list_asset', id=id)
        context = context_data(request)
        context['frm'] = frmListAsset(department_id=department_id)
        log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='access add list asset page')
    except ObjectDoesNotExist:
        messages.error(request, "ข้อมูลผู้ใช้ไม่มีอยู่ หรือ ข้อมูลรายการครุภัณฑ์ไม่มีอยู่")
        return redirect('asset_page')
    except Exception as e:
        messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
        return redirect('asset_page')
    return render(request, 'list_asset_add.html', context)

@login_required
def list_asset_edit(request, id):
    try:
        department_id = UserBio.objects.get(userid=request.user.id).department.id
        asset = Uas_assets.objects.get(id=id)
        if request.method == 'POST':
            data = request.POST.copy()
            frm = frmListAssetEdit(data, request.FILES, instance=asset, department_id=department_id)
            if frm.is_valid():
                print(request.POST['asset_purchase'])
                asset_code = request.POST.get('asset_code').split('/')
                asset_money, asset_group, asset_class, asset_type, asset_amount, asset_number = asset_code[0].split(" ")[0], asset_code[0].split(" ")[1].split("-")[0][0:2], asset_code[0].split(" ")[1].split("-")[0][2:], asset_code[0].split(" ")[1].split("-")[1], asset_code[1].split("-")[0], asset_code[1].split("-")[1]
                asset_purchase, on_set = data['asset_purchase'], Uas_assets_set.objects.get(id=asset.on_set.id)
                asset_instance = frm.save(commit=False)
                asset_code_to_save = f'{asset_money} {asset_group}{asset_class}-{asset_type}-{asset_code[0].split(" ")[1].split("-")[2]}/{asset_amount}-{int(asset_number)}-{asset_code[1].split("-")[2]}'
                asset_instance.asset_money, asset_instance.asset_group, asset_instance.asset_class, asset_instance.asset_type, asset_instance.asset_amount, asset_instance.asset_number, asset_instance.asset_purchase, asset_instance.on_set = asset_money, asset_group, asset_class, asset_type, asset_amount, asset_number, asset_purchase, on_set
                asset_instance.save()
                log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='edit list asset')
                return redirect('list_asset', id=asset.on_set.id)
        frm = frmListAssetEdit(instance=asset, department_id=department_id)
        context = context_data(request)
        context['frm'] = frm
        log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='access edit list asset page')
    except ObjectDoesNotExist:
        messages.error(request, "ข้อมูลผู้ใช้ไม่มีอยู่ หรือ ข้อมูลรายการครุภัณฑ์ไม่มีอยู่")
        return redirect('asset_page')
    except Exception as e:
        messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
        return redirect('asset_page')
    return render(request, 'list_asset_edit.html', context)
        
@login_required
def list_asset_delete(request, id):
    try:
        department = UserBio.objects.get(userid=request.user.id).department.departmentname
        asset = Uas_assets.objects.get(id=id)
        if department != asset.on_location.on_department.departmentname:
            messages.error(request, "คุณไม่มีสิทธิ์การเข้าถึง")
            return redirect('asset_page')
        asset.delete()
        log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='delete list asset')
    except ObjectDoesNotExist:
        messages.error(request, "ข้อมูลผู้ใช้ไม่มีอยู่ หรือ ข้อมูลรายการครุภัณฑ์ไม่มีอยู่")
        return redirect('asset_page')
    except Exception as e:
        messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
        return redirect('asset_page')
    return redirect('list_asset', id=asset.on_set.id)

#end List Asset Function

#Activity Function
@login_required
def activity_page(request):
    log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='access activity page')
    return render(request, 'activity_page.html')

def activity_list(request):
    try:
        department = UserBio.objects.get(userid=request.user.id).department.departmentname
        activity = Uas_department_activity.objects.filter(on_department__departmentname=department, on_activity__status='1')
        data = []
        number_weekday = {
            'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 0
        }
        # ตัวจัดการ recurrence
        typerecur = {
            '1': [],  # Non-recurrence (ไม่มีการเกิดซ้ำ)
            '2': [0, 1, 2, 3, 4, 5, 6],  # Recurs every day
        }

        for row in activity:
            # สำหรับ Non-recurrence ให้ daysOfWeek เป็น [] หรือไม่ต้องส่งไปเลย
            if row.on_activity.typerecur == '3':
                days_of_week = [number_weekday[row.on_activity.activity_start_date.strftime('%A')]]
            else:
                days_of_week = typerecur.get(row.on_activity.typerecur, [])

            event = {
                'id': row.on_activity.id,
                'title': row.on_activity.activity_name,
                'color': '#dc3545' if row.on_activity.allday else '#17a2b8',
                'allDay': row.on_activity.allday,
            }

            # ถ้าเป็น Non-recurrence
            if row.on_activity.typerecur == '1':  # Non-recurrence
                event.update({
                    'start': row.on_activity.activity_start_date.strftime('%Y-%m-%d'),
                    'end': row.on_activity.activity_end_date.strftime('%Y-%m-%d'),
                })
            else:
                # สำหรับ Recurrence
                event.update({
                    'startRecur': row.on_activity.activity_start_date.strftime('%Y-%m-%d'),
                    'endRecur': row.on_activity.activity_end_date.strftime('%Y-%m-%d'),
                    'daysOfWeek': days_of_week,  # กรณี recurrence
                    'startTime': row.on_activity.activity_start_time.strftime('%H:%M') if row.on_activity.activity_start_time else None,
                    'endTime': row.on_activity.activity_end_time.strftime('%H:%M') if row.on_activity.activity_end_time else None,
                })

            data.append(event)
            print(data)

        return JsonResponse(data, safe=False)
    except ObjectDoesNotExist:
        messages.error(request, "ข้อมูลผู้ใช้ไม่มีอยู่ หรือ ข้อมูลกิจกรรมไม่มีอยู่")
        return redirect('activity_page')
    except Exception as e:
        messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
        return redirect('activity_page')

@login_required
def activity_add(request, date):
    department_user = UserBio.objects.get(userid=request.user.id).department.id
    date = f'{date},{department_user}'
    if request.method == 'POST':
        all_day = 1 if request.POST.get('allday') == "on" else 0
        recur = 1 if request.POST.get('recur') == "on" else 0
        typerecur = request.POST.get('typerecur') if request.POST.get('typerecur') else '1'
        status = '1'
        data = request.POST.copy()
        data['allday'], data['recur'], data['typerecur'], data['status'] = all_day, recur, typerecur, status
        frm = frmActivity(data, date=date)
        if frm.is_valid():
            activity_instance = frm.save(commit=False)
            activity_instance.save()
            frmdepartment = frmDepartmentActivity(activity_id=frm.instance.id)
            frmdepartment_instance = frmdepartment.save(commit=False)
            frmdepartment_instance.participants = 0
            frmdepartment_instance.on_department = UserBio.objects.get(userid=request.user.id).department
            frmdepartment_instance.on_activity = activity_instance
            frmdepartment_instance.save()
            log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='add activity')
        return redirect('activity_page')
    frm = frmActivity(date=date)
    context = context_data(request)
    context['date'] = date
    context['frm'] = frm
    log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='access add activity page')
    return render(request, 'activity_add.html', context)

@login_required
def activity_edit(request, id):
    try:
        department_name = UserBio.objects.get(userid=request.user.id).department.id
        department = UserBio.objects.get(userid=request.user.id).department.departmentname
        activity = Uas_activity.objects.get(id=id)
        if department != activity.on_location.on_department.departmentname:
            messages.error(request, "คุณไม่มีสิทธิ์การเข้าถึง")
            return redirect('activity_page')
        if request.method == 'POST':
            all_day = 1 if request.POST.get('allday') == "on" else 0
            recur = 1 if request.POST.get('recur') == "on" else 0
            typerecur = request.POST.get('typerecur') if request.POST.get('typerecur') else '1'
            status = '1'
            data = request.POST.copy()
            data['allday'], data['recur'], data['typerecur'], data['status'] = all_day, recur, typerecur, status
            frm = frmEditActivity(data, instance=activity, user_id=department_name)
            if frm.is_valid():
                frm.save()
                log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='edit activity')
                return redirect('activity_page')
            else:
                print(frm.errors)
        frm = frmEditActivity(instance=activity, user_id=department_name)
        context = context_data(request)
        context['frm'] = frm
        context['activity_id'] = id    
        log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='access edit activity page')
    except ObjectDoesNotExist:
        messages.error(request, "ข้อมูลผู้ใช้ไม่มีอยู่ หรือ ข้อมูลกิจกรรมไม่มีอยู่")
        return redirect('activity_page')
    except Exception as e:
        messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
        return redirect('activity_page')
    return render(request, 'activity_edit.html', context)

@login_required
def activity_delete(request, id):
    try:
        activity = Uas_activity.objects.get(id=id)
        department = UserBio.objects.get(userid=request.user.id).department.departmentname
        if department != activity.on_location.on_department.departmentname:
            messages.error(request, "คุณไม่มีสิทธิ์การเข้าถึง")
            return redirect('activity_page')
        activity.status = '2'
        activity.save()
        log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='delete activity')
    except ObjectDoesNotExist:
        messages.error(request, "ข้อมูลผู้ใช้ไม่มีอยู่ หรือ ข้อมูลกิจกรรมไม่มีอยู่")
        return redirect('activity_page')
    except Exception as e:
        messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
        return redirect('activity_page')
    return redirect('activity_page')

@login_required
def activity_detail(request, id):
    try:
        department = UserBio.objects.get(userid=request.user.id).department.departmentname
        activity = Uas_activity.objects.get(id=id)
        av_asset, nav_asset, maintain_asset = Uas_assets.objects.filter(on_location=activity.on_location, on_status__id=1).count(), Uas_assets.objects.filter(on_location=activity.on_location, on_status__id=2).count(), Uas_assets.objects.filter(on_location=activity.on_location, on_status__id=3).count()
        list_asset = Uas_assets.objects.filter(on_location=activity.on_location, on_status__id=1)
        for asset in list_asset:
            asset.date_expire = add_years(asset.asset_purchase, int(asset.asset_expire))
            asset.asset_purchase = asset.asset_purchase.strftime('%d') + ' ' + month_th_set[int(asset.asset_purchase.strftime('%m')) - 1] + ' ' + str(int(asset.asset_purchase.strftime('%Y'))+543)
            asset.date_expire = asset.date_expire.strftime('%d') + ' ' + month_th_set[int(asset.date_expire.strftime('%m')) - 1] + ' ' + str(int(asset.date_expire.strftime('%Y'))+543)
        total_value= Uas_assets.objects.filter(on_location=activity.on_location, on_status__id=1).aggregate(Sum('asset_value')).get('asset_value__sum') or 0
        start, end = activity.activity_start_date, activity.activity_end_date
        start_timestamp, end_timestamp = datetime.datetime.combine(start, datetime.time.min).timestamp(), datetime.datetime.combine(end, datetime.time.min).timestamp()
        if activity.typerecur == '1':
            count_occur = 1
        elif activity.typerecur == '2':
            count_occur = math.floor((end_timestamp - start_timestamp) / 3600 / 24)
        elif activity.typerecur == '3':
            count_occur = math.floor((end_timestamp - start_timestamp) / 3600 / 24 / 7)
        if activity.allday == 0:
            start_time_timestamp, end_time_timestamp = datetime.datetime.combine(start, activity.activity_start_time).timestamp(), datetime.datetime.combine(start, activity.activity_end_time).timestamp()
            hour = math.floor((end_time_timestamp - start_time_timestamp) / 3600 * count_occur)
        else:
            hour = count_occur * 24
        total_participant = Uas_department_activity.objects.filter(on_activity=activity).aggregate(Sum('participants')).get('participants__sum') or 0
        department_participant = Uas_department_activity.objects.filter(on_activity=activity)
        context = context_data(request)
        context['firstrow'] = {"av": av_asset, "nav": nav_asset, "maintain": maintain_asset, "cost_per_hour": '{:.2f}'.format(total_value/hour)}
        context['data'] = list_asset
        context['lastrow'] = {"total_participants": total_participant, "responsible": activity.activity_responsible.first_name + ' ' + activity.activity_responsible.last_name}
        context['activity_id'] = id
        context['department_participant'] = [{'department': row, 'cost_per_department': "{:.2f}".format(int(row.participants) * (total_value/hour))} for row in department_participant]
        context['permission'] = 0 if department != activity.on_location.on_department.departmentname else 1
        log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='access activity detail page')
    except ObjectDoesNotExist:
        messages.error(request, "ข้อมูลผู้ใช้ไม่มีอยู่ หรือ ข้อมูลกิจกรรมไม่มีอยู่")
        return redirect('activity_page')
    except Exception as e:
        messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
        return redirect('activity_page')
    return render(request, 'activity_detail.html', context)

#end Activity Function

#Location Function
@login_required
def location_page(request):
    try:
        department = UserBio.objects.get(userid=request.user.id).department.departmentname
        location = Uas_location.objects.filter(on_department__departmentname=department)
        context = context_data(request)
        context['location'] = location
        log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='access location page')
    except ObjectDoesNotExist:
        messages.error(request, "ข้อมูลผู้ใช้ไม่มีอยู่ หรือ ข้อมูลสถานที่ไม่มีอยู่")
        return redirect('homepage')
    except Exception as e:
        messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
        return redirect('homepage')
    return render(request, 'location_page.html', context)

@login_required
def location_add(request):
    try:
        user_department = UserBio.objects.get(userid=request.user.id).department.id
        if request.method == 'POST':
            frm = frmLocation(request.POST, user_department=user_department)
            if frm.is_valid():
                frm.save()
                log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='add location')
                return redirect('location_page')
        frm = frmLocation(user_department=user_department)
        context = context_data(request)
        context['frm'] = frm
        log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='access add location page')
    except ObjectDoesNotExist:
        messages.error(request, "ข้อมูลผู้ใช้ไม่มีอยู่")
        return redirect('homepage')
    except Exception as e:
        messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
        return redirect('homepage')
    return render(request, 'location_add.html', context)

@login_required
def location_edit(request, id):
    try:
        department = UserBio.objects.get(userid=request.user.id).department.departmentname
        user_department = UserBio.objects.get(userid=request.user.id).department.id
        location = Uas_location.objects.get(id=id)
        if department != location.on_department.departmentname:
            messages.error(request, "คุณไม่มีสิทธิ์การเข้าถึง")
            log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='access location page')
            return redirect('location_page')
        if request.method == 'POST':
            frm = frmLocation(request.POST, instance=location, user_department=user_department)
            if frm.is_valid():
                frm.save()
                return redirect('location_page')
        frm = frmLocation(instance=location, user_department=user_department)
        context = context_data(request)
        context['frm'] = frm
        log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='access edit location page')
    except ObjectDoesNotExist:
        messages.error(request, "ข้อมูลผู้ใช้ไม่มีอยู่ หรือ ข้อมูลสถานที่ไม่มีอยู่")
        return redirect('location_page')
    except Exception as e:
        messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
        return redirect('location_page')
    return render(request, 'location_edit.html', context)

@login_required
def location_delete(request, id):
    try:
        department = UserBio.objects.get(userid=request.user.id).department.departmentname
        location = Uas_location.objects.get(id=id)
        if department != location.on_department.departmentname:
            messages.error(request, "คุณไม่มีสิทธิ์การเข้าถึง")
            return redirect('location_page')
        location.delete()
        log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='delete location')
    except ObjectDoesNotExist:
        messages.error(request, "ข้อมูลผู้ใช้ไม่มีอยู่ หรือ ข้อมูลสถานที่ไม่มีอยู่")
        return redirect('location_page')
    except Exception as e:
        messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
        return redirect('location_page')
    return redirect('location_page')

#end Location Function

#Semester Function
@login_required
def semester_page(request):
    department = UserBio.objects.get(userid=request.user.id).department.departmentname
    semester = Uas_Semester.objects.filter(status='1')
    for s in semester:
        s.semester_start = s.semester_start.strftime('%d') + ' ' + month_th_set[int(s.semester_start.strftime('%m'))-1] + ' ' + str(int(s.semester_start.strftime('%Y'))+543)
        s.semester_end = s.semester_end.strftime('%d') + ' ' + month_th_set[int(s.semester_end.strftime('%m'))-1] + ' ' + str(int(s.semester_end.strftime('%Y'))+543)
    context = context_data(request)
    context['semester'] = semester
    context['permission'] = 0 if department.strip() != "สำนักงานคณบดี" else 1
    log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='access semester page')
    return render(request, 'semester_page.html', context)

@login_required
def semester_add(request):
    department = UserBio.objects.get(userid=request.user.id).department.departmentname
    if department.strip() != "สำนักงานคณบดี":
        messages.error(request, "คุณไม่มีสิทธิ์การเข้าถึง")
        return redirect('semester_page')
    if request.method == 'POST':
        data = request.POST.copy()
        data['status'] = '1'
        frm = frmSemester(data)
        if frm.is_valid():
            frm.save()
            log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='add semester')
            return redirect('semester_page')
    frm = frmSemester()
    context = context_data(request)
    context['frm'] = frm
    log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='access add semester page')
    return render(request, 'semester_add.html', context)

@login_required
def semester_edit(request, id):
    try:
        department = UserBio.objects.get(userid=request.user.id).department.departmentname
        if department.strip() != "สำนักงานคณบดี":
            messages.error(request, "คุณไม่มีสิทธิ์การเข้าถึง")
            return redirect('semester_page')
        semester = Uas_Semester.objects.get(id=id)
        if request.method == 'POST':
            data = request.POST.copy()
            data['status'] = '1'
            frm = frmSemester(data, instance=semester)
            if frm.is_valid():
                frm.save()
                log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='edit semester')
                return redirect('semester_page')
        context = context_data(request)
        context['frm'] = frmSemester(instance=semester)
        log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='access edit semester page')
    except ObjectDoesNotExist:
        messages.error(request, "ข้อมูลผู้ใช้ไม่มีอยู่ หรือ ข้อมูลภาคเรียนไม่มีอยู่")
    except Exception as e:
        messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
        return redirect('semester')
    return render(request, 'semester_edit.html', context)

@login_required
def semester_delete(request, id):
    try:
        department = UserBio.objects.get(userid=request.user.id).department.departmentname
        if department.strip() != "สำนักงานคณบดี":
            messages.error(request, "คุณไม่มีสิทธิ์การเข้าถึง")
            return redirect('semester_page')
        semester = Uas_Semester.objects.get(id=id)
        semester.status = '2'
        semester.save()
        log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='delete semester')
    except ObjectDoesNotExist:
        messages.error(request, "ข้อมูลผู้ใช้ไม่มีอยู่ หรือ ข้อมูลภาคเรียนไม่มีอยู่")
    except Exception as e:
        messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
    return redirect('semester_page')
    

#end Semester Function

#Status list Asset Function

@login_required
def status_page(request):
    status = Uas_status.objects.all()
    context = context_data(request)
    context['status'] = status
    log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='access status page')
    return render(request, 'status_page.html', context)

@login_required
def status_add(request):
    if request.method == 'POST':
        frm = frmStatus(request.POST)
        if frm.is_valid():
            frm.save()
            log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='add status')
            return redirect('status_page')
    context = context_data(request)
    context['frm'] = frmStatus()
    log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='access add status page')
    return render(request, 'status_add.html', context)

@login_required
def status_edit(request, id):
    try:
        row = Uas_status.objects.get(id=id)
        if request.method == 'POST':
            frm = frmStatus(request.POST, instance=row)
            if frm.is_valid():
                frm.save()
                log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='edit status')
                return redirect('status_page')
        frm = frmStatus(instance=row)
        context = context_data(request)
        context['frm'] = frm
        log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='access edit status page')
    except ObjectDoesNotExist:
        messages.error(request, "ข้อมูลผู้ใช้ไม่มีอยู่ หรือ ข้อมูลสถานะไม่มีอยู่")
        return redirect('status_page')
    except Exception as e:
        messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
        return redirect('status_page')
    return render(request, 'status_edit.html', context)

@login_required
def status_delete(request, id):
    try:
        row = Uas_status.objects.get(id=id)
        row.delete()
        log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='delete status')
    except ObjectDoesNotExist:
        messages.error(request, "ข้อมูลผู้ใช้ไม่มีอยู่ หรือ ข้อมูลสถานะไม่มีอยู่")
    return redirect('status_page')

#end Status list Asset Function

#report Function
@login_required
def report_data(request, id):
    try:
        department = UserBio.objects.get(userid=request.user.id).department.departmentname
        semester, semester_year = Uas_Semester.objects.get(id=id), Uas_Semester.objects.get(id=id).semester_year
        if department.strip() != "สำนักงานคณบดี":
            activity = Uas_activity.objects.filter(on_semester__semester_year=semester_year, on_location__on_department__departmentname=department)
        else:
            activity = Uas_activity.objects.filter(on_semester__semester_year=semester_year)
        total_hour = 0
        data = []
        for a in activity:
            start, end = a.activity_start_date, a.activity_end_date
            start_timestamp, end_timestamp = datetime.datetime.combine(start, datetime.time.min).timestamp(), datetime.datetime.combine(end, datetime.time.min).timestamp()
            if a.typerecur == '1':
                count_occur = 1
            elif a.typerecur == '2':
                count_occur = math.floor((end_timestamp - start_timestamp) / 3600 / 24)
            elif a.typerecur == '3':
                count_occur = math.floor((end_timestamp - start_timestamp) / 3600 / 24 / 7)
            if a.allday == 0:
                start_time_timestamp, end_time_timestamp = datetime.datetime.combine(start, a.activity_start_time).timestamp(), datetime.datetime.combine(start, a.activity_end_time).timestamp()
                hour = math.floor((end_time_timestamp - start_time_timestamp) / 3600 * count_occur)
            else:
                hour = count_occur * 24
            total_hour += hour
            data.append({
                'asset_data' : Uas_assets.objects.filter(on_location=a.on_location, on_status__id=1),
                'activity' : a.activity_name,
            })
    except ObjectDoesNotExist:
        messages.error(request, "ข้อมูลผู้ใช้ไม่มีอยู่ หรือ ข้อมูลกิจกรรมไม่มีอยู่")
        return redirect('activity_page')
    except Exception as e:
        messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
        return redirect('activity_page')
    return [data, total_hour]


@login_required
def report_page(request):
    context = context_data(request)
    context['data'] = Uas_Semester.objects.filter(status='1')
    log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='access report page')
    return render(request, 'report_page.html', context)

@login_required
def generate_report(request, id):
    try:
        data, total_hour = report_data(request, id)[0], report_data(request, id)[1]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="report_{id}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Asset Code', 'Asset Name', 'Asset Value', 'Location', 'Status', 'Total Hour', 'Cost Per Hour', "Asset Set", 'Activity'])
        for d in data:
            total_value = d['asset_data'].aggregate(Sum('asset_value')).get('asset_value__sum')
            for asset in d['asset_data']:
                writer.writerow([
                    asset.asset_code,
                    asset.asset_name,
                    asset.asset_value,
                    asset.on_location.location_name,
                    asset.on_status.status_name,
                    total_hour,
                    "{:.2f}".format((total_value/total_hour)),
                    asset.on_set.set_name,
                    d['activity']
                ])
        log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='generate report')
    except Exception as e:
        messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
        return redirect('report_page')
    return response

@login_required
def preview_data(request, id):
    try:
        font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'THSarabunNew.ttf')
        pdfmetrics.registerFont(TTFont('THSarabunNew', font_path))
        data, total_hour = report_data(request, id)[0], report_data(request, id)[1]
        total_value = sum(d['asset_data'].aggregate(Sum('asset_value')).get('asset_value__sum') or 0 for d in data)
        if total_hour != 0:
            cost_per_hour = "{:.2f}".format((total_value / total_hour))
        else:
            cost_per_hour = "0.00"  # Avoid division by zero, set a default value

        table_data = [['Asset Code', 'Asset Name', 'Asset Value', 'Location', 'Status', 'Total Hour', 'Cost Per Hour', 'Asset Set', 'Activity']]
        for d in data:
            total_value = d['asset_data'].aggregate(Sum('asset_value')).get('asset_value__sum')
            for asset in d['asset_data']:
                table_data.append([
                    asset.asset_code,
                    asset.asset_name,
                    asset.asset_value,
                    asset.on_location.location_name,
                    asset.on_status.status_name,
                    total_hour,
                    cost_per_hour,
                    asset.on_set.set_name,
                    d['activity']
                ])
        element = []
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'THSarabunNew'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 0), (-1, 0), 'THSarabunNew'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        element.append(table)
        
        # Try building the PDF
        doc.build(element)
        
        buffer.seek(0)
        content = buffer.getvalue()
        
        if not content:
            # If the buffer is empty, handle the error gracefully
            return HttpResponse("Error: PDF was not generated properly.", status=500)
        
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="report.pdf"'
        log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='preview report')
        return response

    except Exception as e:
        # Catch and log any errors during the process
        return HttpResponse(f"Error: {str(e)}", status=500)


#end report Function

#department activity Function

@login_required
def department_activity(request, id):
    try:
        row = Uas_department_activity.objects.filter(on_activity=id)
        department = UserBio.objects.get(userid=request.user.id).department.departmentname
        checkpermission = Uas_department_activity.objects.filter(on_activity=id, on_department__departmentname=department).exists()
        if not checkpermission:
            if department == Uas_activity.objects.get(id=id).on_location.on_department.departmentname:
                context = context_data(request)
                context['activity_id'] = id
                context['data'] = row
                context['permission'] = 0 if department != Uas_activity.objects.get(id=id).on_location.on_department.departmentname else 1
                log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='access department activity page')
                return render(request, 'department_act.html', context)
            else:
                messages.error(request, "คุณไม่มีสิทธิ์การเข้าถึง")
                return redirect('activity_page')
        context = context_data(request)
        context['activity_id'] = id
        context['data'] = row
        context['permission'] = 0 if department != Uas_activity.objects.get(id=id).on_location.on_department.departmentname else 1
        log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='access department activity page')
    except ObjectDoesNotExist:
        messages.error(request, "ข้อมูลผู้ใช้ไม่มีอยู่ หรือ ข้อมูลกิจกรรมไม่มีอยู่")
        return redirect('activity_page')
    except Exception as e:
        messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
        return redirect('activity_page')
    return render(request, 'department_act.html', context)

@login_required
def department_activity_add(request, id):
    try:
        department = UserBio.objects.get(userid=request.user.id).department.departmentname
        if department != Uas_activity.objects.get(id=id).on_location.on_department.departmentname:
            messages.error(request, "คุณไม่มีสิทธิ์การเข้าถึง")
            return redirect('department_activity', id=id)
        if request.method == 'POST':
            frm = frmDepartmentActivity(request.POST, activity_id=id)
            if frm.is_valid():
                frm.save()
                log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='add department activity')
                return redirect('activity_detail', id=id)
        frm = frmDepartmentActivity(activity_id=id)
        context = context_data(request)
        context['frm'] = frm
        log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='access add department activity page')
    except ObjectDoesNotExist:
        messages.error(request, "ข้อมูลผู้ใช้ไม่มีอยู่ หรือ ข้อมูลกิจกรรมไม่มีอยู่")
        return redirect('activity_page')
    except Exception as e:
        messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
        return redirect('activity_page')
    return render(request, 'department_act_add.html', context)

@login_required
def department_activity_edit(request, id):
    try:
        department = UserBio.objects.get(userid=request.user.id).department.departmentname
        activity_department = Uas_department_activity.objects.get(id=id).on_activity.on_location.on_department.departmentname
        activity_id = Uas_department_activity.objects.get(id=id).on_activity.id
        if department != activity_department:
            messages.error(request, "คุณไม่มีสิทธิ์การเข้าถึง")
            return redirect('department_activity', id=id)
        row = Uas_department_activity.objects.get(id=id)
        if request.method == 'POST':
            frm = frmDepartmentActivity(request.POST, instance=row, activity_id=activity_id)
            if frm.is_valid():
                frm.save()
                log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='edit department activity')
                return redirect('activity_detail', id=row.on_activity.id)
        context = context_data(request)
        context['frm'] = frmDepartmentActivity(instance=row, activity_id=activity_id)
        log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='access edit department activity page')
    except ObjectDoesNotExist:
        messages.error(request, "ข้อมูลผู้ใช้ไม่มีอยู่ หรือ ข้อมูลกิจกรรมไม่มีอยู่")
        return redirect('activity_page')
    except Exception as e:
        messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
        return redirect('activity_page')
    return render(request, 'department_act_edit.html', context)

@login_required
def department_activity_delete(request, id):
    try:
        department = UserBio.objects.get(userid=request.user.id).department.departmentname
        activity_department = Uas_department_activity.objects.get(id=id).on_activity.on_location.on_department.departmentname
        if department != activity_department:
            messages.error(request, "คุณไม่มีสิทธิ์การเข้าถึง")
            return redirect('activity_detail', id=id)
        row = Uas_department_activity.objects.get(id=id)
        row.delete()
        log.objects.create(log_user=UserBio.objects.get(userid=request.user.id), log_detail='delete department activity')
    except ObjectDoesNotExist:
        messages.error(request, "ข้อมูลผู้ใช้ไม่มีอยู่ หรือ ข้อมูลกิจกรรมไม่มีอยู่")
        return redirect('activity_page')
    return redirect('activity_detail', id=row.on_activity.id)

#end department activity Function