# Generated by Django 4.1.4 on 2022-12-11 19:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0005_user_email_user_first_name_user_last_name"),
    ]

    operations = [
        migrations.RemoveField(model_name="user", name="first_name",),
        migrations.RemoveField(model_name="user", name="last_name",),
    ]