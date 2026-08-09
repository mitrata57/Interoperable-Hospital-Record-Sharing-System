import json
from unittest.mock import patch
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import Hospital, Patient
from records.models import HealthRecord

User = get_user_model()


class HealthRecordTests(APITestCase):

    def setUp(self):
        self.hospital = Hospital.objects.create(
            name="Bir Hospital",
            license_number="LIC-001",
            city="Kathmandu",
            public_key=json.dumps([65537, 3233]),
            private_key=json.dumps([2753, 3233]),
        )

        self.doctor = User.objects.create_user(
            phone="9800000010", full_name="Dr Test", role="doctor",
            password="DocPass123", hospital=self.hospital
        )

        self.patient_profile = Patient.objects.create(
            nhid="NH-00001-BIR",
            full_name="Patient Test",
            dob="1990-01-01",
            blood_group="O+",
            phone="9800000011",
            emergency_contact="9811111111",
        )

        self.patient_user = User.objects.create_user(
            phone="9800000011", full_name="Patient Test", role="patient",
            password="PatientPass123", patient_profile=self.patient_profile
        )

        self.create_url = "/api/records/create/"
        self.read_url = f"/api/records/{self.patient_profile.nhid}/"

    def _login(self, identifier, password):
        response = self.client.post("/api/auth/login/", {
            "identifier": identifier, "password": password
        })
        token = response.data["data"]["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

    @patch("records.views.get_or_cache_patient")
    @patch("records.views.rsa_encrypt", return_value=b"encrypted_key")
    @patch("records.views.aes_encrypt", return_value=b"encrypted_data")
    def test_UT04_doctor_creates_health_record(self, mock_aes, mock_rsa, mock_get_patient):
        mock_get_patient.return_value = self.patient_profile
        self._login("9800000010", "DocPass123")

        response = self.client.post(self.create_url, {
            "patient_nhid": self.patient_profile.nhid,
            "visit_type": "routine",
            "diagnosis": "Hypertension",
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            HealthRecord.objects.filter(patient=self.patient_profile).count(), 1
        )

    @patch("records.views.create_log_entry")
    @patch("records.views.build_lifestyle_summary", return_value=None)
    @patch("records.views.merge_peer_records", return_value=([], []))
    @patch("records.views.broadcast_lookup", return_value=[])
    @patch("records.views.decrypt_patient_records")
    def test_UT05_doctor_views_existing_record(
        self, mock_decrypt, mock_broadcast, mock_merge, mock_lifestyle, mock_log
    ):
        mock_decrypt.return_value = (
            [{
                "record_id": 1,
                "hospital": self.hospital.name,
                "hospital_id": self.hospital.id,
                "doctor": self.doctor.full_name,
                "visit_type": "routine",
                "created_at": "2026-01-01T00:00:00",
                "data": {"diagnosis": "Hypertension"},
                "lab_reports": [],
                "risk_score": None,
            }],
            None
        )
        self._login("9800000010", "DocPass123")

        response = self.client.get(self.read_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        records = response.data["data"]["records"]
        self.assertTrue(any(r["data"].get("diagnosis") == "Hypertension" for r in records))

    @patch("records.views.create_log_entry")
    @patch("records.views.build_lifestyle_summary", return_value=None)
    @patch("records.views.merge_peer_records", return_value=([], []))
    @patch("records.views.broadcast_lookup", return_value=[])
    @patch("records.views.decrypt_patient_records")
    def test_UT06_patient_views_own_record(
        self, mock_decrypt, mock_broadcast, mock_merge, mock_lifestyle, mock_log
    ):
        mock_decrypt.return_value = (
            [{
                "record_id": 1,
                "hospital": self.hospital.name,
                "hospital_id": self.hospital.id,
                "doctor": self.doctor.full_name,
                "visit_type": "routine",
                "created_at": "2026-01-01T00:00:00",
                "data": {"diagnosis": "Hypertension"},
                "lab_reports": [],
            }],
            None
        )
        self._login("9800000011", "PatientPass123")

        response = self.client.get(self.read_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["patient"]["nhid"], self.patient_profile.nhid)