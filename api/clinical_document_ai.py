from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime


class ClinicalDocumentAIService:
    MEDICINE_CATALOG = [
        "paracetamol",
        "azithromycin",
        "amoxicillin",
        "dolo",
        "pantoprazole",
        "omeprazole",
        "cetirizine",
        "montelukast",
        "crocin",
        "zinc",
        "vitamin d",
        "vitamin b12",
        "ors",
        "ibuprofen",
        "metformin",
        "telmisartan",
        "amlodipine",
        "atorvastatin",
    ]

    TIMING_HINTS = {
        "morning": ("morning", "before breakfast", "after breakfast", "od", "1-0-0"),
        "afternoon": ("afternoon", "after lunch", "before lunch", "0-1-0"),
        "night": ("night", "at bedtime", "after dinner", "before dinner", "0-0-1", "hs"),
    }

    TEST_RECOMMENDATIONS = {
        "dengue": ["CBC / platelet count", "NS1 antigen test", "Hydration monitoring"],
        "typhoid": ["Typhoid test", "CBC", "Doctor consultation if fever continues"],
        "influenza": ["Flu test", "Temperature monitoring", "Doctor review if breathing worsens"],
        "malaria": ["Malaria test", "CBC", "Doctor consultation"],
        "diarrhea": ["Stool test", "Hydration check", "Doctor consultation if dehydration signs appear"],
        "covid": ["COVID test", "Oxygen monitoring", "Doctor review if symptoms worsen"],
        "tuberculosis": ["Chest X-ray", "Sputum test", "Doctor consultation"],
        "cholera": ["Stool test", "Hydration assessment", "Urgent doctor consultation"],
        "hepatitis": ["Liver function test", "Bilirubin test", "Doctor consultation"],
    }

    LAB_PATTERNS = {
        "Hemoglobin": re.compile(r"\b(?:hemoglobin|hb)\b[:\s-]*([0-9]+(?:\.[0-9]+)?)\s*(g/dl|gm/dl|g%)?", re.IGNORECASE),
        "Sugar": re.compile(r"\b(?:blood sugar|sugar|glucose|fbs|rbs)\b[:\s-]*([0-9]+(?:\.[0-9]+)?)\s*(mg/dl)?", re.IGNORECASE),
        "Vitamin D": re.compile(r"\b(?:vitamin\s*d|vit\s*d)\b[:\s-]*([0-9]+(?:\.[0-9]+)?)\s*(ng/ml)?", re.IGNORECASE),
        "Vitamin B12": re.compile(r"\b(?:vitamin\s*b12|vit\s*b12)\b[:\s-]*([0-9]+(?:\.[0-9]+)?)\s*(pg/ml)?", re.IGNORECASE),
        "Platelet Count": re.compile(r"\b(?:platelet|platelet count)\b[:\s-]*([0-9]+(?:\.[0-9]+)?)\s*(?:lakh|lakhs|/cumm|x10\^3/ul)?", re.IGNORECASE),
        "WBC": re.compile(r"\b(?:wbc|white blood cells?)\b[:\s-]*([0-9]+(?:\.[0-9]+)?)", re.IGNORECASE),
        "TSH": re.compile(r"\b(?:tsh)\b[:\s-]*([0-9]+(?:\.[0-9]+)?)\s*(uiu/ml|miu/l)?", re.IGNORECASE),
    }

    def extract_prescription_medicines(self, text: str) -> list[dict[str, object]]:
        cleaned_text = " ".join(str(text or "").split())
        if not cleaned_text:
            return []

        medicines = []
        seen = set()
        for medicine_name in self.MEDICINE_CATALOG:
            if re.search(rf"\b{re.escape(medicine_name)}\b", cleaned_text, re.IGNORECASE):
                normalized_name = medicine_name.title()
                if normalized_name.lower() in seen:
                    continue
                seen.add(normalized_name.lower())
                medicines.append(
                    {
                        "name": normalized_name,
                        "dose": self._extract_dose(cleaned_text, medicine_name),
                        "duration_days": self._extract_duration(cleaned_text),
                        "timings": self._extract_timings(cleaned_text),
                        "instructions": self._extract_instruction_snippet(cleaned_text, medicine_name),
                    }
                )

        if medicines:
            return medicines

        line_candidates = re.split(r"(?:\n|\. )+", text or "")
        for line in line_candidates:
            line = " ".join(line.split())
            if not line:
                continue
            if not re.search(r"\b(?:tab|tablet|capsule|cap|syrup|mg|ml)\b", line, re.IGNORECASE):
                continue
            name_match = re.match(r"([A-Za-z][A-Za-z0-9 +\-]{2,40})", line)
            if not name_match:
                continue
            name = name_match.group(1).strip().title()
            if name.lower() in seen:
                continue
            seen.add(name.lower())
            medicines.append(
                {
                    "name": name,
                    "dose": self._extract_generic_dose(line),
                    "duration_days": self._extract_duration(line),
                    "timings": self._extract_timings(line),
                    "instructions": line,
                }
            )

        return medicines

    def extract_lab_metrics(self, text: str) -> list[dict[str, object]]:
        cleaned_text = " ".join(str(text or "").split())
        metrics = []

        for label, pattern in self.LAB_PATTERNS.items():
            for match in pattern.finditer(cleaned_text):
                value = match.group(1)
                unit = match.group(2) if match.lastindex and match.lastindex >= 2 else ""
                metrics.append(
                    {
                        "parameter": label,
                        "value": value,
                        "unit": unit or "",
                        "status": self._infer_metric_status(label, value),
                    }
                )
                break

        deduped = []
        seen = set()
        for metric in metrics:
            key = metric["parameter"].lower()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(metric)
        return deduped

    def build_report_trends(self, reports_with_metrics: list[dict[str, object]]) -> list[dict[str, object]]:
        grouped: dict[str, list[dict[str, object]]] = defaultdict(list)

        for item in reports_with_metrics:
            report_date = item.get("report_date")
            for metric in item.get("metrics", []):
                try:
                    numeric_value = float(metric.get("value"))
                except (TypeError, ValueError):
                    continue
                grouped[metric["parameter"]].append(
                    {
                        "report_date": report_date,
                        "value": numeric_value,
                        "unit": metric.get("unit") or "",
                    }
                )

        trends = []
        for parameter, points in grouped.items():
            if len(points) < 2:
                continue
            points = sorted(points, key=lambda item: item["report_date"] or "")
            trends.append(
                {
                    "parameter": parameter,
                    "values": points,
                    "trend": self._trend_label(points[0]["value"], points[-1]["value"]),
                }
            )
        return trends

    def recommended_tests_for_problem(self, detected_problem: str, matched_symptoms: list[str]) -> list[str]:
        normalized_problem = str(detected_problem or "").strip().lower()
        for key, tests in self.TEST_RECOMMENDATIONS.items():
            if key in normalized_problem:
                return tests

        symptoms = {item.lower() for item in matched_symptoms or []}
        if "fever" in symptoms:
            return ["CBC", "Temperature monitoring", "Doctor consultation if fever continues"]
        if "cough" in symptoms or "shortness of breath" in symptoms:
            return ["Respiratory examination", "Oxygen monitoring", "Doctor consultation"]
        if "abdominal pain" in symptoms or "diarrhea" in symptoms:
            return ["Stool test", "Hydration assessment", "Doctor consultation if symptoms persist"]
        return ["Doctor consultation for further evaluation"]

    def _extract_dose(self, text: str, medicine_name: str) -> str:
        pattern = re.compile(
            rf"{re.escape(medicine_name)}[^.:\n]*?\b([0-9]+(?:\.[0-9]+)?\s*(?:mg|ml|tablet|tab|capsule|cap|teaspoon|tsp))\b",
            re.IGNORECASE,
        )
        match = pattern.search(text)
        return match.group(1) if match else self._extract_generic_dose(text)

    def _extract_generic_dose(self, text: str) -> str:
        match = re.search(r"\b([0-9]+(?:\.[0-9]+)?\s*(?:mg|ml|tablet|tab|capsule|cap|teaspoon|tsp))\b", text, re.IGNORECASE)
        return match.group(1) if match else ""

    def _extract_duration(self, text: str) -> int:
        match = re.search(r"\bfor\s+([0-9]{1,3})\s+days?\b", text, re.IGNORECASE)
        if not match:
            match = re.search(r"\b([0-9]{1,3})\s+days?\b", text, re.IGNORECASE)
        if match:
            return max(1, int(match.group(1)))
        return 5

    def _extract_timings(self, text: str) -> list[str]:
        found = []
        lowered_text = text.lower()
        for timing, hints in self.TIMING_HINTS.items():
            if any(hint in lowered_text for hint in hints):
                found.append(timing)
        return found or ["morning", "night"]

    def _extract_instruction_snippet(self, text: str, medicine_name: str) -> str:
        match = re.search(rf"([^.\n]*{re.escape(medicine_name)}[^.\n]*)", text, re.IGNORECASE)
        return " ".join(match.group(1).split()) if match else ""

    def _infer_metric_status(self, label: str, value: str) -> str:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return "Unknown"

        if label == "Hemoglobin":
            return "Low" if numeric < 12 else "Normal"
        if label == "Sugar":
            return "High" if numeric > 140 else "Normal"
        if label == "Vitamin D":
            return "Deficient" if numeric < 20 else "Normal"
        if label == "Vitamin B12":
            return "Low" if numeric < 200 else "Normal"
        if label == "Platelet Count":
            return "Low" if numeric < 150 else "Normal"
        if label == "TSH":
            return "High" if numeric > 4.5 else "Normal"
        return "Normal"

    def _trend_label(self, start_value: float, end_value: float) -> str:
        if end_value > start_value:
            return "increasing"
        if end_value < start_value:
            return "decreasing"
        return "stable"


clinical_document_ai_service = ClinicalDocumentAIService()
