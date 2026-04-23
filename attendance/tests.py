import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from attendance.models import User, Institution, Batch, Session, Attendance

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def institution():
    return Institution.objects.create(name='Test Institution')

@pytest.fixture
def user_student(institution):
    return User.objects.create_user(
        email='student@test.com',
        name='Test Student',
        password='password123',
        role='student',
        institution_id=institution
    )

@pytest.fixture
def user_trainer(institution):
    return User.objects.create_user(
        email='trainer@test.com',
        name='Test Trainer',
        password='password123',
        role='trainer',
        institution_id=institution
    )

@pytest.mark.django_db
def test_signup_and_login(api_client, institution):
    # Signup
    data = {
        'name': 'New Student',
        'email': 'newstudent@test.com',
        'password': 'password123',
        'role': 'student',
        'institution_id': institution.id
    }
    response = api_client.post('/api/auth/signup/', data)
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data

    # Login
    login_data = {'email': 'newstudent@test.com', 'password': 'password123'}
    response = api_client.post('/api/auth/login/', login_data)
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data

@pytest.mark.django_db
def test_create_session(api_client, user_trainer, institution):
    # Login
    api_client.force_authenticate(user=user_trainer)
    batch = Batch.objects.create(name='Test Batch', institution=institution)
    data = {
        'batch': batch.id,
        'title': 'Test Session',
        'date': '2024-01-01',
        'start_time': '09:00:00',
        'end_time': '10:00:00'
    }
    response = api_client.post('/api/sessions/', data)
    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_mark_attendance(api_client, user_student, user_trainer, institution):
    # Create batch and session
    batch = Batch.objects.create(name='Test Batch', institution=institution)
    from attendance.models import BatchStudent
    BatchStudent.objects.create(batch=batch, student=user_student)
    session = Session.objects.create(
        batch=batch,
        trainer=user_trainer,
        title='Test Session',
        date='2024-01-01',
        start_time='09:00:00',
        end_time='10:00:00'
    )
    # Login as student
    api_client.force_authenticate(user=user_student)
    data = {'session_id': session.id, 'status': 'present'}
    response = api_client.post('/api/attendance/mark/', data)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_monitoring_method_not_allowed(api_client, user_student):
    api_client.force_authenticate(user=user_student)
    response = api_client.post('/api/monitoring/attendance/')
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

@pytest.mark.django_db
def test_unauthorized_access(api_client):
    response = api_client.get('/api/batches/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
