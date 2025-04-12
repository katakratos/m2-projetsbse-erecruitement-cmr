from django.core.management.base import BaseCommand
from users.models import User, JobSeeker, Employer

class Command(BaseCommand):
    help = 'Creates test users: admin, jobseekers, and employer with password "ivan1234"'

    def handle(self, *args, **kwargs):
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='ivan1234',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created admin user: {admin_user.username}'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists'))

        # Create jobseeker users
        jobseekers_data = [
            {
                'username': 'jobseeker',
                'email': 'jobseeker@example.com',
                'first_name': 'Job',
                'last_name': 'Seeker'
            },
            {
                'username': 'jobseeker2',
                'email': 'jobseeker2@example.com',
                'first_name': 'Alice',
                'last_name': 'Doe'
            },
            {
                'username': 'jobseeker3',
                'email': 'jobseeker3@example.com',
                'first_name': 'Bob',
                'last_name': 'Smith'
            },
        ]

        for data in jobseekers_data:
            if not User.objects.filter(username=data['username']).exists():
                jobseeker = JobSeeker.objects.create_user(
                    username=data['username'],
                    email=data['email'],
                    password='ivan1234',
                    first_name=data['first_name'],
                    last_name=data['last_name']
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully created jobseeker: {jobseeker.username}'))
            else:
                self.stdout.write(self.style.WARNING(f"Jobseeker {data['username']} already exists"))

        # Create employer user
        if not User.objects.filter(username='employer').exists():
            employer = Employer.objects.create_user(
                username='employer',
                email='employer@example.com',
                password='ivan1234',
                first_name='Company',
                last_name='Owner',
                company_name='Test Company',
                company_description='A test company for demonstration purposes'
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created employer: {employer.username}'))
        else:
            self.stdout.write(self.style.WARNING('Employer already exists'))

        self.stdout.write(self.style.SUCCESS('All test users created successfully!'))
