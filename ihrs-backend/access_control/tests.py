from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from accounts.models import Patient
from access_control.models import AccessConsent


class ConsentManagementTests(APITestCase):

    def setUp(self):
        self.patient_profile = Patient.objects.create(
            nhid="NH-00001-BIR",
            full_name="Test Patient",
            dob="1990-01-01",
            blood_group="O+",
            phone="9800000020",
            emergency_contact="9811111111",
        )

    def test_UT07_patient_grants_consent(self):
        consent = AccessConsent.objects.create(
            patient=self.patient_profile,
            hospital_name="TUTH",
            granted=True,
            expires_at=timezone.now() + timedelta(days=7),
        )
        self.assertTrue(consent.is_valid())
        self.assertEqual(
            AccessConsent.objects.filter(
                patient=self.patient_profile, hospital_name="TUTH"
            ).count(),
            1
        )

    def test_UT08_patient_revokes_consent(self):
        consent = AccessConsent.objects.create(
            patient=self.patient_profile,
            hospital_name="TUTH",
            granted=True,
            expires_at=timezone.now() + timedelta(days=7),
        )
        consent.granted = False
        consent.save()
        consent.refresh_from_db()
        self.assertFalse(consent.is_valid())

    def test_UT09_access_denied_after_expiry(self):
        consent = AccessConsent.objects.create(
            patient=self.patient_profile,
            hospital_name="TUTH",
            granted=True,
            expires_at=timezone.now() - timedelta(days=1),
        )
        self.assertFalse(consent.is_valid())