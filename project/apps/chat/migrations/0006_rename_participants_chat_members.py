# Generated by Django 3.2.8 on 2021-10-25 04:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_message_sender'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chat',
            old_name='participants',
            new_name='members',
        ),
    ]
