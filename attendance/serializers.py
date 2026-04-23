from rest_framework import serializers
from .models import User, Institution, Batch, BatchTrainer, BatchStudent, BatchInvite, Session, Attendance

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'institution_id', 'created_at']
        read_only_fields = ['id', 'created_at']

class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = '__all__'

class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = '__all__'

class BatchTrainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchTrainer
        fields = '__all__'

class BatchStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchStudent
        fields = '__all__'

class BatchInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchInvite
        fields = '__all__'

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'