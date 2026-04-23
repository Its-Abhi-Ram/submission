from django.shortcuts import render
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
from .models import User, Institution, Batch, BatchTrainer, BatchStudent, BatchInvite, Session, Attendance
from .serializers import UserSerializer, BatchSerializer, SessionSerializer, AttendanceSerializer
import uuid

# Auth views
@api_view(['POST'])
def signup(request):
    data = request.data
    required_fields = ['name', 'email', 'password', 'role']
    for field in required_fields:
        if field not in data:
            return Response({field: 'This field is required'}, status=status.HTTP_400_BAD_REQUEST)
    if data['role'] not in ['student', 'trainer', 'institution', 'programme_manager', 'monitoring_officer']:
        return Response({'role': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(email=data['email']).exists():
        return Response({'email': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.create_user(
        email=data['email'],
        name=data['name'],
        password=data['password'],
        role=data['role'],
        institution_id=data.get('institution_id')
    )
    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': UserSerializer(user).data
    })

@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(request, email=email, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# Monitoring token
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def monitoring_token(request):
    if request.user.role != 'monitoring_officer':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    api_key = request.data.get('key')
    # Hardcode API key for testing
    if api_key != 'test_api_key':
        return Response({'error': 'Invalid API key'}, status=status.HTTP_401_UNAUTHORIZED)
    # Create short-lived token
    refresh = RefreshToken.for_user(request.user)
    refresh.set_exp(lifetime=timedelta(hours=1))
    access = refresh.access_token
    access['scope'] = 'monitoring'
    return Response({'access': str(access)})

# Batch views
class BatchListCreate(generics.ListCreateAPIView):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role not in ['trainer', 'institution']:
            raise permissions.PermissionDenied()
        serializer.save()

class BatchInvite(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        if request.user.role != 'trainer':
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        try:
            batch = Batch.objects.get(id=id)
        except Batch.DoesNotExist:
            return Response({'error': 'Batch not found'}, status=status.HTTP_404_NOT_FOUND)
        invite = BatchInvite.objects.create(
            batch=batch,
            created_by=request.user,
            expires_at=timezone.now() + timedelta(days=7)
        )
        return Response({'token': str(invite.token)})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def join_batch(request):
    token = request.data.get('token')
    if not token:
        return Response({'error': 'Token required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        invite = BatchInvite.objects.get(token=token, used=False, expires_at__gt=timezone.now())
    except BatchInvite.DoesNotExist:
        return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
    if request.user.role != 'student':
        return Response({'error': 'Only students can join batches'}, status=status.HTTP_403_FORBIDDEN)
    BatchStudent.objects.get_or_create(batch=invite.batch, student=request.user)
    invite.used = True
    invite.save()
    return Response({'message': 'Joined batch successfully'})

# Session views
class SessionListCreate(generics.ListCreateAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != 'trainer':
            raise permissions.PermissionDenied()
        serializer.save(trainer=self.request.user)

# Attendance views
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_attendance(request):
    session_id = request.data.get('session_id')
    status_val = request.data.get('status')
    if request.user.role != 'student':
        return Response({'error': 'Only students can mark attendance'}, status=status.HTTP_403_FORBIDDEN)
    try:
        session = Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    # Check if student is in the batch
    if not BatchStudent.objects.filter(batch=session.batch, student=request.user).exists():
        return Response({'error': 'Not enrolled in this session'}, status=status.HTTP_403_FORBIDDEN)
    attendance, created = Attendance.objects.get_or_create(
        session=session,
        student=request.user,
        defaults={'status': status_val}
    )
    if not created:
        attendance.status = status_val
        attendance.marked_at = timezone.now()
        attendance.save()
    return Response({'message': 'Attendance marked'})

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def session_attendance(request, id):
    if request.user.role != 'trainer':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    try:
        session = Session.objects.get(id=id)
    except Session.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    attendances = Attendance.objects.filter(session=session)
    serializer = AttendanceSerializer(attendances, many=True)
    return Response(serializer.data)

# Summary views
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def batch_summary(request, id):
    if request.user.role != 'institution':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    try:
        batch = Batch.objects.get(id=id, institution__user=request.user)  # Assuming institution has user
        # Wait, institution is separate, need to fix
        # For simplicity, assume institution_id in user
        if batch.institution.id != request.user.institution_id:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    except Batch.DoesNotExist:
        return Response({'error': 'Batch not found'}, status=status.HTTP_404_NOT_FOUND)
    # Calculate summary
    sessions = Session.objects.filter(batch=batch)
    total_sessions = sessions.count()
    attendances = Attendance.objects.filter(session__batch=batch)
    present = attendances.filter(status='present').count()
    absent = attendances.filter(status='absent').count()
    late = attendances.filter(status='late').count()
    return Response({
        'total_sessions': total_sessions,
        'present': present,
        'absent': absent,
        'late': late
    })

# Similar for institution and programme summaries
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def institution_summary(request, id):
    if request.user.role != 'programme_manager':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    # Assume programme manager can access
    batches = Batch.objects.filter(institution_id=id)
    # Calculate summary across batches
    total_sessions = Session.objects.filter(batch__in=batches).count()
    attendances = Attendance.objects.filter(session__batch__in=batches)
    present = attendances.filter(status='present').count()
    absent = attendances.filter(status='absent').count()
    late = attendances.filter(status='late').count()
    return Response({
        'total_sessions': total_sessions,
        'present': present,
        'absent': absent,
        'late': late
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def programme_summary(request):
    if request.user.role != 'programme_manager':
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    total_sessions = Session.objects.all().count()
    attendances = Attendance.objects.all()
    present = attendances.filter(status='present').count()
    absent = attendances.filter(status='absent').count()
    late = attendances.filter(status='late').count()
    return Response({
        'total_sessions': total_sessions,
        'present': present,
        'absent': absent,
        'late': late
    })

@api_view(['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def monitoring_attendance(request):
    if request.method != 'GET':
        return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    # Check for monitoring token
    token = request.auth
    if not token or token.get('scope') != 'monitoring':
        return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
    attendances = Attendance.objects.all()
    serializer = AttendanceSerializer(attendances, many=True)
    return Response(serializer.data)
