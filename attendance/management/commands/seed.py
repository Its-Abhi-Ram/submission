from django.core.management.base import BaseCommand
from attendance.models import User, Institution, Batch, BatchTrainer, BatchStudent, Session, Attendance
from django.utils import timezone
from datetime import date, time

class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **options):
        # Create institutions
        inst1 = Institution.objects.create(name='Institution 1')
        inst2 = Institution.objects.create(name='Institution 2')

        # Create users
        users = [
            {'email': 'student1@example.com', 'name': 'Student 1', 'role': 'student', 'institution_id': inst1},
            {'email': 'student2@example.com', 'name': 'Student 2', 'role': 'student', 'institution_id': inst1},
            {'email': 'trainer1@example.com', 'name': 'Trainer 1', 'role': 'trainer', 'institution_id': inst1},
            {'email': 'trainer2@example.com', 'name': 'Trainer 2', 'role': 'trainer', 'institution_id': inst1},
            {'email': 'institution@example.com', 'name': 'Institution Admin', 'role': 'institution', 'institution_id': inst1},
            {'email': 'pm@example.com', 'name': 'Programme Manager', 'role': 'programme_manager', 'institution_id': None},
            {'email': 'mo@example.com', 'name': 'Monitoring Officer', 'role': 'monitoring_officer', 'institution_id': None},
        ]

        for user_data in users:
            user = User.objects.create_user(
                email=user_data['email'],
                name=user_data['name'],
                password='password123',
                role=user_data['role'],
                institution_id=user_data['institution_id']
            )

        # Create batches
        batch1 = Batch.objects.create(name='Batch 1', institution=inst1)
        batch2 = Batch.objects.create(name='Batch 2', institution=inst1)
        batch3 = Batch.objects.create(name='Batch 3', institution=inst2)

        # Assign trainers and students
        trainer1 = User.objects.get(email='trainer1@example.com')
        trainer2 = User.objects.get(email='trainer2@example.com')
        student1 = User.objects.get(email='student1@example.com')
        student2 = User.objects.get(email='student2@example.com')

        BatchTrainer.objects.create(batch=batch1, trainer=trainer1)
        BatchStudent.objects.create(batch=batch1, student=student1)
        BatchStudent.objects.create(batch=batch1, student=student2)

        # Create sessions
        session1 = Session.objects.create(
            batch=batch1,
            trainer=trainer1,
            title='Session 1',
            date=date.today(),
            start_time=time(9, 0),
            end_time=time(10, 0)
        )
        session2 = Session.objects.create(
            batch=batch1,
            trainer=trainer1,
            title='Session 2',
            date=date.today(),
            start_time=time(10, 0),
            end_time=time(11, 0)
        )

        # Mark attendance
        Attendance.objects.create(session=session1, student=student1, status='present')
        Attendance.objects.create(session=session1, student=student2, status='absent')
        Attendance.objects.create(session=session2, student=student1, status='late')

        self.stdout.write(self.style.SUCCESS('Database seeded successfully'))