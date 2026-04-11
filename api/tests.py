"""
Tests for unified API app
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import timedelta
from rest_framework.test import APIClient
from django.utils import timezone
from unittest.mock import patch
from api.ml_service import DiseasePredictionService, disease_prediction_service
from api.models import (
    Appointment,
    AIAnalysisRecord,
    DailyHealthLog,
    Department,
    DoctorProfile,
    MedicationSchedule,
    PatientProfile,
    Report,
    Slot,
)

User = get_user_model()


class UserModelTest(TestCase):
    """Test User model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            role='patient'
        )
    
    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.role, 'patient')
        self.assertTrue(self.user.check_password('testpass123'))
    
    def test_user_str(self):
        self.assertIn('test@example.com', str(self.user))


class PatientProfileTest(TestCase):
    """Test PatientProfile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='patient@example.com',
            username='patientuser',
            password='testpass123',
            role='patient'
        )
        self.patient = PatientProfile.objects.create(
            user=self.user,
            height=170,
            weight=70,
            blood_group='O+'
        )
    
    def test_bmi_calculation(self):
        bmi = self.patient.calculate_bmi()
        expected_bmi = round(70 / ((170 / 100) ** 2), 2)
        self.assertEqual(bmi, expected_bmi)


class DoctorProfileTest(TestCase):
    """Test DoctorProfile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='doctor@example.com',
            username='doctoruser',
            password='testpass123',
            role='doctor'
        )
        self.dept = Department.objects.create(name='Cardiology')
        self.doctor = DoctorProfile.objects.create(
            user=self.user,
            department=self.dept,
            specialization='Heart'
        )
    
    def test_doctor_creation(self):
        self.assertEqual(self.doctor.user.email, 'doctor@example.com')
        self.assertEqual(self.doctor.department.name, 'Cardiology')


class DiseasePredictionAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_ai_assistant_page_endpoint(self):
        response = self.client.get('/ai/assistant/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'MedoAir AI Assistant')

    def test_ai_tracking_page_endpoints(self):
        dashboard_response = self.client.get('/ai/dashboard/')
        medicines_response = self.client.get('/ai/medicines/')
        weekly_response = self.client.get('/ai/weekly-report/')
        timeline_response = self.client.get('/ai/patient-timeline/')

        self.assertEqual(dashboard_response.status_code, 200)
        self.assertContains(dashboard_response, "Today's Health Dashboard")
        self.assertEqual(medicines_response.status_code, 200)
        self.assertContains(medicines_response, 'AI Medicine Tracking')
        self.assertEqual(weekly_response.status_code, 200)
        self.assertContains(weekly_response, 'AI Weekly Health Report')
        self.assertEqual(timeline_response.status_code, 200)
        self.assertContains(timeline_response, 'AI Patient Timeline')

    def test_ai_assistant_message_endpoint(self):
        payload = {
            "message": "Mujhe bukhar, body pain aur thakan ho rahi hai.",
            "symptoms_text": "fever, body pain, fatigue",
            "notes": "2 din se problem hai",
            "food_type": "home",
            "water_intake_glasses": 6,
            "sleep_hours": 5.5,
            "sleep_quality": "poor",
            "stress_level": "moderate",
            "energy_level": "low",
            "top_k": 3,
        }

        response = self.client.post('/api/ai/assistant/message/', payload, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertIn('assistant_response', response.data['data'])
        self.assertIn('detected_problem', response.data['data'])
        self.assertIn('risk_probability', response.data['data'])
        self.assertIn('analysis_record', response.data['data'])
        self.assertIn('analysis_steps', response.data['data'])
        self.assertTrue(len(response.data['data']['matched_symptoms']) >= 2)
        self.assertTrue(len(response.data['data']['recommended_tests']) >= 1)
        self.assertTrue(len(response.data['data']['care_guidance']) >= 1)
        self.assertTrue(len(response.data['data']['warning_signs']) >= 1)
        self.assertTrue(len(response.data['data']['submitted_context']) >= 1)
        self.assertEqual(response.data['data']['prediction']['model'], 'LogisticRegression')
        self.assertEqual(len(response.data['data']['analysis_steps']), 4)
        self.assertIn('model_performance', response.data['data'])
        self.assertIn('prediction_quality', response.data['data'])
        self.assertEqual(AIAnalysisRecord.objects.count(), 1)
        record = AIAnalysisRecord.objects.first()
        self.assertEqual(record.detected_problem, response.data['data']['detected_problem'])
        self.assertEqual(float(record.risk_probability), float(response.data['data']['risk_probability']))

    def test_ai_assistant_response_language_matches_input(self):
        hinglish_response = self.client.post(
            '/api/ai/assistant/message/',
            {"message": "mere ko bukhar hora hai"},
            format='json'
        )
        english_response = self.client.post(
            '/api/ai/assistant/message/',
            {"message": "i have fever today"},
            format='json'
        )

        self.assertEqual(hinglish_response.status_code, 200)
        self.assertEqual(english_response.status_code, 200)
        self.assertEqual(hinglish_response.data['data']['response_language'], 'hinglish')
        self.assertEqual(english_response.data['data']['response_language'], 'english')
        self.assertIn('Aapke message', hinglish_response.data['data']['assistant_response'])
        self.assertIn('Based on the symptoms', english_response.data['data']['assistant_response'])

    def test_ai_assistant_ignores_negated_symptoms(self):
        response = self.client.post(
            '/api/ai/assistant/message/',
            {"message": "mujhe bukhar nahi hai, bas khansi aur thakan hai"},
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('fever', [item.lower() for item in response.data['data']['recognized_negated_symptoms']])
        self.assertNotIn('fever', [item.lower() for item in response.data['data']['matched_symptoms']])
        self.assertIn('cough', [item.lower() for item in response.data['data']['matched_symptoms']])

    def test_ai_assistant_handles_hinglish_typos(self):
        response = self.client.post(
            '/api/ai/assistant/message/',
            {"message": "mujhe bukhr aur khasi hai"},
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        matched_symptoms = [item.lower() for item in response.data['data']['matched_symptoms']]
        self.assertIn('fever', matched_symptoms)
        self.assertIn('cough', matched_symptoms)

    @patch('api.views.document_reader_service.extract_text')
    def test_ai_assistant_accepts_attachment_and_reads_report_text(self, mock_extract_text):
        mock_extract_text.return_value = "fever headache cough fatigue"
        attachment = SimpleUploadedFile(
            "prescription.pdf",
            b"%PDF-1.4 test report",
            content_type="application/pdf",
        )

        response = self.client.post(
            '/api/ai/assistant/message/',
            {
                "message": "",
                "attachment": attachment,
                "top_k": 3,
            },
            format='multipart'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment_context', response.data['data'])
        self.assertEqual(response.data['data']['attachment_context']['filename'], 'prescription.pdf')
        self.assertTrue(response.data['data']['attachment_context']['has_text'])
        self.assertTrue(len(response.data['data']['matched_symptoms']) >= 1)

    def test_disease_prediction_meta_endpoint(self):
        response = self.client.get('/api/ai/disease-prediction/meta/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['model'], 'LogisticRegression')
        self.assertTrue(len(response.data['data']['supported_diseases']) >= 5)
        self.assertIn('dataset_inventory', response.data['data'])
        self.assertIn('knowledge_index', response.data['data'])
        self.assertIn('evaluation', response.data['data'])
        self.assertIn('cross_validation', response.data['data']['evaluation'])
        self.assertIsNotNone(response.data['data']['evaluation']['cross_validation']['accuracy_percent'])

        inventory_by_file = {
            item['file_name']: item
            for item in response.data['data']['dataset_inventory']
        }
        self.assertEqual(inventory_by_file['dengue_dataset_clear.csv']['row_count'], 3198)
        self.assertEqual(inventory_by_file['diarahhe_dataset_clear.csv']['row_count'], 2973)
        self.assertEqual(inventory_by_file['maleria_dataset_clear.csv']['row_count'], 3181)
        self.assertEqual(inventory_by_file['tuber_dataset_clear.csv']['row_count'], 2671)
        self.assertEqual(inventory_by_file['typhoidfewer_dataset_clear.csv']['row_count'], 1847)
        self.assertEqual(inventory_by_file['typhoid_dataset_clear.csv']['status'], 'empty')
        self.assertGreater(response.data['data']['knowledge_index']['total_indexed_chunks'], 0)

    def test_disease_prediction_endpoint(self):
        payload = {
            "symptoms": ["fever", "cough", "sore throat", "fatigue"],
            "top_k": 3
        }

        response = self.client.post('/api/ai/disease-prediction/', payload, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertIn('predicted_disease', response.data['data'])
        self.assertEqual(response.data['data']['model'], 'LogisticRegression')
        self.assertEqual(len(response.data['data']['top_predictions']), 3)
        self.assertIn('model_performance', response.data['data'])
        self.assertIn('prediction_quality', response.data['data'])
        self.assertIsNotNone(response.data['data']['model_performance']['cross_validation_accuracy_percent'])

    def test_disease_prediction_marks_uncertain_for_weak_signal(self):
        prediction = disease_prediction_service.predict(["qwertysymptom"], top_k=3)

        self.assertEqual(prediction['prediction_status'], 'uncertain')
        self.assertTrue(prediction['is_uncertain'])
        self.assertEqual(prediction['predicted_disease'], 'uncertain')
        self.assertEqual(prediction['predicted_display_name'], 'Uncertain')
        self.assertIn('closest_known_match', prediction)
        self.assertIn('confidence_margin_percent', prediction)

    def test_dataset_cleaning_removes_known_noise_entries(self):
        service = DiseasePredictionService()
        service._ensure_model()

        influenza_symptoms = set(service._symptom_bank['influenza'])
        typhoid_symptoms = set(service._symptom_bank['typhoid'])
        diarrhoea_symptoms = set(service._symptom_bank['diarrhoea'])

        self.assertNotIn('reduced egg production', influenza_symptoms)
        self.assertNotIn('what are symptoms of typhoid?', typhoid_symptoms)
        self.assertNotIn('does my child have dehydration', diarrhoea_symptoms)
        self.assertIn('runny nose', influenza_symptoms)
        self.assertIn('constipation', typhoid_symptoms)
        self.assertIn('dehydration', diarrhoea_symptoms)

    def test_curated_symptom_patterns_can_return_confirmed_match(self):
        service = DiseasePredictionService()

        influenza_prediction = service.predict(['fever', 'cough', 'sore throat', 'runny nose', 'fatigue'])
        dengue_prediction = service.predict(['high fever', 'body pain', 'joint pain', 'rash', 'nausea'])
        diarrhea_prediction = service.predict(['diarrhea', 'vomiting', 'abdominal pain', 'dehydration'])
        malaria_prediction = service.predict(['fever', 'chills', 'vomiting', 'sweats', 'fatigue'])
        typhoid_prediction = service.predict(['fever', 'abdominal pain', 'headache', 'constipation', 'fatigue'])
        tb_prediction = service.predict(['cough', 'weight loss', 'night sweats', 'fatigue'])

        self.assertEqual(influenza_prediction['predicted_display_name'], 'Influenza')
        self.assertEqual(influenza_prediction['prediction_status'], 'matched')
        self.assertEqual(dengue_prediction['predicted_display_name'], 'Dengue')
        self.assertEqual(dengue_prediction['prediction_status'], 'matched')
        self.assertEqual(diarrhea_prediction['predicted_display_name'], 'Diarrhoea')
        self.assertEqual(diarrhea_prediction['prediction_status'], 'matched')
        self.assertEqual(malaria_prediction['predicted_display_name'], 'Malaria')
        self.assertEqual(malaria_prediction['prediction_status'], 'matched')
        self.assertEqual(typhoid_prediction['predicted_display_name'], 'Typhoid')
        self.assertEqual(typhoid_prediction['prediction_status'], 'matched')
        self.assertEqual(tb_prediction['predicted_display_name'], 'Tuberculosis')
        self.assertEqual(tb_prediction['prediction_status'], 'matched')
        self.assertTrue(any(item['disease'] == 'dengue' for item in dengue_prediction['triggered_rule_signals']))
        self.assertTrue(any(item['disease'] == 'diarrhoea' for item in diarrhea_prediction['triggered_rule_signals']))
        self.assertTrue(any(item['disease'] == 'typhoid' for item in typhoid_prediction['triggered_rule_signals']))

    def test_hinglish_typhoid_style_message_returns_confirmed_match(self):
        response = self.client.post(
            '/api/ai/assistant/message/',
            {"message": "Mujhe 2 din se bukhar, sir dard, pet dard, kabz aur thakan hai"},
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['detected_problem'], 'Typhoid')
        self.assertEqual(response.data['data']['prediction']['prediction_status'], 'matched')
        self.assertIn('constipation', response.data['data']['prediction']['canonical_input_symptoms'])
        self.assertTrue(
            any(item['disease'] == 'typhoid' for item in response.data['data']['prediction']['triggered_rule_signals'])
        )

    def test_ai_assistant_response_does_not_include_raw_dataset_json(self):
        response = self.client.post(
            '/api/ai/assistant/message/',
            {"message": "Mujhe bukhar, khansi, gala kharab, naak beh rahi hai aur thakan hai"},
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(any(item.strip().startswith('{') for item in response.data['data']['care_guidance']))
        self.assertFalse(any(item.strip().startswith('{') for item in response.data['data']['medicine_guidance']))
        self.assertNotIn('{"disease_name"', response.data['data']['assistant_response'])

    def test_ai_assistant_answers_exact_tb_treatment_question_from_dataset(self):
        response = self.client.post(
            '/api/ai/assistant/message/',
            {"message": "How is TB treated?"},
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['interaction_mode'], 'knowledge')
        self.assertEqual(response.data['data']['detected_problem'], 'Tuberculosis')
        self.assertEqual(response.data['data']['prediction']['prediction_status'], 'knowledge_answer')
        self.assertIn('treatment', response.data['data']['knowledge_match']['topic'])
        self.assertNotIn('I could not identify clear symptoms', response.data['data']['assistant_response'])

    def test_ai_assistant_answers_non_symptom_dataset_question_for_diarrhoea(self):
        response = self.client.post(
            '/api/ai/assistant/message/',
            {"message": "How to treat diarrhoea at home"},
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['interaction_mode'], 'knowledge')
        self.assertEqual(response.data['data']['detected_problem'], 'Diarrhoea')
        self.assertEqual(response.data['data']['prediction']['prediction_status'], 'knowledge_answer')
        self.assertNotIn('I could not identify clear symptoms', response.data['data']['assistant_response'])

    def test_ai_assistant_answers_incubation_question_from_indexed_dataset_rows(self):
        response = self.client.post(
            '/api/ai/assistant/message/',
            {"message": "What is the incubation period of influenza?"},
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['interaction_mode'], 'knowledge')
        self.assertEqual(response.data['data']['detected_problem'], 'Influenza')
        self.assertEqual(response.data['data']['prediction']['prediction_status'], 'knowledge_answer')
        self.assertTrue(
            any('1-4' in chunk or '1 4' in chunk for chunk in response.data['data']['knowledge_match']['matched_chunks'])
        )



class AITrackingModuleTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.patient = User.objects.create_user(
            email='tracker@example.com',
            username='tracker',
            password='testpass123',
            role='patient'
        )
        self.client.force_authenticate(user=self.patient)

    def test_daily_checkin_generates_warning_for_repeated_symptom(self):
        today = timezone.localdate()
        for offset in range(2, -1, -1):
            DailyHealthLog.objects.create(
                user=self.patient,
                log_date=today - timedelta(days=offset),
                symptoms=['fever', 'headache'],
                food_type='junk' if offset == 0 else 'home',
                water_intake_glasses=4,
                sleep_hours=5.5,
                sleep_quality='poor',
                stress_level='high',
                energy_level='low',
            )

        response = self.client.get('/api/ai/daily-checkin/')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(any('Fever for 3 days' in item for item in response.data['data']['warnings']))
        self.assertTrue(any('Low water intake' in item for item in response.data['data']['quick_insights']))

    def test_daily_dashboard_uses_selected_date_and_tracks_seven_days(self):
        today = timezone.localdate()
        for offset in range(6, -1, -1):
            DailyHealthLog.objects.create(
                user=self.patient,
                log_date=today - timedelta(days=offset),
                symptoms=['fever'] if offset < 3 else ['headache'],
                food_type='home',
                water_intake_glasses=7,
                sleep_hours=7,
                sleep_quality='good',
                stress_level='low',
                energy_level='medium',
            )

        response = self.client.get(f'/api/ai/daily-checkin/?log_date={today.isoformat()}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['date'], today.isoformat())
        self.assertEqual(response.data['data']['seven_day_tracker']['days_logged'], 7)
        self.assertTrue(response.data['data']['seven_day_tracker']['is_week_ready'])
        self.assertEqual(len(response.data['data']['seven_day_tracker']['days']), 7)
        self.assertIn('dataset_assessment', response.data['data']['weekly_report_preview'])
        self.assertIn('ai_health_report', response.data['data']['weekly_report_preview'])

    def test_medicine_tracking_and_weekly_report(self):
        medicine_payload = {
            "name": "Paracetamol",
            "dose": "1 tablet",
            "duration_days": 5,
            "timings": ["morning", "night"],
            "source": "manual",
        }
        medicine_response = self.client.post('/api/ai/medicines/', medicine_payload, format='json')

        self.assertEqual(medicine_response.status_code, 201)
        medication_id = medicine_response.data['data']['id']

        dose_payload = {
            "timing": "morning",
            "status": "taken",
        }
        dose_response = self.client.post(
            f'/api/ai/medicines/{medication_id}/dose/',
            dose_payload,
            format='json'
        )

        self.assertEqual(dose_response.status_code, 200)

        DailyHealthLog.objects.create(
            user=self.patient,
            log_date=timezone.localdate(),
            symptoms=['fatigue'],
            food_type='outside',
            water_intake_glasses=7,
            sleep_hours=7,
            sleep_quality='average',
            stress_level='moderate',
            energy_level='medium',
        )

        report_response = self.client.get('/api/ai/weekly-report/')

        self.assertEqual(report_response.status_code, 200)
        self.assertIn('medicine_compliance', report_response.data['data'])
        self.assertTrue(len(report_response.data['data']['recommended_actions']) >= 1)

    @patch('api.views.document_reader_service.extract_text')
    def test_prescription_extract_and_save_flow(self, mock_extract_text):
        mock_extract_text.return_value = "Paracetamol 500 mg for 5 days 1-0-1 after food"
        attachment = SimpleUploadedFile(
            "prescription.pdf",
            b"%PDF-1.4 prescription",
            content_type="application/pdf",
        )

        extract_response = self.client.post(
            '/api/ai/medicines/prescription-extract/',
            {"attachment": attachment},
            format='multipart'
        )

        self.assertEqual(extract_response.status_code, 200)
        self.assertTrue(len(extract_response.data['data']['medicines']) >= 1)

        save_response = self.client.post(
            '/api/ai/medicines/prescription-save/',
            {
                "start_date": timezone.localdate().isoformat(),
                "medicines": extract_response.data['data']['medicines'],
            },
            format='json'
        )

        self.assertEqual(save_response.status_code, 201)
        self.assertTrue(MedicationSchedule.objects.filter(user=self.patient, source='prescription_upload').exists())

    def test_weekly_report_generates_dataset_assessment_after_seven_logs(self):
        today = timezone.localdate()
        symptom_sets = [
            ['fever', 'headache'],
            ['fever', 'body pain'],
            ['fever', 'fatigue'],
            ['headache', 'fatigue'],
            ['fever', 'headache'],
            ['fever'],
            ['headache'],
        ]
        for offset, symptoms in enumerate(reversed(symptom_sets)):
            DailyHealthLog.objects.create(
                user=self.patient,
                log_date=today - timedelta(days=offset),
                symptoms=symptoms,
                food_type='outside' if offset % 2 else 'home',
                water_intake_glasses=6,
                sleep_hours=6.5,
                sleep_quality='average',
                stress_level='moderate',
                energy_level='medium',
            )

        response = self.client.get(f'/api/ai/weekly-report/?end_date={today.isoformat()}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['days_logged'], 7)
        self.assertTrue(response.data['data']['is_week_ready'])
        self.assertIn(response.data['data']['dataset_assessment']['status'], ['ready', 'building'])
        self.assertIsNotNone(response.data['data']['dataset_assessment']['possible_issue'])
        self.assertIsNotNone(response.data['data']['dataset_assessment']['risk_probability'])
        self.assertIn('ai_health_report', response.data['data'])
        self.assertIn('what_is_good', response.data['data']['ai_health_report'])
        self.assertIn('what_needs_attention', response.data['data']['ai_health_report'])
        self.assertIn('what_may_happen_next', response.data['data']['ai_health_report'])

    def test_weekly_report_pdf_download_endpoint(self):
        today = timezone.localdate()
        for offset in range(6, -1, -1):
            DailyHealthLog.objects.create(
                user=self.patient,
                log_date=today - timedelta(days=offset),
                symptoms=['fever', 'headache'] if offset < 4 else ['fatigue'],
                food_type='outside' if offset % 2 else 'home',
                water_intake_glasses=6,
                sleep_hours=6.5,
                sleep_quality='average',
                stress_level='moderate',
                energy_level='medium',
            )

        response = self.client.get(f'/api/ai/weekly-report/pdf/?end_date={today.isoformat()}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn(f'medoair-weekly-report-{today.isoformat()}.pdf', response["Content-Disposition"])
        self.assertTrue(response.content.startswith(b"%PDF-1.4"))
        self.assertIn(b"MedoAir 7-Day AI Health Report", response.content)

    @patch('api.health_tracking_service.document_reader_service.extract_text')
    def test_weekly_report_parses_report_metrics_and_trends(self, mock_extract_text):
        mock_extract_text.side_effect = [
            "Hemoglobin 10.2 g/dl Vitamin D 18 ng/ml Sugar 95 mg/dl",
            "Hemoglobin 11.1 g/dl Vitamin D 24 ng/ml Sugar 110 mg/dl",
        ]
        Report.objects.create(
            user=self.patient,
            title='Blood Test 1',
            file=SimpleUploadedFile("report1.pdf", b"%PDF-1.4 report1", content_type="application/pdf"),
        )
        Report.objects.create(
            user=self.patient,
            title='Blood Test 2',
            file=SimpleUploadedFile("report2.pdf", b"%PDF-1.4 report2", content_type="application/pdf"),
        )

        response = self.client.get('/api/ai/weekly-report/')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data['data']['report_summary']) >= 2)
        self.assertTrue(len(response.data['data']['report_summary'][0]['metrics']) >= 1)
        self.assertTrue(len(response.data['data']['report_metric_trends']) >= 1)

    def test_doctor_timeline_access(self):
        doctor = User.objects.create_user(
            email='doctor.timeline@example.com',
            username='doctor_timeline',
            password='testpass123',
            role='doctor'
        )
        dept = Department.objects.create(name='General Medicine')
        DoctorProfile.objects.create(user=doctor, department=dept, specialization='General')

        slot = Slot.objects.create(
            doctor=doctor,
            date=timezone.localdate(),
            start_time='10:00',
            end_time='10:30'
        )
        Appointment.objects.create(
            patient=self.patient,
            doctor=doctor,
            slot=slot,
            appointment_type='online',
            status='scheduled'
        )

        DailyHealthLog.objects.create(
            user=self.patient,
            log_date=timezone.localdate(),
            symptoms=['cough'],
            food_type='home',
            water_intake_glasses=8,
            sleep_hours=7,
            sleep_quality='good',
            stress_level='low',
            energy_level='high',
        )
        MedicationSchedule.objects.create(
            user=self.patient,
            name='Vitamin D',
            dose='1 capsule',
            duration_days=10,
            timings=['morning'],
            source='manual',
        )

        doctor_client = APIClient()
        doctor_client.force_authenticate(user=doctor)
        response = doctor_client.get(f'/api/ai/patient-timeline/{self.patient.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['patient_email'], self.patient.email)
        self.assertTrue(len(response.data['data']['daily_symptom_history']) >= 1)


class ReportUploadAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='reportuser@example.com',
            username='reportuser',
            password='testpass123',
            role='patient'
        )
        self.client.force_authenticate(user=self.user)

    def test_report_upload_accepts_png_file(self):
        attachment = SimpleUploadedFile(
            "report-image.png",
            b"\x89PNG\r\n\x1a\nfakepngcontent",
            content_type="image/png",
        )

        response = self.client.post(
            '/api/reports/',
            {
                "title": "PNG Report",
                "file": attachment,
            },
            format='multipart'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['data']['title'], 'PNG Report')
        self.assertTrue(response.data['data']['file'].endswith('.png'))
        self.assertTrue(Report.objects.filter(user=self.user, title='PNG Report').exists())
