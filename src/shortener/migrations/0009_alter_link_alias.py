# Generated by Django 4.2.1 on 2023-05-17 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shortener', '0008_alter_link_alias'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='alias',
            field=models.CharField(blank=True, max_length=80, null=True, unique=True),
        ),
    ]