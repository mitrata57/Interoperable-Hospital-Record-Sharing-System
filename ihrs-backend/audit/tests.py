from django.contrib.auth import get_user_model
from django.utils import timezone
from accounts.models import Patient, Hospital
from audit.models import AuditLog
from audit.hash_chain import create_log_entry, verify_chain_integrity
from rest_framework.test import APITestCase

User = get_user_model()


class AuditLogTests(APITestCase):

    def setUp(self):
        self.hospital = Hospital.objects.create(
            name="Bir Hospital",
            license_number="LIC-001",
            city="Kathmandu",
            public_key="[]",
            private_key="[]",
        )
        self.doctor = User.objects.create_user(
            phone="9800000030", full_name="Dr Audit Test", role="doctor",
            password="DocPass123", hospital=self.hospital
        )
        self.patient = Patient.objects.create(
            nhid="NH-00002-BIR",
            full_name="Audit Test Patient",
            dob="1990-01-01",
            blood_group="O+",
            phone="9800000031",
            emergency_contact="9811111111",
        )

    def test_UT10_create_log_entry_chains_correctly(self):
        entry = create_log_entry(
            actor=self.doctor,
            action="RECORD_VIEWED",
            patient=self.patient,
            hospital=self.hospital,
        )
        self.assertIsNotNone(entry.hash)
        self.assertEqual(entry.prev_hash, "0" * 64)  # first entry -> genesis hash
        self.assertEqual(AuditLog.objects.count(), 1)

    def test_UT11_hash_chain_valid_across_multiple_entries(self):
        entry1 = create_log_entry(
            actor=self.doctor, action="RECORD_CREATED",
            patient=self.patient, hospital=self.hospital
        )
        entry2 = create_log_entry(
            actor=self.doctor, action="RECORD_VIEWED",
            patient=self.patient, hospital=self.hospital
        )

        # Second entry's prev_hash must equal first entry's hash
        self.assertEqual(entry2.prev_hash, entry1.hash)

        is_valid, broken_at = verify_chain_integrity(patient=self.patient)
        self.assertTrue(is_valid)
        self.assertIsNone(broken_at)

    def test_UT12_tampering_detected(self):
        entry1 = create_log_entry(
            actor=self.doctor, action="RECORD_CREATED",
            patient=self.patient, hospital=self.hospital
        )
        create_log_entry(
            actor=self.doctor, action="RECORD_VIEWED",
            patient=self.patient, hospital=self.hospital
        )

        # Simulate tampering: directly alter a past entry's action
        # WITHOUT recomputing its hash (this is exactly what an
        # attacker editing the DB directly would do)
        AuditLog.objects.filter(id=entry1.id).update(action="CONSENT_GRANTED")

        is_valid, broken_at = verify_chain_integrity(patient=self.patient)
        self.assertFalse(is_valid)
        self.assertEqual(broken_at, entry1.id)