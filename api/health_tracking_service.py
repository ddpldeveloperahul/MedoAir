from __future__ import annotations

from collections import Counter, defaultdict
from datetime import timedelta
from statistics import mean
from typing import Iterable

from django.db.models import QuerySet
from django.utils import timezone

from .ml_service import disease_prediction_service
from .models import DailyHealthLog, MedicationDoseLog, MedicationSchedule, Report
from .document_reader import document_reader_service
from .clinical_document_ai import clinical_document_ai_service


class HealthTrackingAIService:
    SEVERE_SYMPTOMS = {
        "chest pain",
        "shortness of breath",
        "difficulty breathing",
        "blood in stool",
        "fainting",
        "severe vomiting",
        "severe dehydration",
    }

    def build_daily_dashboard(self, user, target_date=None) -> dict[str, object]:
        target_date = target_date or timezone.localdate()
        daily_log = DailyHealthLog.objects.filter(user=user, log_date=target_date).first()
        seven_day_logs = list(
            DailyHealthLog.objects.filter(
                user=user,
                log_date__range=(target_date - timedelta(days=6), target_date),
            ).order_by("log_date")
        )
        medications = list(
            MedicationSchedule.objects.filter(
                user=user,
                is_active=True,
                start_date__lte=target_date,
                end_date__gte=target_date,
            ).order_by("name")
        )

        medicine_cards = [self._build_medication_card(medication, target_date) for medication in medications]
        pending_doses = sum(card["pending_count"] for card in medicine_cards)
        missed_yesterday = self._find_missed_doses(user, target_date - timedelta(days=1))

        quick_insights: list[str] = []
        warnings: list[str] = []
        prediction = None

        if daily_log is None:
            quick_insights.append("Complete today's check-in to unlock AI insights and weekly tracking.")
        else:
            symptoms = self._clean_symptoms(daily_log.symptoms)
            if symptoms:
                prediction = disease_prediction_service.predict(symptoms, top_k=3)
                warnings.extend(self._build_symptom_warnings(user, target_date, symptoms))
            else:
                quick_insights.append("No symptoms today — good job.")

            if daily_log.food_type == "junk":
                quick_insights.append("Junk food detected — avoid oily food tomorrow if possible.")
            elif daily_log.food_type == "outside":
                quick_insights.append("Outside food noted today — stay hydrated and monitor digestion.")

            if daily_log.water_intake_glasses and daily_log.water_intake_glasses < 6:
                quick_insights.append("Low water intake today — try to increase hydration.")

            if daily_log.sleep_hours is not None and float(daily_log.sleep_hours) < 6:
                quick_insights.append("Sleep was below 6 hours — recovery may be slower.")

            if daily_log.sleep_quality == "poor":
                quick_insights.append("Poor sleep quality detected — keep an eye on fatigue and stress.")

            if daily_log.energy_level == "low":
                quick_insights.append("Energy level is low today — take extra rest if symptoms continue.")

        if pending_doses:
            quick_insights.append(f"You have {pending_doses} medicine dose(s) pending today.")
            due_reminder = self._build_due_now_reminder(medicine_cards, target_date)
            if due_reminder:
                quick_insights.append(due_reminder)

        for missed in missed_yesterday:
            warnings.append(
                f"You missed yesterday's {missed['timing']} dose of {missed['name']}."
            )

        tracker = self._build_seven_day_tracker(seven_day_logs, target_date)
        weekly_preview = self.build_weekly_report(user, target_date)

        return {
            "date": str(target_date),
            "daily_log": self._serialize_daily_log(daily_log),
            "today_medicines": medicine_cards,
            "quick_insights": self._dedupe(quick_insights),
            "warnings": self._dedupe(warnings),
            "prediction": prediction,
            "health_score": self._calculate_health_score(daily_log, medicine_cards),
            "seven_day_tracker": tracker,
            "weekly_report_preview": weekly_preview,
        }

    def build_weekly_report(self, user, end_date=None) -> dict[str, object]:
        end_date = end_date or timezone.localdate()
        start_date = end_date - timedelta(days=6)
        logs = list(
            DailyHealthLog.objects.filter(user=user, log_date__range=(start_date, end_date)).order_by("log_date")
        )
        medicines = list(MedicationSchedule.objects.filter(user=user).order_by("name"))
        reports = list(Report.objects.filter(user=user)[:5])
        parsed_reports = self._build_report_summaries(reports)

        symptom_counter: Counter[str] = Counter()
        junk_days = 0
        outside_food_days = 0
        sleep_values: list[float] = []
        symptom_days = 0
        daily_scores: list[dict[str, object]] = []

        for log in logs:
            symptoms = self._clean_symptoms(log.symptoms)
            if symptoms:
                symptom_days += 1
                symptom_counter.update(symptoms)
            if log.food_type == "junk":
                junk_days += 1
            if log.food_type == "outside":
                outside_food_days += 1
            if log.sleep_hours is not None:
                sleep_values.append(float(log.sleep_hours))

            daily_scores.append(
                {
                    "date": str(log.log_date),
                    "health_score": self._calculate_health_score(log, []),
                }
            )

        issues_detected = self._weekly_issue_summary(user, end_date)
        medicine_compliance = [self._medicine_compliance_summary(medication, end_date) for medication in medicines]
        trend_weeks = self._build_trend_windows(user, end_date)
        dataset_assessment = self._build_weekly_dataset_assessment(logs)
        logging_summary = self._build_seven_day_tracker(logs, end_date)
        report_metric_trends = clinical_document_ai_service.build_report_trends(parsed_reports)
        recommended_actions = self._build_recommended_actions(
            issues_detected,
            junk_days,
            medicine_compliance,
            parsed_reports,
        )

        return {
            "period": {
                "start_date": str(start_date),
                "end_date": str(end_date),
            },
            "days_logged": len(logs),
            "is_week_ready": len(logs) >= 7,
            "missing_days": max(0, 7 - len(logs)),
            "logging_summary": logging_summary,
            "issues_detected": issues_detected,
            "lifestyle_summary": {
                "junk_food_count": junk_days,
                "outside_food_count": outside_food_days,
                "sleep_avg_hours": round(mean(sleep_values), 1) if sleep_values else None,
                "symptom_days": symptom_days,
            },
            "dataset_assessment": dataset_assessment,
            "ai_health_report": self._build_ai_health_report(
                logs=logs,
                dataset_assessment=dataset_assessment,
                issues_detected=issues_detected,
                medicine_compliance=medicine_compliance,
                parsed_reports=parsed_reports,
                sleep_avg_hours=round(mean(sleep_values), 1) if sleep_values else None,
                junk_days=junk_days,
                outside_food_days=outside_food_days,
                symptom_days=symptom_days,
                daily_scores=daily_scores,
            ),
            "report_summary": parsed_reports,
            "report_metric_trends": report_metric_trends,
            "medicine_compliance": medicine_compliance,
            "weekly_trends": trend_weeks,
            "daily_health_scores": daily_scores,
            "recommended_actions": recommended_actions,
        }

    def build_doctor_timeline(self, patient_user) -> dict[str, object]:
        recent_logs = DailyHealthLog.objects.filter(user=patient_user).order_by("-log_date")[:14]
        medications = MedicationSchedule.objects.filter(user=patient_user).order_by("-created_at")[:10]
        reports = Report.objects.filter(user=patient_user)[:10]

        return {
            "patient_id": patient_user.id,
            "patient_email": patient_user.email,
            "daily_symptom_history": [self._serialize_daily_log(log) for log in recent_logs],
            "food_habits": [
                {
                    "date": str(log.log_date),
                    "food_type": log.food_type,
                    "water_intake_glasses": log.water_intake_glasses,
                    "sleep_hours": float(log.sleep_hours) if log.sleep_hours is not None else None,
                    "stress_level": log.stress_level,
                    "energy_level": log.energy_level,
                }
                for log in recent_logs
            ],
            "medicines": [
                {
                    "id": medication.id,
                    "name": medication.name,
                    "dose": medication.dose,
                    "timings": medication.timings,
                    "status": self._medication_status_label(medication),
                    "compliance": self._medicine_compliance_summary(medication, timezone.localdate()),
                }
                for medication in medications
            ],
            "reports": [
                {
                    "id": report.id,
                    "title": report.title or "Report",
                    "uploaded_at": report.uploaded_at.isoformat(),
                }
                for report in reports
            ],
        }

    def _build_medication_card(self, medication: MedicationSchedule, target_date) -> dict[str, object]:
        due_timings = [timing for timing in medication.timings if timing in dict(MedicationSchedule.TIMING_CHOICES)]
        dose_logs = {
            log.timing: log
            for log in MedicationDoseLog.objects.filter(medication=medication, dose_date=target_date)
        }
        doses = []
        pending_count = 0

        for timing in due_timings:
            log = dose_logs.get(timing)
            status = log.status if log else "pending"
            if status == "pending":
                pending_count += 1
            doses.append(
                {
                    "timing": timing,
                    "status": status,
                }
            )

        return {
            "id": medication.id,
            "name": medication.name,
            "dose": medication.dose,
            "timings": due_timings,
            "doses": doses,
            "pending_count": pending_count,
            "status": self._medication_status_label(medication, target_date),
        }

    def _build_symptom_warnings(self, user, target_date, symptoms: Iterable[str]) -> list[str]:
        warnings = []
        repeated = self._repeating_symptoms(user, target_date)
        for symptom in symptoms:
            lowered = symptom.lower()
            repeated_days = repeated.get(lowered, 0)
            if repeated_days >= 3:
                warnings.append(
                    f"{symptom.title()} for {repeated_days} days -> Doctor consultation recommended."
                )

            if lowered in self.SEVERE_SYMPTOMS:
                warnings.append(
                    f"{symptom.title()} looks severe -> Seek immediate medical attention."
                )

        return warnings

    def _weekly_issue_summary(self, user, end_date) -> list[str]:
        repeated = self._repeating_symptoms(user, end_date, lookback_days=7)
        issues = [
            f"{symptom.title()} for {days} day(s)"
            for symptom, days in sorted(repeated.items(), key=lambda item: (-item[1], item[0]))
            if days >= 3
        ]
        return issues or ["No major symptom pattern detected this week."]

    def _build_recommended_actions(
        self,
        issues_detected: list[str],
        junk_days: int,
        medicine_compliance: list[dict[str, object]],
        parsed_reports: list[dict[str, object]] | None = None,
    ) -> list[str]:
        actions: list[str] = []
        if any("No major symptom pattern" not in item for item in issues_detected):
            actions.append("Consider doctor consultation if repeated symptoms continue.")
        if junk_days >= 3:
            actions.append("Avoid oily or junk food for the next few days.")
        if any((item.get("compliance_percent") or 0) < 80 for item in medicine_compliance):
            actions.append("Improve medicine adherence and avoid missing scheduled doses.")
        abnormal_metrics = [
            metric
            for report in (parsed_reports or [])
            for metric in report.get("metrics", [])
            if metric.get("status") not in {"Normal", "Unknown"}
        ]
        for metric in abnormal_metrics[:3]:
            actions.append(
                f"Review {metric.get('parameter')} result ({metric.get('value')} {metric.get('unit')}) because it is marked {metric.get('status')}."
            )
        if not actions:
            actions.append("Continue your current routine and keep logging daily health data.")
        return actions

    def _build_ai_health_report(
        self,
        logs: list[DailyHealthLog],
        dataset_assessment: dict[str, object],
        issues_detected: list[str],
        medicine_compliance: list[dict[str, object]],
        parsed_reports: list[dict[str, object]],
        sleep_avg_hours: float | None,
        junk_days: int,
        outside_food_days: int,
        symptom_days: int,
        daily_scores: list[dict[str, object]],
    ) -> dict[str, object]:
        positive_signals: list[str] = []
        concern_signals: list[str] = []
        important_observations: list[str] = []
        future_risks: list[str] = []

        if logs:
            fully_logged = len(logs) >= 7
            if fully_logged:
                positive_signals.append("You completed a full 7-day health log, so the report is based on complete weekly data.")
            else:
                concern_signals.append(f"Only {len(logs)}/7 days are logged, so the report may be less accurate than a full weekly record.")

        if symptom_days <= 2 and logs:
            positive_signals.append("Symptoms were present on fewer days this week, which is a good sign.")
        elif symptom_days >= 4:
            concern_signals.append(f"Symptoms were logged on {symptom_days} days this week, showing a repeated health concern.")

        if sleep_avg_hours is not None and sleep_avg_hours >= 7:
            positive_signals.append(f"Average sleep was {sleep_avg_hours} hours, which supports recovery.")
        elif sleep_avg_hours is not None and sleep_avg_hours < 6:
            concern_signals.append(f"Average sleep was only {sleep_avg_hours} hours, which may slow recovery and increase fatigue.")

        if junk_days <= 1 and logs:
            positive_signals.append("Junk food intake stayed low this week.")
        elif junk_days >= 3:
            concern_signals.append(f"Junk food was logged {junk_days} times this week, which can worsen digestion and recovery.")

        if outside_food_days >= 4:
            concern_signals.append(f"Outside food was logged {outside_food_days} times, so hygiene and digestion need more attention.")

        low_compliance = [item for item in medicine_compliance if (item.get("compliance_percent") or 0) < 80]
        if low_compliance:
            concern_signals.append("Medicine compliance dropped below 80% for some medicines.")
            future_risks.append("If medicine doses continue to be missed, symptom control may become weaker.")
        elif medicine_compliance:
            positive_signals.append("Medicine adherence looks stable for the current schedule.")

        abnormal_metrics = [
            metric
            for report in parsed_reports
            for metric in report.get("metrics", [])
            if metric.get("status") not in {"Normal", "Unknown"}
        ]
        for metric in abnormal_metrics[:3]:
            important_observations.append(
                f"{metric.get('parameter')} is {metric.get('status')} at {metric.get('value')} {metric.get('unit')}".strip()
            )

        likely_issue = dataset_assessment.get("possible_issue")
        risk_probability = dataset_assessment.get("risk_probability")
        top_matches = dataset_assessment.get("top_predictions") or []
        closest_dataset_match = dataset_assessment.get("closest_dataset_match") or {}
        alternative_matches = [item.get("display_name") for item in top_matches[1:3] if item.get("display_name")]

        if likely_issue == "Uncertain":
            current_status = (
                "Your recent 7-day symptom pattern does not yet point to one clear issue."
            )
            if closest_dataset_match.get("display_name"):
                current_status += (
                    f" The nearest dataset match is {closest_dataset_match['display_name']} "
                    f"at {risk_probability}% confidence."
                )
            if alternative_matches:
                current_status += f" Other close matches are {', '.join(alternative_matches)}."
        elif likely_issue:
            current_status = (
                f"Your recent 7-day pattern mainly matches {likely_issue} "
                f"with {risk_probability}% risk probability based on the symptom dataset."
            )
            if alternative_matches:
                current_status += f" Other close matches are {', '.join(alternative_matches)}."
        else:
            current_status = "There is not enough symptom evidence yet to identify a strong weekly issue."

        if issues_detected and all("No major symptom pattern" not in item for item in issues_detected):
            important_observations.extend(issues_detected[:3])

        health_score_trend = self._build_health_score_trend_summary(daily_scores)
        if health_score_trend:
            important_observations.append(health_score_trend)

        if likely_issue and risk_probability is not None and float(risk_probability) >= 65:
            future_risks.append(
                f"If the same symptom pattern continues, {likely_issue} may become more clinically significant and should be reviewed by a doctor."
            )
        if symptom_days >= 4:
            future_risks.append("Repeated symptoms over multiple days can increase the chance of worsening discomfort or delayed recovery.")
        if sleep_avg_hours is not None and sleep_avg_hours < 6:
            future_risks.append("Low sleep can increase weakness, stress, and slower recovery over the next few days.")
        if junk_days >= 3:
            future_risks.append("Frequent junk food can worsen stomach issues, acidity, or inflammation-related symptoms.")
        if not future_risks:
            future_risks.append("Current trends look manageable if you continue the same routine and keep tracking daily.")

        attention_level = self._determine_attention_level(
            dataset_assessment=dataset_assessment,
            issues_detected=issues_detected,
            abnormal_metrics=abnormal_metrics,
        )

        weekly_summary = self._build_weekly_summary_text(
            current_status=current_status,
            attention_level=attention_level,
            positive_signals=positive_signals,
            concern_signals=concern_signals,
        )

        return {
            "summary": weekly_summary,
            "current_status": current_status,
            "what_is_good": positive_signals or ["No strong positive pattern has been identified yet."],
            "what_needs_attention": concern_signals or ["No major weekly concern was detected from the current logs."],
            "important_observations": important_observations or ["Keep logging daily data for stronger report quality."],
            "what_may_happen_next": future_risks,
            "attention_level": attention_level,
        }

    def _determine_attention_level(
        self,
        dataset_assessment: dict[str, object],
        issues_detected: list[str],
        abnormal_metrics: list[dict[str, object]],
    ) -> str:
        risk_probability = float(dataset_assessment.get("risk_probability") or 0)
        repeated_issue = any("No major symptom pattern" not in item for item in issues_detected)
        critical_metric = any(metric.get("status") in {"Low", "High", "Deficient"} for metric in abnormal_metrics)

        if risk_probability >= 70 or (repeated_issue and critical_metric):
            return "High"
        if risk_probability >= 45 or repeated_issue or critical_metric:
            return "Moderate"
        return "Low"

    def _build_health_score_trend_summary(self, daily_scores: list[dict[str, object]]) -> str | None:
        if len(daily_scores) < 2:
            return None

        first_score = daily_scores[0].get("health_score")
        last_score = daily_scores[-1].get("health_score")
        if first_score is None or last_score is None:
            return None

        if last_score > first_score:
            return f"Health score improved from {first_score} to {last_score} during the selected week."
        if last_score < first_score:
            return f"Health score dropped from {first_score} to {last_score} during the selected week."
        return f"Health score stayed stable at around {last_score} during the selected week."

    def _build_weekly_summary_text(
        self,
        current_status: str,
        attention_level: str,
        positive_signals: list[str],
        concern_signals: list[str],
    ) -> str:
        summary = f"{current_status} Overall attention level is {attention_level.lower()}."
        if positive_signals:
            summary += f" Positive signs: {positive_signals[0]}"
        if concern_signals:
            summary += f" Main concern: {concern_signals[0]}"
        return summary

    def _build_weekly_dataset_assessment(self, logs: list[DailyHealthLog]) -> dict[str, object]:
        if not logs:
            return {
                "status": "insufficient_data",
                "message": "Start logging your daily symptoms to generate a 7-day AI health report.",
                "possible_issue": None,
                "risk_probability": None,
                "matched_symptoms": [],
                "care_guidance": [],
                "warning_signs": [],
                "medicine_guidance": [],
            }

        symptom_counter: Counter[str] = Counter()
        for log in logs:
            symptom_counter.update(item.lower() for item in self._clean_symptoms(log.symptoms))

        weighted_symptoms: list[str] = []
        for symptom, count in symptom_counter.most_common(8):
            weighted_symptoms.extend([symptom] * min(count, 3))

        if not weighted_symptoms:
            return {
                "status": "no_symptoms_logged",
                "message": "No symptom pattern detected in your recent logs.",
                "possible_issue": None,
                "risk_probability": None,
                "matched_symptoms": [],
                "care_guidance": [],
                "warning_signs": [],
                "medicine_guidance": [],
            }

        prediction = disease_prediction_service.predict(weighted_symptoms, top_k=3)
        top_prediction = prediction["top_predictions"][0]
        closest_known_match = prediction.get("closest_known_match") or top_prediction
        disease_details = disease_prediction_service._dataset_details.get(closest_known_match["disease"], {})
        readiness_message = (
            "7 days of data completed. This weekly report is based on your stored daily routine and symptom pattern."
            if len(logs) >= 7
            else f"{len(logs)}/7 days logged. Add more daily check-ins for a stronger weekly assessment."
        )

        return {
            "status": "ready" if len(logs) >= 7 else "building",
            "message": readiness_message,
            "possible_issue": prediction["predicted_display_name"],
            "risk_probability": top_prediction["confidence"],
            "matched_symptoms": [symptom for symptom, _ in symptom_counter.most_common(5)],
            "care_guidance": disease_details.get("care_guidance", []),
            "warning_signs": disease_details.get("warning_signs", []),
            "medicine_guidance": disease_details.get("medicine_guidance", []),
            "closest_dataset_match": closest_known_match,
            "prediction_status": prediction.get("prediction_status"),
            "top_predictions": prediction["top_predictions"],
        }

    def _build_seven_day_tracker(self, logs: list[DailyHealthLog], end_date) -> dict[str, object]:
        start_date = end_date - timedelta(days=6)
        log_map = {log.log_date: log for log in logs}
        days = []

        for offset in range(7):
            day = start_date + timedelta(days=offset)
            log = log_map.get(day)
            days.append(
                {
                    "date": str(day),
                    "logged": bool(log),
                    "symptoms": self._clean_symptoms(log.symptoms) if log else [],
                    "health_score": self._calculate_health_score(log, []) if log else None,
                }
            )

        return {
            "start_date": str(start_date),
            "end_date": str(end_date),
            "days_logged": len(logs),
            "days_remaining": max(0, 7 - len(logs)),
            "is_week_ready": len(logs) >= 7,
            "days": days,
        }

    def _build_report_summaries(self, reports: list[Report]) -> list[dict[str, object]]:
        summaries = []
        for report in reports:
            try:
                extracted_text = document_reader_service.extract_text(report.file)
            except Exception:
                extracted_text = ""
            metrics = clinical_document_ai_service.extract_lab_metrics(extracted_text)
            summaries.append(
                {
                    "title": report.title or "Report",
                    "uploaded_at": report.uploaded_at.isoformat(),
                    "report_date": report.uploaded_at.date().isoformat(),
                    "metrics": metrics,
                    "preview": extracted_text[:240] + ("..." if len(extracted_text) > 240 else ""),
                }
            )
        return summaries

    def _build_due_now_reminder(self, medicine_cards: list[dict[str, object]], target_date) -> str | None:
        if target_date != timezone.localdate():
            return None

        current_hour = timezone.localtime().hour
        current_window = None
        if 5 <= current_hour < 12:
            current_window = "morning"
        elif 12 <= current_hour < 17:
            current_window = "afternoon"
        elif 17 <= current_hour <= 23:
            current_window = "night"

        if not current_window:
            return None

        due_names = []
        for card in medicine_cards:
            for dose in card.get("doses", []):
                if dose.get("timing") == current_window and dose.get("status") == "pending":
                    due_names.append(card.get("name"))

        if not due_names:
            return None

        joined = ", ".join(due_names[:3])
        return f"It is time for your {current_window} medicine: {joined}."

    def _medicine_compliance_summary(self, medication: MedicationSchedule, end_date) -> dict[str, object]:
        start_date = medication.start_date
        last_date = min(end_date, medication.end_date or end_date)
        due_days = max((last_date - start_date).days + 1, 0)
        due_doses = due_days * len(medication.timings)
        taken_doses = medication.dose_logs.filter(status="taken", dose_date__lte=end_date).count()
        missed_doses = medication.dose_logs.filter(status__in=["missed", "skipped"], dose_date__lte=end_date).count()
        compliance = round((taken_doses / due_doses) * 100, 1) if due_doses else 0

        return {
            "medicine": medication.name,
            "compliance_percent": compliance,
            "taken_doses": taken_doses,
            "missed_doses": missed_doses,
            "status": self._medication_status_label(medication, end_date),
        }

    def _build_trend_windows(self, user, end_date) -> list[dict[str, object]]:
        windows = []
        for offset in range(2, -1, -1):
            window_end = end_date - timedelta(days=offset * 7)
            window_start = window_end - timedelta(days=6)
            logs = list(
                DailyHealthLog.objects.filter(
                    user=user,
                    log_date__range=(window_start, window_end),
                )
            )
            if not logs:
                continue

            symptom_days = sum(1 for log in logs if self._clean_symptoms(log.symptoms))
            junk_food_count = sum(1 for log in logs if log.food_type == "junk")
            health_scores = [self._calculate_health_score(log, []) for log in logs]

            windows.append(
                {
                    "label": f"{window_start.isoformat()} to {window_end.isoformat()}",
                    "health_score": round(mean(health_scores), 1) if health_scores else None,
                    "symptom_days": symptom_days,
                    "junk_food_count": junk_food_count,
                }
            )
        return windows

    def _find_missed_doses(self, user, target_date) -> list[dict[str, object]]:
        active_medications = MedicationSchedule.objects.filter(
            user=user,
            start_date__lte=target_date,
            end_date__gte=target_date,
        )
        missed = []

        for medication in active_medications:
            existing_logs = {
                log.timing: log.status
                for log in MedicationDoseLog.objects.filter(medication=medication, dose_date=target_date)
            }
            for timing in medication.timings:
                status = existing_logs.get(timing, "missed")
                if status in {"missed", "skipped"}:
                    missed.append({"name": medication.name, "timing": timing})

        return missed

    def _repeating_symptoms(self, user, end_date, lookback_days=5) -> dict[str, int]:
        start_date = end_date - timedelta(days=lookback_days - 1)
        logs = list(
            DailyHealthLog.objects.filter(
                user=user,
                log_date__range=(start_date, end_date),
            ).order_by("-log_date")
        )
        consecutive_counts: dict[str, int] = {}

        for symptom in {
            item.lower()
            for log in logs
            for item in self._clean_symptoms(log.symptoms)
        }:
            days = 0
            expected_date = end_date
            for log in logs:
                if log.log_date != expected_date:
                    break
                current = {item.lower() for item in self._clean_symptoms(log.symptoms)}
                if symptom not in current:
                    break
                days += 1
                expected_date -= timedelta(days=1)
            consecutive_counts[symptom] = days

        return consecutive_counts

    def _calculate_health_score(self, daily_log: DailyHealthLog | None, medicine_cards: list[dict[str, object]]) -> int:
        if daily_log is None:
            return 50

        score = 100
        symptoms = self._clean_symptoms(daily_log.symptoms)
        if symptoms:
            score -= min(30, len(symptoms) * 7)
        if daily_log.food_type == "junk":
            score -= 10
        elif daily_log.food_type == "outside":
            score -= 5
        if daily_log.water_intake_glasses < 6:
            score -= 8
        if daily_log.sleep_hours is not None and float(daily_log.sleep_hours) < 6:
            score -= 8
        if daily_log.sleep_quality == "poor":
            score -= 6
        if daily_log.stress_level == "high":
            score -= 8
        if daily_log.energy_level == "low":
            score -= 8
        if medicine_cards:
            score -= sum(card["pending_count"] * 3 for card in medicine_cards)
        return max(0, min(100, int(round(score))))

    def _serialize_daily_log(self, log: DailyHealthLog | None) -> dict[str, object] | None:
        if log is None:
            return None
        return {
            "id": log.id,
            "date": str(log.log_date),
            "symptoms": self._clean_symptoms(log.symptoms),
            "symptoms_text": log.symptoms_text,
            "food_type": log.food_type,
            "water_intake_glasses": log.water_intake_glasses,
            "sleep_hours": float(log.sleep_hours) if log.sleep_hours is not None else None,
            "sleep_quality": log.sleep_quality,
            "stress_level": log.stress_level,
            "energy_level": log.energy_level,
            "notes": log.notes,
        }

    def _clean_symptoms(self, symptoms: Iterable[str]) -> list[str]:
        cleaned = []
        seen = set()
        for symptom in symptoms or []:
            value = str(symptom or "").strip()
            if not value:
                continue
            lowered = value.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
            cleaned.append(value)
        return cleaned

    def _medication_status_label(self, medication: MedicationSchedule, target_date=None) -> str:
        target_date = target_date or timezone.localdate()
        if not medication.is_active:
            return "completed"
        if medication.end_date and medication.end_date < target_date:
            return "completed"
        return "ongoing"

    def _dedupe(self, items: Iterable[str]) -> list[str]:
        deduped = []
        seen = set()
        for item in items:
            if item in seen:
                continue
            seen.add(item)
            deduped.append(item)
        return deduped


health_tracking_ai_service = HealthTrackingAIService()
