# Generated by Django 3.1.7 on 2021-04-25 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0024_auto_20210425_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='month',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='year',
            field=models.IntegerField(default=4),
            preserve_default=False,
        ),
    ]
