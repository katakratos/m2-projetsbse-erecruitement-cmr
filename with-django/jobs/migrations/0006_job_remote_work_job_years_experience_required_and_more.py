# Generated by Django 5.2 on 2025-04-30 05:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0005_candidatedata'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='remote_work',
            field=models.BooleanField(default=False, help_text='Can this job be done remotely?'),
        ),
        migrations.AddField(
            model_name='job',
            name='years_experience_required',
            field=models.PositiveIntegerField(default=0, help_text='Number of years of experience required for this job'),
        ),
        migrations.AlterField(
            model_name='job',
            name='experience',
            field=models.CharField(choices=[('Entry', 'Entry level'), ('Intermediate', 'Intermediate'), ('Expert', 'Expert')], default='Entry', max_length=50),
        ),
        migrations.AlterField(
            model_name='job',
            name='type',
            field=models.CharField(choices=[('Full-time', 'Full time'), ('Part-time', 'Part time'), ('Internship', 'Internship'), ('Project', 'Project work'), ('Volunteering', 'Volunteering')], default='Full-time', max_length=50),
        ),
    ]
