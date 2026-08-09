from django.db import models
from accounts.models import Patient, Hospital, CustomUser


class HealthRecord(models.Model):
    VISIT_TYPE_CHOICES = [
        ("emergency", "Emergency"),
        ("followup", "Follow-up"),
        ("routine", "Routine"),
    ]

    patient = models.ForeignKey(
        Patient, on_delete=models.PROTECT, related_name="health_records"
    )
    hospital = models.ForeignKey(
        Hospital, on_delete=models.PROTECT, related_name="health_records"
    )
    doctor = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True,
        related_name="created_records"
    )

    visit_type = models.CharField(max_length=20, choices=VISIT_TYPE_CHOICES)

    encrypted_data = models.BinaryField()

    aes_key_encrypted = models.BinaryField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"] 

    def __str__(self):
        return f"Record for {self.patient.nhid} — {self.visit_type} ({self.created_at.date()})"


class LabReport(models.Model):
    
    record = models.ForeignKey(
        HealthRecord, on_delete=models.PROTECT, related_name="lab_reports"
    )

    added_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True,
        related_name="lab_reports_added"
    )

    encrypted_data = models.BinaryField()
    aes_key_encrypted = models.BinaryField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Lab report on record #{self.record_id} by {self.added_by}"