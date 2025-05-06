from django.urls import path, include
from uassetsapp import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('admin/', admin.site.urls, name='admin'),
    path('logout/', views.logout_request, name='logout'),
    #Asset path
    path('asset_page/', views.asset_page, name='asset_page'),
    path('asset_add/', views.asset_add, name='asset_add'),
    path('asset_edit/<int:id>/', views.asset_edit, name='asset_edit'),
    path('asset_delete/<int:id>/', views.asset_delete, name='asset_delete'),
    #end Asset path
    #List Asset path
    path('list_asset/<int:id>', views.list_asset, name='list_asset'),
    path('list_asset/add/<int:id>', views.list_asset_add, name='list_asset_add'),
    path('list_asset/edit/<int:id>', views.list_asset_edit, name='list_asset_edit'),
    path('list_asset/delete/<int:id>', views.list_asset_delete, name='list_asset_delete'),
    #end List Asset path
    #Activity path
    path('activity_page/', views.activity_page, name='activity_page'),
    path('activity_add/<str:date>', views.activity_add, name='activity_add'),
    path('activity_edit/<int:id>/', views.activity_edit, name='activity_edit'),
    path('activity_delete/<int:id>/', views.activity_delete, name='activity_delete'),
    path('activity_list', views.activity_list, name='activity_list'),
    path('activity_detail/<int:id>', views.activity_detail, name='activity_detail'),
    #end Activity path
    #Location path
    path('location_page/', views.location_page, name='location_page'),
    path('location_add/', views.location_add, name='location_add'),
    path('location_edit/<int:id>/', views.location_edit, name='location_edit'),
    path('location_delete/<int:id>/', views.location_delete, name='location_delete'),
    #end Location path
    #Semester path
    path('semester_page/', views.semester_page, name='semester_page'),
    path('semester_add/', views.semester_add, name='semester_add'),
    path('semester_edit/<int:id>/', views.semester_edit, name='semester_edit'),
    path('semester_delete/<int:id>/', views.semester_delete, name='semester_delete'),
    #end Semester path
    #Status list Asset path
    path('status_page/', views.status_page, name='status_page'),
    path('status_add/', views.status_add, name='status_add'),
    path('status_edit/<int:id>/', views.status_edit, name='status_edit'),
    path('status_delete/<int:id>/', views.status_delete, name='status_delete'),
    #end Status list Asset path
    #Report path
    path('report_page/', views.report_page, name='report_page'),
    path('report_csv/<int:id>', views.generate_report, name='report_csv'),
    path('preview_data/<int:id>', views.preview_data, name='preview_data'),
    #end Report path
    #department activity path
    path('department_activity/<int:id>', views.department_activity, name='department_activity'),
    path('department_activity_add/<int:id>', views.department_activity_add, name='department_activity_add'),
    path('department_activity_edit/<int:id>/', views.department_activity_edit, name='department_activity_edit'),
    path('department_activity_delete/<int:id>/', views.department_activity_delete, name='department_activity_delete'),
    #end department activity path
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)