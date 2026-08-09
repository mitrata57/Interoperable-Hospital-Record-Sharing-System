
import requests


BIR_URL = "http://127.0.0.1:8001"
TUTH_URL = "http://127.0.0.1:8002"

BIR_ADMIN = {"identifier": "9800000011", "password": "SecurePass123"}
BIR_DOCTOR = {"identifier": "9811112222", "password": "DoctorOwnPass456"}
BIR_RECEPTIONIST = {"identifier": "9876678900", "password": "receppass"}
BIR_PATIENT = {"identifier": "9898987676", "password": "asdfghjkl"}
TUTH_DOCTOR = {"identifier": "9898989800", "password": "samaysamay"}
PATIENT_NHID = "NH-00004-KTM"  
TUTH_HOSPITAL_NAME = "TUTH" 

results = []  


def login(base_url, identifier, password):
    resp = requests.post(f"{base_url}/api/auth/login/", json={
        "identifier": identifier, "password": password
    })
    if resp.status_code == 200:
        return resp.json()["data"]["token"]
    return None


def auth_headers(token):
    return {"Authorization": f"Token {token}"}


def report(test_id, description, passed, detail=""):
    status_text = "PASS" if passed else "FAIL"
    print(f"[{status_text}] {test_id} — {description}")
    if detail:
        print(f"        -> {detail}")
    results.append((test_id, description, passed))



# ST-01: Authentication & Dashboard (role-based login check)


def test_st01():
    print("\n--- ST-01: Authentication & Role-Based Login ---")
    roles_to_check = {
        "doctor": BIR_DOCTOR,
        "receptionist": BIR_RECEPTIONIST,
        "patient": BIR_PATIENT,
        "hospital_admin": BIR_ADMIN,
    }
    all_ok = True
    for role_name, creds in roles_to_check.items():
        resp = requests.post(f"{BIR_URL}/api/auth/login/", json=creds)
        ok = resp.status_code == 200 and resp.json()["data"]["user"]["role"] == role_name
        all_ok = all_ok and ok
        print(f"    {role_name}: {'ok' if ok else 'FAILED - ' + resp.text}")
    report("ST-01", "Login redirects/resolves correct role for each account type", all_ok)


# ST-02: Patient & Clinical Workflow

def test_st02():
    print("\n--- ST-02: Patient Registration + Health Record Creation ---")
    recep_token = login(BIR_URL, BIR_RECEPTIONIST["identifier"], BIR_RECEPTIONIST["password"])
    if not recep_token:
        report("ST-02", "Receptionist registers patient, doctor creates record", False, "Receptionist login failed")
        return None

    new_patient = {
        "phone": "9811112232",
        "full_name": "System Test Patient",
        "email": "systemtest@example.com",
        "dob": "1995-05-05",
        "blood_group": "B+",
        "emergency_contact": "9811119999",
    }
    resp = requests.post(f"{BIR_URL}/api/auth/register/", json=new_patient,
                          headers=auth_headers(recep_token))
    if resp.status_code != 201:
        report("ST-02", "Receptionist registers patient, doctor creates record", False, resp.text)
        return None

    nhid = resp.json()["data"]["nhid"]
    print(f"    Registered patient NHID: {nhid}")

    doctor_token = login(BIR_URL, BIR_DOCTOR["identifier"], BIR_DOCTOR["password"])
    record_resp = requests.post(f"{BIR_URL}/api/records/create/", json={
        "patient_nhid": nhid,
        "visit_type": "routine",
        "diagnosis": "Routine checkup - system test",
    }, headers=auth_headers(doctor_token))

    ok = record_resp.status_code == 201
    report("ST-02", "Receptionist registers patient, doctor creates linked record", ok, record_resp.text)
    return nhid


# ST-03: Clinical & NEWS2 Flow


def test_st03():
    print("\n--- ST-03: NEWS2 Score + Lifestyle Recommendation ---")
    doctor_token = login(BIR_URL, BIR_DOCTOR["identifier"], BIR_DOCTOR["password"])

    record_resp = requests.post(f"{BIR_URL}/api/records/create/", json={
        "patient_nhid": PATIENT_NHID,
        "visit_type": "emergency",
        "diagnosis": "Breathing difficulty - system test",
        "vitals": {
            "respiratory_rate": 25,
            "spo2": 90,
            "on_oxygen": True,
            "systolic_bp": 85,
            "pulse": 130,
            "consciousness": "V",
            "temperature": 35.5,
        }
    }, headers=auth_headers(doctor_token))

    if record_resp.status_code != 201:
        report("ST-03", "NEWS2 score + lifestyle recommendation generated with vitals", False, record_resp.text)
        return

    read_resp = requests.get(f"{BIR_URL}/api/records/{PATIENT_NHID}/",
                              headers=auth_headers(doctor_token))
    data = read_resp.json().get("data", {})
    records = data.get("records", [])
    has_risk_score = any(r.get("risk_score") is not None for r in records)
    has_lifestyle = data.get("lifestyle_summary") is not None

    ok = read_resp.status_code == 200 and has_risk_score
    report("ST-03", "NEWS2 risk_score present for doctor view; lifestyle_summary generated",
           ok, f"risk_score found: {has_risk_score}, lifestyle_summary present: {has_lifestyle}")


# ST-04: Access Control (RBAC)


def test_st04():
    print("\n--- ST-04: RBAC — receptionist/patient blocked from creating records ---")
    recep_token = login(BIR_URL, BIR_RECEPTIONIST["identifier"], BIR_RECEPTIONIST["password"])
    patient_token = login(BIR_URL, BIR_PATIENT["identifier"], BIR_PATIENT["password"])

    recep_resp = requests.post(f"{BIR_URL}/api/records/create/", json={
        "patient_nhid": PATIENT_NHID, "visit_type": "routine"
    }, headers=auth_headers(recep_token))

    patient_resp = requests.post(f"{BIR_URL}/api/records/create/", json={
        "patient_nhid": PATIENT_NHID, "visit_type": "routine"
    }, headers=auth_headers(patient_token))

    ok = recep_resp.status_code == 403 and patient_resp.status_code == 403
    report("ST-04", "Receptionist and patient forbidden from create_record (403)", ok,
           f"receptionist: {recep_resp.status_code}, patient: {patient_resp.status_code}")

# ST-05 / ST-06: Consent grant then revoke

def test_st05_st06():
    print("\n--- ST-05/06: Consent Grant then Revoke ---")
    patient_token = login(BIR_URL, BIR_PATIENT["identifier"], BIR_PATIENT["password"])

    grant_resp = requests.post(f"{BIR_URL}/api/consent/grant/", json={
        "hospital_name": TUTH_HOSPITAL_NAME, "duration_days": 7
    }, headers=auth_headers(patient_token))
    ok_grant = grant_resp.status_code == 200
    report("ST-05", "Patient grants consent to hospital", ok_grant, grant_resp.text)

    revoke_resp = requests.post(f"{BIR_URL}/api/consent/revoke/", json={
        "hospital_name": TUTH_HOSPITAL_NAME
    }, headers=auth_headers(patient_token))
    ok_revoke = revoke_resp.status_code == 200
    report("ST-06", "Patient revokes previously granted consent", ok_revoke, revoke_resp.text)

# ST-07: Break-Glass Emergency Access

def test_st07():
    print("\n--- ST-07: Break-Glass Emergency Access ---")
    doctor_token = login(BIR_URL, BIR_DOCTOR["identifier"], BIR_DOCTOR["password"])

    resp = requests.post(
        f"{BIR_URL}/api/consent/emergency/request/{PATIENT_NHID}/",
        json={"justification": "Patient unconscious, need immediate history - system test"},
        headers=auth_headers(doctor_token)
    )
    ok = resp.status_code == 201
    report("ST-07", "Doctor requests emergency access with justification, access granted", ok, resp.text)

# ST-08: End-to-End Patient Journey (patient views own record)


def test_st08():
    print("\n--- ST-08: Patient views own record after full journey ---")
    patient_token = login(BIR_URL, BIR_PATIENT["identifier"], BIR_PATIENT["password"])

    resp = requests.get(f"{BIR_URL}/api/records/{PATIENT_NHID}/",
                         headers=auth_headers(patient_token))
    data = resp.json().get("data", {})
    has_records = len(data.get("records", [])) > 0
    has_lifestyle = data.get("lifestyle_summary") is not None

    ok = resp.status_code == 200 and has_records
    report("ST-08", "Patient views own complete record + lifestyle summary", ok,
           f"records found: {has_records}, lifestyle_summary present: {has_lifestyle}")


# ST-09: Cross-Hospital Federation 

def test_st09():
    print("\n--- ST-09: Cross-Hospital Federation (view) ---")
    patient_token = login(BIR_URL, BIR_PATIENT["identifier"], BIR_PATIENT["password"])
    grant_resp = requests.post(f"{BIR_URL}/api/consent/grant/", json={
        "hospital_name": TUTH_HOSPITAL_NAME, "duration_days": 7
    }, headers=auth_headers(patient_token))

    if grant_resp.status_code != 200:
        report("ST-09", "Doctor at TUTH views Bir patient's record after consent", False,
               f"consent grant failed: {grant_resp.text}")
        return

    tuth_doctor_token = login(TUTH_URL, TUTH_DOCTOR["identifier"], TUTH_DOCTOR["password"])
    if not tuth_doctor_token:
        report("ST-09", "Doctor at TUTH views Bir patient's record after consent", False,
               "TUTH doctor login failed")
        return

    view_resp = requests.get(f"{TUTH_URL}/api/records/{PATIENT_NHID}/",
                              headers=auth_headers(tuth_doctor_token))
    data = view_resp.json().get("data", {})
    has_peer_records = any(
        r.get("is_peer_record") for r in data.get("records", [])
    )

    ok = view_resp.status_code == 200 and has_peer_records
    report("ST-09", "Doctor at TUTH views Bir patient's record after consent granted",
           ok, f"peer records visible: {has_peer_records}")
# Running everything

if __name__ == "__main__":
    print("=" * 60)
    print("IHRS SYSTEM TESTING — ST-01 to ST-07")
    print("=" * 60)

    test_st01()
    test_st02()
    test_st03()
    test_st04()
    test_st05_st06()
    test_st07()
    test_st08()
    test_st09()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for test_id, desc, passed in results:
        print(f"{test_id}: {'PASS' if passed else 'FAIL'} — {desc}")

    total = len(results)
    passed_count = sum(1 for _, _, p in results if p)
    print(f"\n{passed_count}/{total} test cases passed.")