# Generated by Django 5.1.6 on 2025-02-11 16:24

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BioStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('statusname', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Campus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('email', models.CharField(blank=True, max_length=100, null=True)),
                ('tel', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Database',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('databasename', models.CharField(max_length=100)),
                ('weight', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
            ],
        ),
        migrations.CreateModel(
            name='Degree',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='EmployeeTitle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titlename', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='EmployeeType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('typename', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ('typename',),
            },
        ),
        migrations.CreateModel(
            name='Funding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='InnovationType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('typename', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='JobTitle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titlename', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ('titlename',),
            },
        ),
        migrations.CreateModel(
            name='Prefix',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prename', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ResearchType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('typename', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Uas_Semester',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester_name', models.CharField(blank=True, max_length=255, null=True)),
                ('semester_year', models.CharField(blank=True, max_length=255, null=True)),
                ('semester_start', models.DateField(blank=True, null=True)),
                ('semester_end', models.DateField(blank=True, null=True)),
                ('semester_number', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(choices=[('1', 'แสดงผล'), ('2', 'ไม่แสดงผล')], default='1', max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='Uas_status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status_name', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Education',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qualification', models.CharField(max_length=200)),
                ('graduateYEAR', models.DateField(blank=True, null=True)),
                ('organizer', models.CharField(blank=True, max_length=200, null=True)),
                ('province', models.CharField(blank=True, max_length=100, null=True)),
                ('view', models.CharField(choices=[('1', 'สาธารณะ'), ('2', 'ในองค์กร'), ('3', 'ส่วนตัว')], default=3, max_length=2)),
                ('order', models.CharField(blank=True, max_length=10, null=True)),
                ('degree', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='uassetsapp.degree')),
                ('userid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Faculty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('facultyname', models.CharField(max_length=200)),
                ('email', models.CharField(blank=True, max_length=100, null=True)),
                ('tel', models.CharField(blank=True, max_length=100, null=True)),
                ('campus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='uassetsapp.campus')),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('departmentname', models.CharField(max_length=200)),
                ('email', models.CharField(blank=True, max_length=100, null=True)),
                ('tel', models.CharField(blank=True, max_length=100, null=True)),
                ('faculty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='uassetsapp.faculty')),
            ],
            options={
                'ordering': ('faculty__facultyname', 'departmentname'),
            },
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('positionname', models.CharField(max_length=100)),
                ('employeetitle', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='uassetsapp.employeetitle')),
            ],
            options={
                'ordering': ('positionname',),
            },
        ),
        migrations.CreateModel(
            name='Training',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('location', models.CharField(blank=True, max_length=100, null=True)),
                ('province', models.CharField(blank=True, max_length=100, null=True)),
                ('organizer', models.CharField(blank=True, max_length=100, null=True)),
                ('beginDate', models.DateField(blank=True, null=True)),
                ('endDate', models.DateField(blank=True, null=True)),
                ('certificate', models.FileField(blank=True, null=True, upload_to='cert/')),
                ('summary', models.TextField(blank=True, null=True)),
                ('result', models.CharField(blank=True, max_length=255, null=True)),
                ('apply', models.TextField(blank=True, null=True)),
                ('keyword', models.CharField(blank=True, max_length=100, null=True)),
                ('view', models.CharField(choices=[('1', 'สาธารณะ'), ('2', 'ในองค์กร'), ('3', 'ส่วนตัว')], default=3, max_length=2)),
                ('order', models.CharField(blank=True, max_length=10, null=True)),
                ('userid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Uas_activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_name', models.CharField(blank=True, max_length=255, null=True)),
                ('activity_start_date', models.DateField(blank=True, null=True)),
                ('activity_end_date', models.DateField(blank=True, null=True)),
                ('activity_start_time', models.TimeField(blank=True, null=True)),
                ('activity_end_time', models.TimeField(blank=True, null=True)),
                ('allday', models.BooleanField(default=False)),
                ('recur', models.BooleanField(default=False)),
                ('typerecur', models.CharField(choices=[('1', 'ไม่เกิดซ้ำ'), ('2', 'วันละครั้ง'), ('3', 'สัปดาห์ละครั้ง')], default='1', max_length=1)),
                ('status', models.CharField(choices=[('1', 'แสดงผล'), ('2', 'ไม่แสดงผล')], default='1', max_length=1)),
                ('on_department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='uassetsapp.department')),
            ],
        ),
        migrations.CreateModel(
            name='Uas_assets_set',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('set_name', models.CharField(blank=True, max_length=255, null=True)),
                ('set_purchase', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('1', 'แสดงผล'), ('2', 'ไม่แสดงผล')], default='1', max_length=1)),
                ('on_faculty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='uassetsapp.faculty')),
            ],
        ),
        migrations.CreateModel(
            name='Uas_department_activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('participants', models.IntegerField(blank=True, null=True)),
                ('on_activity', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='uassetsapp.uas_activity')),
                ('on_department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='uassetsapp.department')),
            ],
        ),
        migrations.CreateModel(
            name='Uas_location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location_name', models.CharField(blank=True, max_length=255, null=True)),
                ('on_department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='uassetsapp.department')),
            ],
        ),
        migrations.AddField(
            model_name='uas_activity',
            name='on_location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='uassetsapp.uas_location'),
        ),
        migrations.AddField(
            model_name='uas_activity',
            name='on_semester',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='uassetsapp.uas_semester'),
        ),
        migrations.CreateModel(
            name='Uas_assets',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset_code', models.CharField(blank=True, max_length=255, null=True)),
                ('asset_name', models.CharField(blank=True, max_length=255, null=True)),
                ('asset_money', models.CharField(blank=True, max_length=255, null=True)),
                ('asset_group', models.CharField(blank=True, max_length=255, null=True)),
                ('asset_class', models.CharField(blank=True, max_length=255, null=True)),
                ('asset_type', models.CharField(blank=True, max_length=255, null=True)),
                ('asset_amount', models.CharField(blank=True, max_length=255, null=True)),
                ('asset_number', models.CharField(blank=True, max_length=255, null=True)),
                ('asset_purchase', models.DateField(blank=True, null=True)),
                ('asset_value', models.FloatField(blank=True, null=True)),
                ('asset_expire', models.DateField(blank=True, null=True)),
                ('asset_img', models.ImageField(blank=True, null=True, upload_to='assets/')),
                ('on_set', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='uassetsapp.uas_assets_set')),
                ('on_location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='uassetsapp.uas_location')),
                ('on_status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='uassetsapp.uas_status')),
            ],
        ),
        migrations.CreateModel(
            name='UserBio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=200, null=True)),
                ('last_name', models.CharField(blank=True, max_length=200, null=True)),
                ('birthdate', models.DateField(blank=True, null=True)),
                ('citizenid', models.CharField(blank=True, max_length=20, null=True)),
                ('sex', models.CharField(choices=[('1', 'ชาย'), ('2', 'หญิง'), ('3', 'ไม่ระบุ')], default=3, max_length=2)),
                ('tel', models.CharField(blank=True, max_length=100, null=True)),
                ('employeeid', models.CharField(blank=True, max_length=20, null=True)),
                ('startdate', models.DateField(blank=True, null=True)),
                ('profile', models.ImageField(default='/media/members/avatar.png', upload_to='media/members/')),
                ('description', models.TextField(blank=True, null=True)),
                ('proexp', models.CharField(blank=True, max_length=200)),
                ('resexp', models.CharField(blank=True, max_length=200)),
                ('department', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='uassetsapp.department')),
                ('employeetype', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='uassetsapp.employeetype')),
                ('jobtitle', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='uassetsapp.jobtitle')),
                ('position', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='uassetsapp.position')),
                ('prefix', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='uassetsapp.prefix')),
                ('status', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='uassetsapp.biostatus')),
                ('userid', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'RMUTTO',
                'ordering': ('first_name', 'last_name'),
            },
        ),
        migrations.AddField(
            model_name='uas_activity',
            name='activity_responsible',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='uassetsapp.userbio'),
        ),
        migrations.CreateModel(
            name='log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log_date', models.DateTimeField(auto_now_add=True)),
                ('log_detail', models.TextField(blank=True, null=True)),
                ('log_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='uassetsapp.userbio')),
            ],
        ),
        migrations.CreateModel(
            name='Workhistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('beginDate', models.DateField(blank=True, null=True)),
                ('endDate', models.DateField(blank=True, null=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('organizer', models.CharField(blank=True, max_length=100, null=True)),
                ('view', models.CharField(choices=[('1', 'สาธารณะ'), ('2', 'ในองค์กร'), ('3', 'ส่วนตัว')], default=3, max_length=2)),
                ('order', models.CharField(blank=True, max_length=10, null=True)),
                ('userid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
