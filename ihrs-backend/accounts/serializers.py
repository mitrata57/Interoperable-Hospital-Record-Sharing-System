from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Hospital, Patient

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):

   # for data validation user uses to register
    
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "id", "phone", "email", "full_name",
            "role", "hospital", "password",
        ]

    def validate_role(self, value):
        allowed_roles = ["patient", "doctor", "nurse", "hospital_admin", "receptionist"]
        if value not in allowed_roles:
            raise serializers.ValidationError(
                f"Invalid role. Allowed: {allowed_roles}"
            )
        return value

    def validate(self, data):
        # doctor/nurse/hospital_admin/receptionist - hospital field compulsory hunuparcha
        role = data.get("role")
        hospital = data.get("hospital")

        if role in ["doctor", "nurse", "hospital_admin", "receptionist"] and not hospital:
            raise serializers.ValidationError(
                {"hospital": "Hospital is compulsary for this role."}
            )
        return data

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()  # phone or email
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    nhid = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ["id", "phone", "email", "full_name", "role", "hospital", "nhid"]
    def get_nhid(self, obj):
        if obj.role == "patient" and obj.patient_profile:
            return obj.patient_profile.nhid
        return None