# Generated by Django 3.2.9 on 2022-02-09 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indberetning', '0004_alter_indberetninglinje_salgsvægt'),
    ]

    operations = [
        migrations.AddField(
            model_name='virksomhed',
            name='navn',
            field=models.TextField(null=True, verbose_name='Navn'),
        ),
    ]
