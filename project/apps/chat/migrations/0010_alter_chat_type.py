# Generated by Django 3.2.8 on 2021-10-26 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0009_auto_20211025_2042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='type',
            field=models.PositiveIntegerField(choices=[(1, 'Common'), (2, 'Direct')], default=1, editable=False),
        ),
    ]
