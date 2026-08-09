from rest_framework import serializers


class VitalsSerializer(serializers.Serializer):
    
    respiratory_rate = serializers.IntegerField(required=False, allow_null=True)
    spo2 = serializers.IntegerField(required=False, allow_null=True, min_value=0, max_value=100)
    on_oxygen = serializers.BooleanField(required=False, default=False)
    systolic_bp = serializers.IntegerField(required=False, allow_null=True)
    pulse = serializers.IntegerField(required=False, allow_null=True)
    consciousness = serializers.ChoiceField(
        choices=["A", "C", "V", "P", "U"],  # ACVPU scale
        required=False, default="A"
    )
    temperature = serializers.FloatField(required=False, allow_null=True)


class CreateRecordSerializer(serializers.Serializer):
   
    patient_nhid = serializers.CharField(max_length=20)
    visit_type = serializers.ChoiceField(
        choices=["emergency", "followup", "routine"]
    )
    diagnosis = serializers.CharField(allow_blank=True, required=False, default="")
    prescription = serializers.CharField(allow_blank=True, required=False, default="")
    notes = serializers.CharField(allow_blank=True, required=False, default="")
    confidential_notes = serializers.CharField(allow_blank=True, required=False, default="")
    vitals = VitalsSerializer(required=False, default=dict)

    def validate(self, data):
       
        data["record_data"] = {
            "diagnosis": data.get("diagnosis", ""),
            "prescription": data.get("prescription", ""),
            "notes": data.get("notes", ""),
            "confidential_notes": data.get("confidential_notes", ""),
            "vitals": data.get("vitals", {}),
        }
        return data


class AddLabReportSerializer(serializers.Serializer):
   
    LAB_TEST_CHOICES = [
        ("glucose_fasting", "Fasting Blood Glucose"),
        ("hba1c", "HbA1c"),
        ("creatinine", "Serum Creatinine"),
        ("hemoglobin", "Hemoglobin"),
        ("systolic_bp", "Systolic Blood Pressure (lab-recorded)"),
        ("ldl_cholesterol", "LDL Cholesterol"),
        ("bmi", "Body Mass Index"),
    ]

    UNIT_MAP = {
        "glucose_fasting": "mg/dL",
        "hba1c": "%",
        "creatinine": "mg/dL",
        "hemoglobin": "g/dL",
        "systolic_bp": "mmHg",
        "ldl_cholesterol": "mg/dL",
        "bmi": "kg/m2",
    }

    test_type = serializers.ChoiceField(choices=LAB_TEST_CHOICES)
    value = serializers.FloatField()
    remarks = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, data):
        data["unit"] = self.UNIT_MAP[data["test_type"]]
        return data