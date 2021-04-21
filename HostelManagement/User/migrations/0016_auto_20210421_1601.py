# Generated by Django 3.1.7 on 2021-04-21 10:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0015_attandace'),
    ]

    operations = [
        migrations.CreateModel(
            name='attendace',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attendace_id', models.IntegerField()),
                ('date', models.DateField()),
                ('status', models.BooleanField(default=False)),
                ('sd_name', models.CharField(max_length=50)),
                ('stduent_info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='User.student')),
            ],
        ),
        migrations.DeleteModel(
            name='attandace',
        ),
    ]
