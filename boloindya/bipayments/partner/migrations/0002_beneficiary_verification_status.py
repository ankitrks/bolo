# Generated by Django 3.1.1 on 2020-10-02 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='beneficiary',
            name='verification_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('verified', 'Verified'), ('failed', 'Failed')], default='pending', max_length=30, verbose_name='Bank IFSC'),
        ),
    ]
