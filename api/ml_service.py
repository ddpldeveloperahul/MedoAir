"""
Utility service for symptom-based disease prediction.
"""

from __future__ import annotations

import csv
import json
import random
import re
import threading
from collections import Counter
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from statistics import mean
from typing import Iterable

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_val_score
from sklearn.pipeline import Pipeline
from .clinical_document_ai import clinical_document_ai_service


@dataclass(frozen=True)
class DatasetConfig:
    disease: str
    display_name: str
    file_name: str


@dataclass(frozen=True)
class KnowledgeEntry:
    disease: str
    display_name: str
    topic: str
    question: str
    answer: str


@dataclass(frozen=True)
class DatasetKnowledgeChunk:
    disease: str
    display_name: str
    section: str
    field: str
    topic: str
    text: str


class DiseasePredictionService:
    MODEL_NAME = "LogisticRegression"
    CROSS_VALIDATION_FOLDS = 5
    HIGH_CONFIDENCE_THRESHOLD = 85.0
    MINIMUM_CONFIDENCE_THRESHOLD = 50.0
    UNCERTAIN_MARGIN_THRESHOLD = 8.0
    FUZZY_MATCH_THRESHOLD = 0.84
    HINDI_SCRIPT_PATTERN = re.compile(r"[\u0900-\u097F]")
    NEGATION_MARKERS = {
        "no", "not", "without", "never", "nahi", "nahin", "na", "mat", "deny", "denies", "denied",
    }
    FRAGMENT_STOPWORDS = {
        "i", "have", "mujhe", "mujhko", "mere", "main", "mai", "feeling", "having",
        "ho", "rahi", "raha", "hai", "hain", "bas", "sirf", "only", "just",
    }
    HINGLISH_MARKERS = {
        "mujhe", "mere", "mera", "meri", "mai", "main", "hai", "ho", "hora", "hori",
        "bukhar", "sar", "sir", "dard", "khansi", "gala", "pet", "saans", "ulti",
        "dast", "kamzori", "thakan", "nahi", "kharab",
    }
    ENGLISH_MARKERS = {
        "i", "have", "am", "feeling", "with", "pain", "fever", "cough", "headache",
        "today", "since", "body", "throat", "stomach", "breathing",
    }
    DATASETS = (
        DatasetConfig("dengue", "Dengue", "dengue_dataset_clear.csv"),
        DatasetConfig("diarrhoea", "Diarrhoea", "diarahhe_dataset_clear.csv"),
        DatasetConfig("influenza", "Influenza", "influnza_dataset_clear.csv"),
        DatasetConfig("malaria", "Malaria", "maleria_dataset_clear.csv"),
        DatasetConfig("tuberculosis", "Tuberculosis", "tuber_dataset_clear.csv"),
        DatasetConfig("typhoid", "Typhoid", "typhoidfewer_dataset_clear.csv"),
    )

    INCLUDE_HINTS = (
        "symptom",
        "symptoms",
        "clinical feature",
        "clinical features",
        "clinical presentation",
        "clinical illness",
        "clinical signs",
        "signs and symptoms",
        "clinical manifestations",
        "warning signs",
        "red flags",
        "dehydration signs",
    )

    SYMPTOM_SECTION_EXCLUDE_HINTS = (
        "chatbot",
        "faq",
        "intent",
        "support",
        "capabilities",
        "surveillance",
        "carrier",
        "clearance",
        "testing",
        "pregnancy",
        "breastfeeding",
        "prevention",
        "vaccination",
        "public health",
    )

    EXCLUDE_HINTS = (
        "duration",
        "example",
        "examples",
        "alias",
        "mortality",
        "fatality",
        "criteria",
        "definition",
        "description",
        "management",
        "diagnosis",
        "diagnostic",
        "treatment",
        "prevention",
        "vaccine",
        "vaccination",
        "control",
        "agent",
        "agents",
        "pathogen",
        "pathogens",
        "cause",
        "causes",
        "location",
        "locations",
        "size",
        "color",
        "colour",
        "year",
        "percent",
        "risk multiplier",
        "mortality driver",
        "driver",
        "trend",
        "impact",
        "supportive care",
    )

    NOISE_VALUES = {
        "face",
        "neck",
        "chest",
        "abdomen",
        "back",
        "arms",
        "legs",
        "true",
        "false",
        "none",
        "present",
        "majority",
        "cholera",
        "dysentery",
        "shigella",
        "salmonella",
        "campylobacter",
        "rotavirus",
        "vibrio cholerae",
        "enterotoxigenic e. coli (etec)",
        "etec",
        "giardia",
        "cryptosporidium",
        "eaec",
        "epec",
        "hours to days",
        "14 days or more",
        ">14 days",
    }

    TEXT_BLOCK_KEYS = (
        "clinical_signs",
        "clinical_features",
        "clinical_presentation",
        "clinical_manifestations",
        "symptoms",
        "warning_signs",
        "red_flags",
        "most_sensitive_symptoms",
        "general_symptoms",
        "common_symptoms",
        "respiratory_symptoms",
        "gastrointestinal_symptoms",
        "systemic_symptoms",
    )

    DETAIL_TEXT_KEYS = {
        "warning_signs": (
            "warning_signs",
            "red_flags",
            "emergency_warning_signs",
            "early_warning_signs",
            "return_immediately_if",
        ),
        "care_guidance": (
            "supportive_care",
            "supportive_management",
            "home_isolation",
            "hygiene_measures",
            "personal_protection",
            "non_pharmaceutical_measures",
            "nutrition_support",
            "recommended_actions",
        ),
        "medicine_guidance": (
            "antivirals",
            "antiviral_drugs",
            "antiviral_medications",
            "antiviral_therapy",
            "antibiotics",
            "first_line_antibiotics",
            "recommended_drugs",
            "common_drugs",
            "alternative_agents",
        ),
    }

    WARNING_HINTS = (
        "warning",
        "red flag",
        "emergency",
        "return immediately",
        "urgent",
        "danger sign",
        "seek medical care",
        "seek immediate care",
        "severe symptom",
    )

    CARE_HINTS = (
        "management",
        "supportive care",
        "supportive management",
        "standard care",
        "home care",
        "treatment",
        "prevention",
        "guidance",
        "nutrition",
        "hydration",
        "fluid",
        "isolation",
        "protection",
        "recommendation",
        "action",
    )

    CARE_EXCLUDE_HINTS = (
        "diagnosis",
        "diagnostic",
        "test",
        "surveillance",
        "vaccine",
        "vaccination",
        "monitoring",
        "source",
        "metadata",
        "chatbot",
        "resistance",
        "compiled",
        "reviewed",
    )

    MEDICINE_HINTS = (
        "drug",
        "antiviral",
        "antibiotic",
        "antimalarial",
        "medicine",
        "medication",
        "first line",
        "second line",
        "alternative agent",
        "recommended drug",
        "regimen",
        "chemoprophylaxis",
        "therapy",
    )

    MEDICATION_VALUE_PATTERN = re.compile(
        r"\b("
        r"paracetamol|oseltamivir|zanamivir|ciprofloxacin|azithromycin|ceftriaxone|"
        r"cefixime|norfloxacin|ofloxacin|chloroquine|artesunate|artemether|"
        r"lumefantrine|piperaquine|doxycycline|mefloquine|atovaquone|proguanil|"
        r"zinc|ors|oral rehydration solution|crystalloid fluids|intravenous fluids|"
        r"iv fluids|blood transfusion|platelet transfusion"
        r")\b",
        re.IGNORECASE,
    )

    COMMON_SYMPTOM_ALIASES = {
        "fever": ("bukhar", "bukhar hora hai", "bukhar ho raha hai", "high fever", "temperature", "body temperature"),
        "cough": ("khansi", "dry cough", "severe cough"),
        "sore throat": ("gala kharab", "gale mein dard", "gala me dard", "gala mai dard", "throat pain"),
        "headache": ("sar dard", "sar me dard", "sar mai dard", "sir dard", "sir me dard", "sir mai dard", "head pain"),
        "fatigue": ("kamzori", "weakness", "thakan", "tiredness"),
        "joint pain": ("jodon mein dard", "jodo me dard", "joint ache"),
        "muscle pain": ("body pain", "body me pain", "body mai pain", "badan dard", "body ache"),
        "chills": ("thand lagna", "kapkapi"),
        "sweats": ("paseena", "bahut paseena", "sweating"),
        "nausea": ("jee machalna", "nauseous"),
        "vomiting": ("ulti", "vomit"),
        "diarrhea": ("loose motion", "loose motions", "motions", "dast"),
        "abdominal pain": ("pet dard", "pet me dard", "pet mai dard", "stomach pain", "tummy pain"),
        "constipation": ("kabz", "qabz", "pet saaf nahi ho raha", "hard stool", "stool hard"),
        "chest pain": ("seene mein dard", "seene me dard", "chest tightness"),
        "shortness of breath": ("saans phoolna", "saans lene me dikkat", "breathing difficulty"),
        "runny nose": ("naak behna", "runny nostril"),
        "rash": ("skin rash", "daane", "rashes"),
        "night sweats": ("raat mein paseena", "night sweating"),
        "weight loss": ("wazan kam hona", "weight dropping"),
        "loss of appetite": ("bhook nahi lag rahi", "bhook kam lag rahi", "bhook nahi lagti", "appetite low"),
        "dry mouth": ("muh sukh raha hai", "munh sukh raha hai", "dry mouth"),
    }

    DATASET_CANONICAL_SYMPTOMS = {
        "fever": (
            "fever", "high fever", "persistent fever", "prolonged fever",
            "gradual onset fever", "sudden high fever", "fever >37.5", "fever >=38",
        ),
        "cough": ("cough", "coughing", "dry cough", "persistent cough", "productive cough"),
        "sore throat": ("sore throat", "throat pain", "mild throat pain"),
        "runny nose": ("runny nose", "nasal discharge", "nasal congestion", "sneezing"),
        "headache": ("headache", "severe headache", "frontal headache"),
        "fatigue": ("fatigue", "lethargy", "malaise", "weakness", "extreme weakness", "severe weakness"),
        "muscle pain": ("muscle pain", "muscle aches", "body aches", "body pain", "myalgia"),
        "joint pain": ("joint pain", "arthralgia", "bone or joint pain"),
        "chills": ("chills", "rigor", "rigors", "cold shivers"),
        "sweats": ("sweats", "hot sweats", "sweating"),
        "night sweats": ("night sweats",),
        "nausea": ("nausea",),
        "vomiting": ("vomiting", "vomit", "persistent vomiting"),
        "diarrhea": (
            "diarrhea", "diarrhoea", "bloody diarrhea", "frequent loose or watery stools",
            "loose or watery stools", "three or more loose stools in 24 hours",
        ),
        "abdominal pain": ("abdominal pain", "abdominal tenderness", "abdominal cramps"),
        "shortness of breath": ("shortness of breath", "breathlessness", "respiratory distress"),
        "chest pain": ("chest pain",),
        "rash": ("rash", "rose spots", "maculopapular lesions", "skin rash"),
        "loss of appetite": ("loss of appetite", "reduced appetite", "anorexia"),
        "bleeding": ("bleeding", "mucosal bleeding", "minor bleeding", "severe bleeding", "gi bleeding"),
        "dehydration": ("dehydration", "thirst", "loss of skin turgor", "sunken eyes", "decreased urination"),
        "coughing up blood": ("coughing up blood", "hemoptysis", "bloody sputum"),
        "weight loss": ("weight loss",),
        "confusion": ("confusion",),
        "jaundice": ("jaundice",),
        "dizziness": ("giddiness", "syncope", "dizziness"),
        "lymph node swelling": ("swollen lymph nodes", "lymph node swelling", "painless swelling"),
    }

    DISEASE_SYMPTOM_WHITELIST = {
        "dengue": {
            "fever", "headache", "muscle pain", "joint pain", "rash", "nausea", "vomiting",
            "abdominal pain", "bleeding", "fatigue", "chills", "decreased urine output",
            "shortness of breath", "dizziness",
        },
        "diarrhoea": {
            "diarrhea", "abdominal pain", "nausea", "vomiting", "dehydration",
            "increased stool frequency", "blood or mucus in stool", "dry mouth", "dark urine",
            "dizziness", "reduced urination", "unusual sleepiness", "bloating", "urgency",
            "fatigue", "fever",
        },
        "influenza": {
            "fever", "cough", "sore throat", "runny nose", "headache", "muscle pain",
            "fatigue", "chills", "shortness of breath", "loss of appetite",
        },
        "malaria": {
            "fever", "chills", "headache", "muscle pain", "fatigue", "vomiting", "sweats",
            "nausea", "jaundice", "abdominal pain", "diarrhea", "joint pain", "shortness of breath",
        },
        "tuberculosis": {
            "fever", "night sweats", "weight loss", "fatigue", "loss of appetite", "chest pain",
            "cough", "coughing up blood", "shortness of breath", "lymph node swelling",
            "back pain", "confusion",
        },
        "typhoid": {
            "fever", "headache", "fatigue", "loss of appetite", "cough", "constipation",
            "diarrhea", "abdominal pain", "rash", "nausea", "vomiting", "bleeding",
        },
    }

    DISEASE_RULE_BOOSTS = {
        "dengue": (
            {
                "name": "dengue_fever_pain_rash_pattern",
                "all_of": ("fever",),
                "group_any_of": (
                    ("joint pain", "muscle pain"),
                    ("rash", "bleeding"),
                    ("nausea", "vomiting", "abdominal pain", "headache", "fatigue"),
                ),
                "multiplier": 2.2,
            },
        ),
        "diarrhoea": (
            {
                "name": "diarrhea_digestive_dehydration_pattern",
                "all_of": ("diarrhea",),
                "group_any_of": (
                    ("dehydration", "dry mouth", "dark urine", "reduced urination", "unusual sleepiness"),
                    ("abdominal pain", "bloating", "urgency"),
                    ("vomiting", "nausea"),
                ),
                "multiplier": 2.5,
            },
        ),
        "typhoid": (
            {
                "name": "typhoid_fever_abdomen_constipation_pattern",
                "all_of": ("fever",),
                "group_any_of": (
                    ("abdominal pain", "constipation", "diarrhea"),
                    ("headache", "fatigue", "loss of appetite"),
                ),
                "multiplier": 1.9,
            },
        ),
        "malaria": (
            {
                "name": "malaria_fever_chills_sweats_pattern",
                "all_of": ("fever", "chills"),
                "group_any_of": (
                    ("sweats",),
                    ("vomiting", "nausea", "headache", "muscle pain", "fatigue"),
                ),
                "multiplier": 1.6,
            },
        ),
    }

    QUESTION_PREFIXES = (
        "what ", "how ", "do ", "does ", "did ", "is ", "are ", "can ", "should ",
        "when ", "why ", "which ", "who ", "where ",
    )

    KNOWLEDGE_TOPIC_HINTS = {
        "definition": ("what is", "definition", "overview", "about", "meaning"),
        "cause": ("cause", "causes", "why", "agent"),
        "transmission": ("spread", "transmission", "airborne", "catch", "infectious"),
        "risk": ("risk", "who is at risk", "dangerous", "severe", "high risk"),
        "symptoms": ("symptom", "sign", "start"),
        "testing": ("test", "testing", "diagnosis", "diagnostic", "confirmed", "detect"),
        "treatment": ("treat", "treated", "treatment", "medicine", "drug", "dot", "curable", "antibiotic"),
        "prevention": ("prevent", "prevention", "avoid", "protection", "vaccine"),
    }

    DISEASE_QUERY_ALIASES = {
        "tb": "tuberculosis",
        "tuberculosis": "tuberculosis",
        "typhoid": "typhoid",
        "typhoid fever": "typhoid",
        "dengue": "dengue",
        "dengue fever": "dengue",
        "malaria": "malaria",
        "flu": "influenza",
        "influenza": "influenza",
        "diarrhea": "diarrhoea",
        "diarrhoea": "diarrhoea",
    }

    NON_HUMAN_HINTS = (
        "avian", "poultry", "bird", "birds", "chicken", "chickens", "turkey", "turkeys",
        "duck", "ducks", "swine", "pig", "pigs", "cattle", "livestock", "goat", "goats",
        "sheep", "bat", "bats", "comb", "wattles", "egg", "feed intake", "cloacal",
        "tracheal", "wild birds", "aquatic birds",
    )

    OUTCOME_OR_METADATA_HINTS = (
        "death", "organ failure", "renal failure", "circulatory collapse", "sepsis",
        "pneumonia", "secondary bacterial infection", "systemic illness", "neurological signs",
        "encephalitis", "myocarditis", "multi-organ failure", "acute respiratory distress",
        "majority of infections", "common in semi-immune populations", "up to ",
        "every 48 hours", "every 72 hours", "every 24 hours", "48 hours", "72 hours", "24 hours",
        "brain and spinal cord", "genitourinary system", "bones and joints",
        "bones", "joints", "brain", "spine", "kidneys", "genital tract", "eye", "skin",
        "warning signs present", "shock", "dss", "hematocrit rise", "rapidly falling platelet count",
        "clinical fluid accumulation", "rising hematocrit", "poor feeding", "reduced water intake",
        "reduced feed intake", "poor egg quality", "drop in egg production", "decreased egg production",
        "reduced egg production", "cyanosis", "hemorrhages", "oedema", "respiratory signs", "nervous signs",
        "edema", "ocular discharge", "swelling of head", "sinuses", "incoordination", "cytokine storm",
        "respiratory failure", "ards", "coma", "seizures", "irregular", "cold stage", "liver stage",
        "anemia", "splenomegaly", "impaired consciousness", "multiple convulsions", "joint swelling",
        "meningitis symptoms", "sputum production", "neck stiffness", "dysuria", "infertility",
        "relative bradycardia", "hepatomegaly", "mental dullness", "slight deafness", "neurologic manifestations",
        "intestinal perforation", "delirium", "meningitis", "guillain", "toxic appearance", "failure to thrive",
        "flu-like symptoms", "swelling", "bluish lips", "sudden worsening after improvement",
    )

    ARRAY_PATTERN = re.compile(r"\[(.*?)\]", re.DOTALL)
    QUOTED_VALUE_PATTERN = re.compile(r'"([^"]+)"')

    def __init__(self) -> None:
        self.datasets_dir = Path(__file__).resolve().parents[1] / "datasets"
        self._lock = threading.Lock()
        self._pipeline: Pipeline | None = None
        self._symptom_bank: dict[str, list[str]] = {}
        self._symptom_lookup: list[tuple[str, str]] = []
        self._metadata: dict[str, object] | None = None
        self._dataset_details: dict[str, dict[str, list[str]]] = {}
        self._knowledge_entries: list[KnowledgeEntry] = []
        self._knowledge_topics: dict[str, dict[str, list[str]]] = {}
        self._knowledge_chunks: list[DatasetKnowledgeChunk] = []
        self._knowledge_vectorizer: TfidfVectorizer | None = None
        self._knowledge_matrix = None

    def metadata(self) -> dict[str, object]:
        self._ensure_model()
        return self._metadata or {}

    def predict(self, symptoms: Iterable[str], top_k: int = 3) -> dict[str, object]:
        self._ensure_model()

        cleaned_symptoms = [self._clean_text(item) for item in symptoms if self._clean_text(item)]
        if not cleaned_symptoms:
            raise ValueError("At least one symptom is required")

        canonical_input_symptoms = self._canonicalize_symptoms_for_rules(cleaned_symptoms)
        symptom_text = ", ".join(canonical_input_symptoms or cleaned_symptoms)
        base_probabilities = self._pipeline.predict_proba([symptom_text])[0]
        adjusted_probabilities, canonical_input_symptoms, triggered_rule_signals = self._apply_rule_based_adjustments(
            probabilities=base_probabilities,
            symptoms=cleaned_symptoms,
        )
        ranked_indices = sorted(
            range(len(adjusted_probabilities)),
            key=lambda index: adjusted_probabilities[index],
            reverse=True,
        )[:top_k]

        predictions = []
        for index in ranked_indices:
            disease_key = self._pipeline.classes_[index]
            predictions.append(
                {
                    "disease": disease_key,
                    "display_name": self._display_name_for(disease_key),
                    "confidence": round(float(adjusted_probabilities[index]) * 100, 2),
                    "model_confidence": round(float(base_probabilities[index]) * 100, 2),
                    "sample_symptoms": self._symptom_bank.get(disease_key, [])[:6],
                }
            )

        top_prediction = predictions[0]
        second_prediction = predictions[1] if len(predictions) > 1 else None
        confidence_margin = round(
            float(top_prediction["confidence"]) - float(second_prediction["confidence"] if second_prediction else 0.0),
            2,
        )
        prediction_quality = self._build_prediction_quality(
            top_prediction["confidence"],
            confidence_margin_percent=confidence_margin,
        )
        is_uncertain = bool(prediction_quality["is_uncertain"])
        return {
            "input_symptoms": cleaned_symptoms,
            "canonical_input_symptoms": canonical_input_symptoms,
            "predicted_disease": top_prediction["disease"] if not is_uncertain else "uncertain",
            "predicted_display_name": top_prediction["display_name"] if not is_uncertain else "Uncertain",
            "confidence": top_prediction["confidence"],
            "confidence_margin_percent": confidence_margin,
            "closest_known_match": top_prediction,
            "top_predictions": predictions,
            "triggered_rule_signals": triggered_rule_signals,
            "prediction_status": "uncertain" if is_uncertain else "matched",
            "is_uncertain": is_uncertain,
            "model": self.MODEL_NAME,
            "model_performance": self._build_model_performance_summary(),
            "prediction_quality": prediction_quality,
        }

    def assistant_reply(
        self,
        message: str = "",
        symptoms: Iterable[str] | None = None,
        symptoms_text: str = "",
        notes: str = "",
        log_date: object | None = None,
        food_type: str = "",
        water_intake_glasses: object | None = None,
        sleep_hours: object | None = None,
        sleep_quality: str = "",
        stress_level: str = "",
        energy_level: str = "",
        top_k: int = 3,
    ) -> dict[str, object]:
        self._ensure_model()

        cleaned_message = self._clean_text(
            " ".join(
                part for part in [message, symptoms_text, notes] if self._clean_text(part)
            )
        )
        provided_symptoms = [
            self._clean_text(item)
            for item in (symptoms or [])
            if self._clean_text(item)
        ]

        if not cleaned_message and not provided_symptoms:
            raise ValueError("Please describe your symptoms first.")

        response_language = self._detect_response_language(message, symptoms_text, notes)
        submitted_context = self._build_context_summary(
            response_language=response_language,
            log_date=log_date,
            food_type=food_type,
            water_intake_glasses=water_intake_glasses,
            sleep_hours=sleep_hours,
            sleep_quality=sleep_quality,
            stress_level=stress_level,
            energy_level=energy_level,
        )

        if cleaned_message and self._looks_like_question_text(cleaned_message):
            knowledge_response = self._answer_knowledge_query(
                query=cleaned_message,
                response_language=response_language,
                submitted_context=submitted_context,
            )
            if knowledge_response is not None:
                return knowledge_response

        negated_symptoms = self._extract_negated_symptoms_from_message(cleaned_message)
        matched_symptoms = self._dedupe_preserve_order(
            provided_symptoms + self._extract_symptoms_from_message(cleaned_message)
        )
        if not matched_symptoms:
            raise ValueError(
                "I could not identify clear symptoms from your message. Try phrases like fever, cough, headache, vomiting, diarrhea, or body pain."
            )

        prediction = self.predict(matched_symptoms, top_k=top_k)
        top_prediction = prediction["top_predictions"][0]
        closest_known_match = prediction.get("closest_known_match") or top_prediction
        disease_details = self._dataset_details.get(closest_known_match["disease"], {})

        return {
            "message": cleaned_message,
            "matched_symptoms": matched_symptoms,
            "recognized_negated_symptoms": negated_symptoms,
            "prediction": prediction,
            "detected_problem": prediction["predicted_display_name"],
            "closest_dataset_match": closest_known_match,
            "response_language": response_language,
            "assistant_response": self._build_assistant_response(
                prediction=prediction,
                matched_symptoms=matched_symptoms,
                disease_details=disease_details,
                response_language=response_language,
            ),
            "dataset_reference_symptoms": disease_details.get("reference_symptoms", closest_known_match["sample_symptoms"]),
            "care_guidance": disease_details.get("care_guidance", []),
            "medicine_guidance": disease_details.get("medicine_guidance", []),
            "warning_signs": disease_details.get("warning_signs", []),
            "recommended_tests": clinical_document_ai_service.recommended_tests_for_problem(
                closest_known_match["display_name"],
                matched_symptoms,
            ),
            "model_performance": prediction.get("model_performance") or self._build_model_performance_summary(),
            "prediction_quality": prediction.get("prediction_quality") or self._build_prediction_quality(
                top_prediction["confidence"],
                confidence_margin_percent=float(prediction.get("confidence_margin_percent") or 0.0),
            ),
            "submitted_context": submitted_context,
            "follow_up_questions": self._build_follow_up_questions(
                predicted_display_name=prediction["predicted_display_name"],
                closest_match_display_name=closest_known_match["display_name"],
                is_uncertain=bool(prediction.get("is_uncertain")),
                response_language=response_language,
            ),
            "note": self._build_note(response_language),
        }

    def _ensure_model(self) -> None:
        if self._pipeline is not None:
            return

        with self._lock:
            if self._pipeline is not None:
                return

            texts: list[str] = []
            labels: list[str] = []
            symptom_bank: dict[str, list[str]] = {}
            dataset_details: dict[str, dict[str, list[str]]] = {}
            knowledge_entries: list[KnowledgeEntry] = []
            knowledge_topics: dict[str, dict[str, list[str]]] = {}
            knowledge_chunks: list[DatasetKnowledgeChunk] = []
            dataset_row_counts: dict[str, int] = {}
            knowledge_chunk_counts: dict[str, int] = {}
            training_sample_counts: dict[str, int] = {}

            for config in self.DATASETS:
                symptoms = self._extract_symptoms_for_dataset(config)
                if not symptoms:
                    continue

                symptom_bank[config.disease] = symptoms
                dataset_details[config.disease] = self._extract_dataset_details(config, symptoms)
                topic_map, dataset_knowledge_entries = self._build_dataset_knowledge(config)
                dataset_chunks, dataset_row_count = self._build_dataset_knowledge_chunks(config)
                knowledge_topics[config.disease] = topic_map
                knowledge_entries.extend(dataset_knowledge_entries)
                knowledge_chunks.extend(dataset_chunks)
                dataset_row_counts[config.disease] = dataset_row_count
                knowledge_chunk_counts[config.disease] = len(dataset_chunks)
                samples = self._build_training_samples(config.disease, symptoms)
                training_sample_counts[config.disease] = len(samples)
                texts.extend(samples)
                labels.extend([config.disease] * len(samples))

            if not texts:
                raise RuntimeError("No training samples could be prepared from the dataset files")

            self._pipeline = Pipeline(
                steps=[
                    (
                        "tfidf",
                        TfidfVectorizer(
                            lowercase=True,
                            ngram_range=(1, 2),
                            min_df=1,
                        ),
                    ),
                    (
                        "classifier",
                        LogisticRegression(
                            max_iter=1000,
                            random_state=42,
                        ),
                    ),
                ]
            )
            self._pipeline.fit(texts, labels)
            vectorizer: TfidfVectorizer = self._pipeline.named_steps["tfidf"]
            evaluation = self._evaluate_model(
                texts=texts,
                labels=labels,
                symptom_bank=symptom_bank,
            )

            self._symptom_bank = symptom_bank
            self._symptom_lookup = self._build_symptom_lookup(symptom_bank)
            self._dataset_details = dataset_details
            self._knowledge_entries = knowledge_entries
            self._knowledge_topics = knowledge_topics
            self._knowledge_chunks = knowledge_chunks
            self._knowledge_vectorizer = None
            self._knowledge_matrix = None
            if knowledge_chunks:
                self._knowledge_vectorizer = TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 2),
                    min_df=1,
                )
                self._knowledge_matrix = self._knowledge_vectorizer.fit_transform(
                    [chunk.text for chunk in knowledge_chunks]
                )
            self._metadata = {
                "model": self.MODEL_NAME,
                "trained_samples": len(texts),
                "supported_diseases": [
                    {
                        "disease": config.disease,
                        "display_name": config.display_name,
                        "dataset_file": config.file_name,
                        "dataset_row_count": dataset_row_counts.get(config.disease, 0),
                        "training_sample_count": training_sample_counts.get(config.disease, 0),
                        "knowledge_chunk_count": knowledge_chunk_counts.get(config.disease, 0),
                        "symptom_count": len(symptom_bank.get(config.disease, [])),
                        "sample_symptoms": symptom_bank.get(config.disease, [])[:8],
                    }
                    for config in self.DATASETS
                    if config.disease in symptom_bank
                ],
                "dataset_inventory": self._build_dataset_inventory(
                    dataset_row_counts=dataset_row_counts,
                    knowledge_chunk_counts=knowledge_chunk_counts,
                    training_sample_counts=training_sample_counts,
                ),
                "knowledge_index": {
                    "total_indexed_chunks": len(knowledge_chunks),
                    "loaded_dataset_rows": sum(dataset_row_counts.values()),
                    "note": (
                        "The symptom model trains on curated symptom patterns, and the raw dataset rows are "
                        "indexed for dataset-based question answering."
                    ),
                },
                "vocabulary_size": len(vectorizer.vocabulary_),
                "evaluation": evaluation,
            }

    def _evaluate_model(
        self,
        *,
        texts: list[str],
        labels: list[str],
        symptom_bank: dict[str, list[str]],
    ) -> dict[str, object]:
        class_counts = Counter(labels)
        fold_count = max(2, min(self.CROSS_VALIDATION_FOLDS, min(class_counts.values())))
        cv = StratifiedKFold(n_splits=fold_count, shuffle=True, random_state=42)
        evaluation_pipeline = Pipeline(
            steps=[
                (
                    "tfidf",
                    TfidfVectorizer(
                        lowercase=True,
                        ngram_range=(1, 2),
                        min_df=1,
                    ),
                ),
                (
                    "classifier",
                    LogisticRegression(
                        max_iter=1000,
                        random_state=42,
                    ),
                ),
            ]
        )
        accuracy_scores = cross_val_score(evaluation_pipeline, texts, labels, cv=cv, scoring="accuracy")
        macro_f1_scores = cross_val_score(evaluation_pipeline, texts, labels, cv=cv, scoring="f1_macro")
        predicted_labels = cross_val_predict(evaluation_pipeline, texts, labels, cv=cv)
        precision, recall, f1, _ = precision_recall_fscore_support(
            labels,
            predicted_labels,
            labels=sorted(class_counts.keys()),
            zero_division=0,
        )

        single_symptom_texts: list[str] = []
        single_symptom_labels: list[str] = []
        for disease, symptoms in symptom_bank.items():
            for symptom in symptoms:
                single_symptom_texts.append(symptom)
                single_symptom_labels.append(disease)

        single_symptom_predictions = self._pipeline.predict(single_symptom_texts)
        per_class_metrics = []
        for index, disease in enumerate(sorted(class_counts.keys())):
            per_class_metrics.append(
                {
                    "disease": disease,
                    "display_name": self._display_name_for(disease),
                    "precision_percent": round(float(precision[index]) * 100, 2),
                    "recall_percent": round(float(recall[index]) * 100, 2),
                    "f1_percent": round(float(f1[index]) * 100, 2),
                    "training_samples": class_counts[disease],
                }
            )

        return {
            "cross_validation": {
                "folds": fold_count,
                "accuracy_percent": round(float(mean(accuracy_scores)) * 100, 2),
                "macro_f1_percent": round(float(mean(macro_f1_scores)) * 100, 2),
                "accuracy_by_fold_percent": [round(float(score) * 100, 2) for score in accuracy_scores],
            },
            "single_symptom_check": {
                "accuracy_percent": round(float(accuracy_score(single_symptom_labels, single_symptom_predictions)) * 100, 2),
                "macro_f1_percent": round(float(f1_score(single_symptom_labels, single_symptom_predictions, average="macro")) * 100, 2),
                "samples_evaluated": len(single_symptom_labels),
            },
            "per_class_metrics": per_class_metrics,
            "confidence_policy": {
                "high_confidence_threshold_percent": self.HIGH_CONFIDENCE_THRESHOLD,
                "minimum_confidence_threshold_percent": self.MINIMUM_CONFIDENCE_THRESHOLD,
                "uncertain_margin_threshold_percent": self.UNCERTAIN_MARGIN_THRESHOLD,
            },
        }

    def _build_model_performance_summary(self) -> dict[str, object]:
        evaluation = (self._metadata or {}).get("evaluation") or {}
        cross_validation = evaluation.get("cross_validation") or {}
        single_symptom_check = evaluation.get("single_symptom_check") or {}
        return {
            "cross_validation_accuracy_percent": cross_validation.get("accuracy_percent"),
            "cross_validation_macro_f1_percent": cross_validation.get("macro_f1_percent"),
            "single_symptom_accuracy_percent": single_symptom_check.get("accuracy_percent"),
        }

    def _build_prediction_quality(
        self,
        confidence_percent: float,
        *,
        confidence_margin_percent: float,
    ) -> dict[str, object]:
        is_uncertain = self._is_prediction_uncertain(confidence_percent, confidence_margin_percent)

        if is_uncertain and confidence_percent < self.MINIMUM_CONFIDENCE_THRESHOLD:
            band = "low"
            message = "Model confidence is low, so more symptom detail is needed before suggesting a likely match."
        elif is_uncertain:
            band = "medium"
            message = "Top matches are too close together, so the result is still uncertain."
        elif confidence_percent >= self.HIGH_CONFIDENCE_THRESHOLD:
            band = "high"
            message = "Model confidence is high for this match, but doctor review is still recommended."
        else:
            band = "medium"
            message = "Model confidence is moderate, so this result should be reviewed carefully."

        return {
            "confidence_percent": round(float(confidence_percent), 2),
            "confidence_margin_percent": round(float(confidence_margin_percent), 2),
            "confidence_band": band,
            "is_uncertain": is_uncertain,
            "needs_clinical_review": True,
            "message": message,
        }

    def _is_prediction_uncertain(self, confidence_percent: float, confidence_margin_percent: float) -> bool:
        return (
            float(confidence_percent) < self.MINIMUM_CONFIDENCE_THRESHOLD
            or float(confidence_margin_percent) < self.UNCERTAIN_MARGIN_THRESHOLD
        )

    def _apply_rule_based_adjustments(
        self,
        *,
        probabilities: Iterable[float],
        symptoms: list[str],
    ) -> tuple[list[float], list[str], list[dict[str, object]]]:
        adjusted = [float(value) for value in probabilities]
        canonical_symptoms = self._canonicalize_symptoms_for_rules(symptoms)
        symptom_set = set(canonical_symptoms)
        class_index = {
            disease: index
            for index, disease in enumerate(self._pipeline.classes_)
        }
        triggered_rule_signals: list[dict[str, object]] = []

        for disease, rules in self.DISEASE_RULE_BOOSTS.items():
            disease_index = class_index.get(disease)
            if disease_index is None:
                continue

            multiplier = 1.0
            matched_rules: list[str] = []
            for rule in rules:
                if self._rule_matches_symptoms(symptom_set, rule):
                    multiplier *= float(rule["multiplier"])
                    matched_rules.append(str(rule["name"]))

            if multiplier > 1.0:
                adjusted[disease_index] *= multiplier
                triggered_rule_signals.append(
                    {
                        "disease": disease,
                        "display_name": self._display_name_for(disease),
                        "matched_rules": matched_rules,
                        "multiplier": round(multiplier, 3),
                    }
                )

        total_probability = sum(adjusted)
        if total_probability > 0:
            adjusted = [value / total_probability for value in adjusted]

        return adjusted, canonical_symptoms, triggered_rule_signals

    def _canonicalize_symptoms_for_rules(self, symptoms: Iterable[str]) -> list[str]:
        canonicalized: list[str] = []
        for symptom in symptoms:
            cleaned_symptom = self._clean_text(symptom)
            if not cleaned_symptom:
                continue

            matched = self._match_fragment_to_known_symptom(cleaned_symptom)
            canonicalized.append((matched or cleaned_symptom).lower())

        return self._dedupe_preserve_order(canonicalized)

    def _rule_matches_symptoms(self, symptom_set: set[str], rule: dict[str, object]) -> bool:
        required_all = {str(item).lower() for item in rule.get("all_of", ())}
        if required_all and not required_all.issubset(symptom_set):
            return False

        grouped_options = rule.get("group_any_of", ()) or ()
        for group in grouped_options:
            normalized_group = {str(item).lower() for item in group}
            if normalized_group and not symptom_set.intersection(normalized_group):
                return False

        return True

    def _build_symptom_lookup(self, symptom_bank: dict[str, list[str]]) -> list[tuple[str, str]]:
        lookup: dict[str, str] = {}

        for symptoms in symptom_bank.values():
            for symptom in symptoms:
                cleaned = self._clean_text(symptom)
                normalized = self._normalize_for_matching(cleaned)
                if normalized:
                    lookup.setdefault(normalized, cleaned)

        for canonical, aliases in self.COMMON_SYMPTOM_ALIASES.items():
            normalized_canonical = self._normalize_for_matching(canonical)
            if normalized_canonical:
                lookup.setdefault(normalized_canonical, canonical)

            for alias in aliases:
                normalized_alias = self._normalize_for_matching(alias)
                if normalized_alias:
                    lookup[normalized_alias] = canonical

        return sorted(lookup.items(), key=lambda item: (-len(item[0]), item[0]))

    def _extract_symptoms_from_message(self, message: str) -> list[str]:
        normalized_message = self._normalize_for_matching(message)
        padded_message = f" {normalized_message} "
        negated_symptoms = {item.lower() for item in self._extract_negated_symptoms_from_message(message)}
        matched: list[str] = []
        seen: set[str] = set()

        for normalized_term, canonical_symptom in self._symptom_lookup:
            if not normalized_term:
                continue

            if f" {normalized_term} " not in padded_message:
                continue

            if canonical_symptom.lower() in negated_symptoms:
                continue

            normalized_canonical = canonical_symptom.lower()
            if normalized_canonical in seen:
                continue

            seen.add(normalized_canonical)
            matched.append(canonical_symptom)

        fragments = [
            self._clean_text(fragment)
            for fragment in re.split(r"[\n,;/]+|\band\b|\baur\b|\bwith\b|\balso\b", message, flags=re.IGNORECASE)
        ]
        for fragment in fragments:
            if self._fragment_contains_negation(fragment):
                continue

            cleaned_fragment = self._clean_symptom_fragment(fragment)
            if not cleaned_fragment or not self._looks_like_symptom_value(cleaned_fragment):
                continue

            canonical_match = self._match_fragment_to_known_symptom(cleaned_fragment)
            if canonical_match:
                normalized_canonical = canonical_match.lower()
                if normalized_canonical not in seen and normalized_canonical not in negated_symptoms:
                    seen.add(normalized_canonical)
                    matched.append(canonical_match)
                continue

            if len(cleaned_fragment.split()) > 3:
                continue

            lowered_words = set(cleaned_fragment.lower().split())
            if lowered_words & self.FRAGMENT_STOPWORDS:
                continue

            normalized_fragment = cleaned_fragment.lower()
            if normalized_fragment in seen:
                continue

            seen.add(normalized_fragment)
            matched.append(cleaned_fragment)

        return matched[:12]

    def _build_assistant_response(
        self,
        prediction: dict[str, object],
        matched_symptoms: list[str],
        disease_details: dict[str, list[str]],
        response_language: str,
    ) -> str:
        top_predictions = prediction["top_predictions"]
        top_prediction = top_predictions[0]
        closest_known_match = prediction.get("closest_known_match") or top_prediction
        is_uncertain = bool(prediction.get("is_uncertain"))
        alternatives = [
            f'{item["display_name"]} ({item["confidence"]}%)'
            for item in top_predictions[1:3]
        ]
        alternative_text = ""
        if alternatives:
            alternative_text = f" Other close matches in the dataset are {', '.join(alternatives)}."

        care_text = ""
        if disease_details.get("care_guidance"):
            care_text = f" Dataset-based care highlights: {', '.join(disease_details['care_guidance'][:3])}."

        medicine_text = ""
        if disease_details.get("medicine_guidance"):
            medicine_text = f" Dataset treatment options include {', '.join(disease_details['medicine_guidance'][:3])}."

        if is_uncertain:
            if response_language == "hinglish":
                alternative_text_hinglish = ""
                if alternatives:
                    alternative_text_hinglish = f" Close dataset matches {', '.join(alternatives)} hain."
                return (
                    f"Aapke message se mujhe ye symptoms mile: {', '.join(matched_symptoms)}. "
                    f"Current dataset me sabse close match {closest_known_match['display_name']} dikh raha hai, "
                    f"lekin confidence abhi clear nahi hai ({top_prediction['confidence']}%)."
                    f"{alternative_text_hinglish} Thoda aur detail dijiye, jaise symptom kitne din se hai, "
                    f"bukhar kitna hai, aur koi severe sign to nahi hai."
                )

            return (
                f"Based on the symptoms I recognized from your message ({', '.join(matched_symptoms)}), "
                f"The closest dataset match right now is {closest_known_match['display_name']}, "
                f"but the result is still uncertain at {top_prediction['confidence']}% confidence."
                f"{alternative_text} Please share a bit more detail such as duration, fever severity, "
                f"and any warning signs before treating this as a likely match."
            )

        if response_language == "hinglish":
            alternative_text_hinglish = ""
            if alternatives:
                alternative_text_hinglish = f" Dataset ke hisaab se dusre close matches {', '.join(alternatives)} hain."

            care_text_hinglish = ""
            if disease_details.get("care_guidance"):
                care_text_hinglish = f" Dataset-based care highlights: {', '.join(disease_details['care_guidance'][:3])}."

            medicine_text_hinglish = ""
            if disease_details.get("medicine_guidance"):
                medicine_text_hinglish = f" Dataset treatment options: {', '.join(disease_details['medicine_guidance'][:3])}."

            confidence_note_hinglish = ""
            if float(top_prediction["confidence"]) < self.HIGH_CONFIDENCE_THRESHOLD:
                confidence_note_hinglish = " Is prediction ki confidence 100% nahi hai, isliye isse final diagnosis na samjhein."

            return (
                f"Aapke message se jo symptoms mujhe mile ({', '.join(matched_symptoms)}), "
                f"unke basis par current dataset me sabse close match {top_prediction['display_name']} hai "
                f"jiski confidence {top_prediction['confidence']}% hai."
                f"{alternative_text_hinglish}{care_text_hinglish}{medicine_text_hinglish}{confidence_note_hinglish} "
                f"Is result ko dataset-based suggestion samajhiye, final diagnosis ke liye doctor se consult kijiye."
            )

        confidence_note = ""
        if float(top_prediction["confidence"]) < self.HIGH_CONFIDENCE_THRESHOLD:
            confidence_note = " This prediction is not 100% certain, so it should not be treated as a final diagnosis."

        return (
            f"Based on the symptoms I recognized from your message ({', '.join(matched_symptoms)}), "
            f"the closest match in the current dataset is {top_prediction['display_name']} "
            f"with {top_prediction['confidence']}% confidence.{alternative_text}"
            f"{care_text}{medicine_text}{confidence_note} "
            f"Please treat this as a dataset-based suggestion only and consult a doctor for diagnosis."
        )

    def _build_follow_up_questions(
        self,
        predicted_display_name: str,
        response_language: str,
        closest_match_display_name: str = "",
        is_uncertain: bool = False,
    ) -> list[str]:
        if is_uncertain or predicted_display_name == "Uncertain":
            if response_language == "hinglish":
                return [
                    "Ye symptoms kitne din se ho rahe hain?",
                    (
                        f"Kya symptoms {closest_match_display_name} jaise lag rahe hain ya kuch aur bhi add hua hai?"
                        if closest_match_display_name
                        else "Kya bukhar, dard, ya weakness badh rahi hai?"
                    ),
                    "Kya koi warning sign hai jaise saans ki dikkat, dehydration, ya bahut tez dard?",
                ]

            return [
                "How many days have you had these symptoms?",
                (
                    f"Do these symptoms feel closer to {closest_match_display_name}, or has something else appeared too?"
                    if closest_match_display_name
                    else "Are the fever, pain, or weakness getting worse?"
                ),
                "Do you have any warning signs such as breathing trouble, dehydration, or severe pain?",
            ]

        if response_language == "hinglish":
            return [
                f"{predicted_display_name} se related ye symptoms aapko kitne time se ho rahe hain?",
                "Kya bukhar ya dard time ke saath badh raha hai?",
                "Kya aapko ulti, dehydration, saans ki dikkat, ya bahut zyada kamzori bhi ho rahi hai?",
            ]

        return [
            f"How long have you been feeling these symptoms linked to {predicted_display_name}?",
            "Is the fever or pain getting worse over time?",
            "Are you also having vomiting, dehydration, breathing trouble, or severe weakness?",
        ]

    def _build_note(self, response_language: str) -> str:
        if response_language == "hinglish":
            return "Ye answer aapke local symptom dataset se generate hua hai aur ye medical diagnosis nahi hai."
        return "This answer is generated from your local symptom dataset and is not a medical diagnosis."

    def _extract_symptoms_for_dataset(self, config: DatasetConfig) -> list[str]:
        file_path = self.datasets_dir / config.file_name
        if not file_path.exists():
            return []

        structured_rows = self._extract_structured_rows(file_path)
        text_blob_rows = self._extract_text_blob_rows(file_path)
        symptoms = self._dedupe_preserve_order(structured_rows + text_blob_rows)
        curated_whitelist = self.DISEASE_SYMPTOM_WHITELIST.get(config.disease)
        if curated_whitelist:
            curated = [symptom for symptom in symptoms if symptom in curated_whitelist]
            if curated:
                symptoms = curated
        return symptoms

    def _extract_dataset_details(
        self,
        config: DatasetConfig,
        symptoms: list[str],
    ) -> dict[str, list[str]]:
        file_path = self.datasets_dir / config.file_name
        details = {
            "reference_symptoms": symptoms[:10],
            "warning_signs": [],
            "care_guidance": [],
            "medicine_guidance": [],
        }
        if not file_path.exists():
            return details

        with file_path.open("r", encoding="utf-8-sig", newline="") as dataset_file:
            reader = csv.DictReader(dataset_file)
            for row in reader:
                section = row.get("Section", "") or ""
                field = row.get("Field", "") or ""
                value = self._clean_text(row.get("Value", "") or "")
                if not value:
                    continue

                if self._looks_like_warning_detail(section, field, value):
                    details["warning_signs"].append(value)
                if self._looks_like_medicine_detail(section, field, value):
                    details["medicine_guidance"].append(value)
                elif self._looks_like_care_detail(section, field, value):
                    details["care_guidance"].append(value)

                text_blob_details = self._extract_text_blob_details(value)
                for key, values in text_blob_details.items():
                    details[key].extend(values)

        return {
            key: self._clean_detail_items(values)[:10]
            for key, values in details.items()
        }

    def _build_dataset_knowledge(
        self,
        config: DatasetConfig,
    ) -> tuple[dict[str, list[str]], list[KnowledgeEntry]]:
        file_path = self.datasets_dir / config.file_name
        topic_map = {topic: [] for topic in self.KNOWLEDGE_TOPIC_HINTS}
        raw_questions: list[tuple[str, str]] = []
        if not file_path.exists():
            return topic_map, []

        with file_path.open("r", encoding="utf-8-sig", newline="") as dataset_file:
            reader = csv.DictReader(dataset_file)
            for row in reader:
                section = self._clean_text(row.get("Section", "") or "")
                field = self._clean_text(row.get("Field", "") or "")
                value = self._clean_text(row.get("Value", "") or "")
                topic = self._infer_knowledge_topic(section, field, value)

                for question_text in self._extract_question_candidates(section, field, value):
                    raw_questions.append((question_text, topic))

                if not topic or not value or self._looks_like_structured_blob(value):
                    continue

                if self._looks_like_question_text(value):
                    continue

                knowledge_snippet = self._format_knowledge_snippet(field, value)
                if knowledge_snippet:
                    topic_map.setdefault(topic, []).append(knowledge_snippet)

        cleaned_topic_map = {
            topic: self._clean_detail_items(values)[:8]
            for topic, values in topic_map.items()
        }

        entries: list[KnowledgeEntry] = []
        for question_text, topic in raw_questions:
            answer = self._compose_topic_answer(
                disease_display_name=config.display_name,
                disease_key=config.disease,
                topic=topic,
                topic_map=cleaned_topic_map,
            )
            if answer:
                entries.append(
                    KnowledgeEntry(
                        disease=config.disease,
                        display_name=config.display_name,
                        topic=topic,
                        question=question_text,
                        answer=answer,
                    )
                )

        return cleaned_topic_map, entries

    def _build_dataset_knowledge_chunks(
        self,
        config: DatasetConfig,
    ) -> tuple[list[DatasetKnowledgeChunk], int]:
        file_path = self.datasets_dir / config.file_name
        if not file_path.exists():
            return [], 0

        chunks: list[DatasetKnowledgeChunk] = []
        row_count = 0
        with file_path.open("r", encoding="utf-8-sig", newline="") as dataset_file:
            reader = csv.DictReader(dataset_file)
            for row in reader:
                row_count += 1
                section = self._clean_text(row.get("Section", "") or "")
                field = self._clean_text(row.get("Field", "") or "")
                value = self._clean_text(row.get("Value", "") or "")
                topic = self._infer_knowledge_topic(section, field, value)
                for chunk_text in self._extract_knowledge_chunk_texts(section, field, value):
                    chunks.append(
                        DatasetKnowledgeChunk(
                            disease=config.disease,
                            display_name=config.display_name,
                            section=section,
                            field=field,
                            topic=topic,
                            text=chunk_text,
                        )
                    )

        unique_chunks: list[DatasetKnowledgeChunk] = []
        seen_texts: set[tuple[str, str]] = set()
        for chunk in chunks:
            chunk_key = (chunk.disease, chunk.text.lower())
            if chunk_key in seen_texts:
                continue
            seen_texts.add(chunk_key)
            unique_chunks.append(chunk)
        return unique_chunks, row_count

    def _extract_structured_rows(self, file_path: Path) -> list[str]:
        symptoms: list[str] = []
        with file_path.open("r", encoding="utf-8-sig", newline="") as dataset_file:
            reader = csv.DictReader(dataset_file)
            for row in reader:
                section = row.get("Section", "")
                field = row.get("Field", "")
                value = row.get("Value", "")

                if self._looks_like_symptom_row(section, field, value):
                    symptoms.extend(self._extract_dataset_symptom_candidates(value))
        return symptoms

    def _extract_text_blob_rows(self, file_path: Path) -> list[str]:
        extracted: list[str] = []
        with file_path.open("r", encoding="utf-8-sig", newline="") as dataset_file:
            reader = csv.DictReader(dataset_file)
            for row in reader:
                value = row.get("Value", "") or ""
                if not value:
                    continue

                lowered_value = value.lower()
                if not any(block_key in lowered_value for block_key in self.TEXT_BLOCK_KEYS):
                    continue

                extracted.extend(self._extract_from_text_blob(value))
        return extracted

    def _extract_from_text_blob(self, text: str) -> list[str]:
        symptoms: list[str] = []

        for key in self.TEXT_BLOCK_KEYS:
            array_pattern = re.compile(
                rf'"{re.escape(key)}"\s*:\s*\[(.*?)\]',
                re.IGNORECASE | re.DOTALL,
            )
            for match in array_pattern.finditer(text):
                symptoms.extend(self.QUOTED_VALUE_PATTERN.findall(match.group(1)))

            object_pattern = re.compile(
                rf'"{re.escape(key)}"\s*:\s*\{{',
                re.IGNORECASE,
            )
            for match in object_pattern.finditer(text):
                start_index = match.end() - 1
                block = self._slice_balanced_block(text, start_index)
                if block:
                    symptoms.extend(self._extract_strings_from_arrays(block))

        cleaned: list[str] = []
        for item in symptoms:
            cleaned.extend(self._extract_dataset_symptom_candidates(item))
        return self._dedupe_preserve_order(cleaned)

    def _extract_text_blob_details(self, text: str) -> dict[str, list[str]]:
        extracted = {
            "warning_signs": [],
            "care_guidance": [],
            "medicine_guidance": [],
        }
        if not text or "{" not in text:
            return extracted

        for detail_key, blob_keys in self.DETAIL_TEXT_KEYS.items():
            for blob_key in blob_keys:
                array_pattern = re.compile(
                    rf'"{re.escape(blob_key)}"\s*:\s*\[(.*?)\]',
                    re.IGNORECASE | re.DOTALL,
                )
                for match in array_pattern.finditer(text):
                    extracted[detail_key].extend(
                        self.QUOTED_VALUE_PATTERN.findall(match.group(1))
                    )

                object_pattern = re.compile(
                    rf'"{re.escape(blob_key)}"\s*:\s*\{{',
                    re.IGNORECASE,
                )
                for match in object_pattern.finditer(text):
                    start_index = match.end() - 1
                    block = self._slice_balanced_block(text, start_index)
                    if not block:
                        continue

                    parsed = self._parse_json_block(block)
                    if parsed is None:
                        continue

                    extracted[detail_key].extend(
                        self._extract_strings_from_structure(
                            parsed,
                            include_object_keys=detail_key == "medicine_guidance",
                        )
                    )

        return {
            key: [
                self._clean_text(item)
                for item in values
                if self._clean_text(item)
            ]
            for key, values in extracted.items()
        }

    def _extract_knowledge_chunk_texts(self, section: str, field: str, value: str) -> list[str]:
        cleaned_value = self._clean_text(value)
        if not cleaned_value:
            return []

        chunks: list[str] = []
        formatted_row = self._compose_knowledge_chunk_text(section, field, cleaned_value)
        if formatted_row and not self._looks_like_structured_blob(cleaned_value):
            chunks.append(formatted_row)

        if self._looks_like_structured_blob(cleaned_value):
            for parsed_object in self._extract_json_objects_from_text(cleaned_value):
                chunks.extend(
                    self._flatten_structure_to_chunk_texts(
                        parsed_object,
                        prefix=[section, field],
                    )
                )

            if not chunks:
                for symptom in self._extract_from_text_blob(cleaned_value):
                    composed = self._compose_knowledge_chunk_text(section, field, symptom)
                    if composed:
                        chunks.append(composed)

                blob_details = self._extract_text_blob_details(cleaned_value)
                for detail_values in blob_details.values():
                    for detail in detail_values:
                        composed = self._compose_knowledge_chunk_text(section, field, detail)
                        if composed:
                            chunks.append(composed)

        return self._clean_detail_items(chunks)[:120]

    def _compose_knowledge_chunk_text(self, section: str, field: str, value: str) -> str:
        cleaned_value = self._clean_text(value)
        if not cleaned_value:
            return ""

        combined_key = self._normalize_for_matching(f"{section} {field}")
        if any(
            blocked_hint in combined_key
            for blocked_hint in ("chatbot", "intent", "faq", "question", "response template", "template")
        ):
            return ""

        parts: list[str] = []
        cleaned_section = self._clean_text(str(section).replace("_", " "))
        cleaned_field = self._clean_text(str(field).replace("_", " "))
        if cleaned_section:
            parts.append(cleaned_section)
        if cleaned_field and cleaned_field.lower() not in {"value", "content"}:
            parts.append(cleaned_field)
        parts.append(cleaned_value)
        return self._clean_text(": ".join(parts[:-1]) + (": " if len(parts) > 1 else "") + parts[-1])

    def _extract_json_objects_from_text(self, text: str) -> list[object]:
        parsed_objects: list[object] = []
        working_text = self._clean_text(text)
        if not working_text or "{" not in working_text:
            return parsed_objects

        start_index = 0
        while start_index < len(working_text):
            brace_index = working_text.find("{", start_index)
            if brace_index == -1:
                break

            block = self._slice_balanced_block(working_text, brace_index)
            if not block:
                break

            parsed = self._parse_json_block(block)
            if parsed is not None:
                parsed_objects.append(parsed)
            start_index = brace_index + len(block)

        return parsed_objects

    def _flatten_structure_to_chunk_texts(
        self,
        value: object,
        *,
        prefix: list[str],
    ) -> list[str]:
        chunks: list[str] = []

        if isinstance(value, dict):
            for key, item in value.items():
                cleaned_key = self._clean_text(str(key).replace("_", " "))
                next_prefix = prefix + ([cleaned_key] if cleaned_key else [])
                chunks.extend(self._flatten_structure_to_chunk_texts(item, prefix=next_prefix))
            return chunks

        if isinstance(value, list):
            scalar_values: list[str] = []
            for item in value:
                if isinstance(item, (str, int, float, bool)):
                    scalar_text = self._stringify_scalar_value(item)
                    if scalar_text:
                        scalar_values.append(scalar_text)
                else:
                    chunks.extend(self._flatten_structure_to_chunk_texts(item, prefix=prefix))

            if scalar_values:
                for scalar_text in scalar_values:
                    composed = self._compose_knowledge_chunk_text(" ".join(prefix[:-1]), prefix[-1] if prefix else "", scalar_text)
                    if composed:
                        chunks.append(composed)

                if 1 < len(scalar_values) <= 6:
                    joined_text = "; ".join(scalar_values)
                    composed = self._compose_knowledge_chunk_text(" ".join(prefix[:-1]), prefix[-1] if prefix else "", joined_text)
                    if composed:
                        chunks.append(composed)
            return chunks

        scalar_text = self._stringify_scalar_value(value)
        if scalar_text:
            composed = self._compose_knowledge_chunk_text(" ".join(prefix[:-1]), prefix[-1] if prefix else "", scalar_text)
            if composed:
                chunks.append(composed)
        return chunks

    def _stringify_scalar_value(self, value: object) -> str:
        if isinstance(value, bool):
            return "Yes" if value else "No"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, str):
            return self._clean_text(value.replace("_", " "))
        return ""

    def _build_training_samples(self, disease: str, symptoms: list[str]) -> list[str]:
        samples = list(symptoms)
        if symptoms:
            samples.append(", ".join(symptoms[: min(len(symptoms), 12)]))

        random_generator = random.Random(sum(ord(char) for char in disease))
        max_combo_count = min(18, len(symptoms) * 2)

        for sample_size in (2, 3, 4):
            if len(symptoms) < sample_size:
                continue

            for _ in range(max_combo_count):
                combo = random_generator.sample(symptoms, sample_size)
                samples.append(", ".join(combo))

        return self._dedupe_preserve_order(samples)

    def _looks_like_symptom_row(self, section: str, field: str, value: str) -> bool:
        text_key = f"{section} {field}".lower()
        if not any(hint in text_key for hint in self.INCLUDE_HINTS):
            return False

        if any(hint in text_key for hint in self.SYMPTOM_SECTION_EXCLUDE_HINTS):
            return False

        if any(hint in text_key for hint in self.EXCLUDE_HINTS):
            return False

        return self._looks_like_symptom_value(value)

    def _looks_like_symptom_value(self, value: str) -> bool:
        cleaned = self._clean_text(value).lower()
        if not cleaned:
            return False

        if cleaned in self.NOISE_VALUES:
            return False

        if len(cleaned) < 3:
            return False

        if re.fullmatch(r"[\d\W]+", cleaned):
            return False

        if re.fullmatch(r"[\d.]+", cleaned):
            return False

        if re.search(r"\b(?:mg|ml|cm|days?|weeks?|months?|years?|percent)\b", cleaned):
            return False

        if cleaned.startswith(("http", "www")):
            return False

        return any(character.isalpha() for character in cleaned)

    def _extract_dataset_symptom_candidates(self, value: str) -> list[str]:
        raw_value = self._clean_text(str(value or "").replace("_", " "))
        if not raw_value or not self._looks_like_symptom_value(raw_value):
            return []

        normalized_value = self._normalize_for_matching(raw_value)
        candidates: list[str] = []
        padded_value = f" {normalized_value} "
        for canonical, phrases in self.DATASET_CANONICAL_SYMPTOMS.items():
            for phrase in phrases:
                normalized_phrase = self._normalize_for_matching(phrase)
                if normalized_phrase and f" {normalized_phrase} " in padded_value:
                    candidates.append(canonical)
                    break

        if candidates:
            return self._dedupe_preserve_order(candidates)

        if self._is_dataset_noise_value(normalized_value):
            return []

        cleaned_value = re.sub(r"\([^)]*\)", "", raw_value)
        cleaned_value = re.sub(r"\s+", " ", cleaned_value).strip(" ,;:-")
        if not cleaned_value:
            return []

        normalized_cleaned = self._normalize_for_matching(cleaned_value)
        if self._is_dataset_noise_value(normalized_cleaned):
            return []

        if len(cleaned_value.split()) > 5:
            return []

        return [cleaned_value.lower()]

    def _is_dataset_noise_value(self, normalized_value: str) -> bool:
        if not normalized_value:
            return True

        if normalized_value.startswith(self.QUESTION_PREFIXES):
            return True

        if "?" in normalized_value:
            return True

        if any(hint in normalized_value for hint in self.NON_HUMAN_HINTS):
            return True

        if any(hint in normalized_value for hint in self.OUTCOME_OR_METADATA_HINTS):
            return True

        if re.search(r"\b\d+\b", normalized_value) and any(
            unit in normalized_value for unit in ("hours", "days", "weeks", "months", "years", "percent")
        ):
            return True

        return False

    def _looks_like_question_text(self, value: str) -> bool:
        cleaned = self._clean_text(value).lower()
        if not cleaned:
            return False
        if "?" in cleaned:
            return True
        return cleaned.startswith(self.QUESTION_PREFIXES)

    def _infer_knowledge_topic(self, section: str, field: str, value: str) -> str:
        searchable = self._normalize_for_matching(f"{section} {field} {value}")
        for topic, hints in self.KNOWLEDGE_TOPIC_HINTS.items():
            if any(hint in searchable for hint in hints):
                return topic
        return ""

    def _extract_question_candidates(self, section: str, field: str, value: str) -> list[str]:
        candidates: list[str] = []
        for candidate in (field, value):
            cleaned = self._clean_text(candidate)
            if self._looks_like_question_text(cleaned):
                candidates.append(cleaned)
        return self._dedupe_preserve_order(candidates)

    def _format_knowledge_snippet(self, field: str, value: str) -> str:
        cleaned_value = self._clean_text(value)
        if not cleaned_value:
            return ""
        if cleaned_value.lower() == "true":
            cleaned_value = "Yes"
        elif cleaned_value.lower() == "false":
            cleaned_value = "No"

        cleaned_field = self._clean_text(field.replace("_", " "))
        cleaned_field = re.sub(r"\s+\d+$", "", cleaned_field).strip()
        normalized_field = cleaned_field.lower()

        if not cleaned_field or normalized_field in {"value", "content", "question", "faq"}:
            return cleaned_value

        if normalized_field in {"name", "mode", "principle", "importance", "curability", "duration", "type", "goal"}:
            return f"{cleaned_field}: {cleaned_value}"

        if len(cleaned_field.split()) <= 4:
            return f"{cleaned_field}: {cleaned_value}"

        return cleaned_value

    def _compose_topic_answer(
        self,
        *,
        disease_display_name: str,
        disease_key: str,
        topic: str,
        topic_map: dict[str, list[str]],
    ) -> str:
        snippets = topic_map.get(topic) or []
        if not snippets:
            return ""

        intro_map = {
            "definition": f"{disease_display_name} ke baare me dataset yeh batata hai:",
            "cause": f"{disease_display_name} ke common causes ya source dataset me yeh milte hain:",
            "transmission": f"{disease_display_name} ke spread/transmission ke baare me dataset ke key points:",
            "risk": f"{disease_display_name} ke risk ya severity ke baare me dataset me yeh points hain:",
            "symptoms": f"{disease_display_name} ke symptoms ke baare me dataset ke main points:",
            "testing": f"{disease_display_name} ke testing/diagnosis ke liye dataset me yeh information hai:",
            "treatment": f"{disease_display_name} ke treatment ke liye dataset me yeh points hain:",
            "prevention": f"{disease_display_name} ki prevention ke liye dataset me yeh suggestions hain:",
        }
        intro = intro_map.get(topic, f"{disease_display_name} ke dataset-based points:")
        return f"{intro} {'; '.join(snippets[:4])}."

    def _detect_query_disease(self, query: str) -> str:
        normalized_query = self._normalize_for_matching(query)
        for alias, disease in self.DISEASE_QUERY_ALIASES.items():
            normalized_alias = self._normalize_for_matching(alias)
            if normalized_alias and f" {normalized_alias} " in f" {normalized_query} ":
                return disease
        return ""

    def _score_knowledge_match(self, query: str, entry: KnowledgeEntry) -> float:
        normalized_query = self._normalize_for_matching(query)
        normalized_question = self._normalize_for_matching(entry.question)
        similarity = SequenceMatcher(None, normalized_query, normalized_question).ratio()
        query_tokens = set(normalized_query.split())
        question_tokens = set(normalized_question.split())
        overlap = len(query_tokens & question_tokens)
        detected_disease = self._detect_query_disease(query)
        disease_alignment = 0.0
        if detected_disease:
            disease_alignment = 0.25 if detected_disease == entry.disease else -0.25
        return similarity + (overlap * 0.08) + disease_alignment

    def _answer_knowledge_query(
        self,
        *,
        query: str,
        response_language: str,
        submitted_context: list[str],
    ) -> dict[str, object] | None:
        best_entry: KnowledgeEntry | None = None
        best_score = 0.0
        for entry in self._knowledge_entries:
            score = self._score_knowledge_match(query, entry)
            if score > best_score:
                best_score = score
                best_entry = entry

        detected_disease = self._detect_query_disease(query)
        if detected_disease and best_entry is not None and best_entry.disease != detected_disease:
            best_entry = None
            best_score = 0.0
        inferred_topic = self._infer_knowledge_topic("", "", query)
        if (best_entry is None or best_score < 0.72) and detected_disease and inferred_topic:
            fallback_answer = self._compose_topic_answer(
                disease_display_name=self._display_name_for(detected_disease),
                disease_key=detected_disease,
                topic=inferred_topic,
                topic_map=self._knowledge_topics.get(detected_disease, {}),
            )
            if fallback_answer:
                best_entry = KnowledgeEntry(
                    disease=detected_disease,
                    display_name=self._display_name_for(detected_disease),
                    topic=inferred_topic,
                    question=query,
                    answer=fallback_answer,
                )
                best_score = 0.75

        if best_entry is None or best_score < 0.72:
            return self._answer_chunk_retrieval_query(
                query=query,
                response_language=response_language,
                submitted_context=submitted_context,
            )

        answer_text = best_entry.answer
        if response_language == "english":
            answer_text = self._build_english_knowledge_answer(best_entry)

        return {
            "message": self._clean_text(query),
            "matched_symptoms": [],
            "recognized_negated_symptoms": [],
            "prediction": {
                "predicted_disease": best_entry.disease,
                "predicted_display_name": best_entry.display_name,
                "confidence": round(min(best_score, 0.99) * 100, 2),
                "prediction_status": "knowledge_answer",
                "is_uncertain": False,
                "model": self.MODEL_NAME,
                "top_predictions": [],
                "triggered_rule_signals": [],
            },
            "detected_problem": best_entry.display_name,
            "response_language": response_language,
            "assistant_response": answer_text,
            "dataset_reference_symptoms": self._symptom_bank.get(best_entry.disease, [])[:6],
            "care_guidance": self._knowledge_topics.get(best_entry.disease, {}).get(best_entry.topic, [])[:6],
            "medicine_guidance": self._dataset_details.get(best_entry.disease, {}).get("medicine_guidance", [])[:6],
            "warning_signs": self._dataset_details.get(best_entry.disease, {}).get("warning_signs", [])[:6],
            "recommended_tests": [],
            "model_performance": self._build_model_performance_summary(),
            "prediction_quality": {
                "confidence_percent": round(min(best_score, 0.99) * 100, 2),
                "confidence_band": "knowledge",
                "is_uncertain": False,
                "needs_clinical_review": False,
                "message": "This answer was matched from the dataset knowledge base.",
            },
            "submitted_context": submitted_context,
            "follow_up_questions": self._build_knowledge_follow_up_questions(best_entry, response_language),
            "note": self._build_note(response_language),
            "interaction_mode": "knowledge",
            "knowledge_match": {
                "disease": best_entry.disease,
                "display_name": best_entry.display_name,
                "topic": best_entry.topic,
                "matched_question": best_entry.question,
                "score_percent": round(min(best_score, 0.99) * 100, 2),
            },
        }

    def _answer_chunk_retrieval_query(
        self,
        *,
        query: str,
        response_language: str,
        submitted_context: list[str],
    ) -> dict[str, object] | None:
        if not self._knowledge_chunks or self._knowledge_vectorizer is None or self._knowledge_matrix is None:
            return None

        query_vector = self._knowledge_vectorizer.transform([query])
        similarity_scores = cosine_similarity(query_vector, self._knowledge_matrix)[0]
        if not len(similarity_scores):
            return None

        detected_disease = self._detect_query_disease(query)
        inferred_topic = self._infer_knowledge_topic("", "", query)
        ranked_chunks: list[tuple[float, DatasetKnowledgeChunk]] = []
        for index, raw_score in enumerate(similarity_scores):
            adjusted_score = float(raw_score)
            chunk = self._knowledge_chunks[index]
            if detected_disease:
                adjusted_score += 0.12 if chunk.disease == detected_disease else -0.02
            if inferred_topic and chunk.topic == inferred_topic:
                adjusted_score += 0.05
            ranked_chunks.append((adjusted_score, chunk))

        ranked_chunks.sort(key=lambda item: item[0], reverse=True)
        relevant_chunks = [
            (score, chunk)
            for score, chunk in ranked_chunks[:8]
            if score >= 0.12 and chunk.text
        ]
        if not relevant_chunks:
            return None

        disease_scores: dict[str, float] = {}
        for score, chunk in relevant_chunks:
            disease_scores[chunk.disease] = disease_scores.get(chunk.disease, 0.0) + score

        primary_disease = detected_disease or max(disease_scores, key=disease_scores.get)
        selected_chunks = [
            (score, chunk)
            for score, chunk in relevant_chunks
            if chunk.disease == primary_disease
        ][:4]
        if not selected_chunks:
            selected_chunks = relevant_chunks[:4]

        top_chunk = selected_chunks[0][1]
        display_name = self._display_name_for(primary_disease)
        snippet_text = "; ".join(chunk.text for _, chunk in selected_chunks[:3])
        confidence_percent = round(min(99.0, max(60.0, selected_chunks[0][0] * 100 + 35.0)), 2)

        if response_language == "english":
            answer_text = f"Based on the {display_name} dataset, these relevant points were found: {snippet_text}."
            confidence_message = "This answer was matched from indexed dataset rows."
        else:
            answer_text = f"{display_name} ke dataset se mujhe ye relevant points mile: {snippet_text}."
            confidence_message = "Ye answer indexed dataset rows se match karke diya gaya hai."

        disease_details = self._dataset_details.get(primary_disease, {})
        return {
            "message": self._clean_text(query),
            "matched_symptoms": [],
            "recognized_negated_symptoms": [],
            "prediction": {
                "predicted_disease": primary_disease,
                "predicted_display_name": display_name,
                "confidence": confidence_percent,
                "prediction_status": "knowledge_answer",
                "is_uncertain": False,
                "model": self.MODEL_NAME,
                "top_predictions": [],
                "triggered_rule_signals": [],
            },
            "detected_problem": display_name,
            "response_language": response_language,
            "assistant_response": answer_text,
            "dataset_reference_symptoms": self._symptom_bank.get(primary_disease, [])[:6],
            "care_guidance": disease_details.get("care_guidance", [])[:6],
            "medicine_guidance": disease_details.get("medicine_guidance", [])[:6],
            "warning_signs": disease_details.get("warning_signs", [])[:6],
            "recommended_tests": [],
            "model_performance": self._build_model_performance_summary(),
            "prediction_quality": {
                "confidence_percent": confidence_percent,
                "confidence_band": "knowledge",
                "is_uncertain": False,
                "needs_clinical_review": False,
                "message": confidence_message,
            },
            "submitted_context": submitted_context,
            "follow_up_questions": self._build_knowledge_follow_up_questions(
                KnowledgeEntry(
                    disease=primary_disease,
                    display_name=display_name,
                    topic=top_chunk.topic or inferred_topic or "knowledge",
                    question=query,
                    answer=answer_text,
                ),
                response_language,
            ),
            "note": self._build_note(response_language),
            "interaction_mode": "knowledge",
            "knowledge_match": {
                "disease": primary_disease,
                "display_name": display_name,
                "topic": top_chunk.topic or inferred_topic or "knowledge",
                "matched_question": query,
                "score_percent": confidence_percent,
                "matched_chunks": [chunk.text for _, chunk in selected_chunks[:3]],
            },
        }

    def _build_english_knowledge_answer(self, entry: KnowledgeEntry) -> str:
        topic_map = {
            "definition": f"Based on the dataset, here is a quick overview of {entry.display_name}:",
            "cause": f"Based on the dataset, common causes or sources of {entry.display_name} include:",
            "transmission": f"Based on the dataset, key points about how {entry.display_name} spreads are:",
            "risk": f"Based on the dataset, key risk or severity points for {entry.display_name} are:",
            "symptoms": f"Based on the dataset, common symptom-related points for {entry.display_name} are:",
            "testing": f"Based on the dataset, testing or diagnosis information for {entry.display_name} includes:",
            "treatment": f"Based on the dataset, treatment information for {entry.display_name} includes:",
            "prevention": f"Based on the dataset, prevention guidance for {entry.display_name} includes:",
        }
        intro = topic_map.get(entry.topic, f"Based on the dataset, key points for {entry.display_name} are:")
        answer_body = entry.answer.split(":", 1)[-1].strip()
        return f"{intro} {answer_body}"

    def _build_knowledge_follow_up_questions(self, entry: KnowledgeEntry, response_language: str) -> list[str]:
        if response_language == "hinglish":
            return [
                f"Kya aap {entry.display_name} ke symptoms ke baare me bhi puchna chahte hain?",
                f"Kya aap {entry.display_name} ke tests ya treatment details aur dekhna chahte hain?",
                "Agar aapko apne symptoms batane hain to main symptom check bhi kar sakta hoon.",
            ]

        return [
            f"Do you also want to know the symptoms of {entry.display_name}?",
            f"Do you want more detail about tests or treatment for {entry.display_name}?",
            "If you want, I can also switch to symptom checking for your own case.",
        ]

    def _build_dataset_inventory(
        self,
        *,
        dataset_row_counts: dict[str, int],
        knowledge_chunk_counts: dict[str, int],
        training_sample_counts: dict[str, int],
    ) -> list[dict[str, object]]:
        configured_by_filename = {config.file_name: config for config in self.DATASETS}
        inventory: list[dict[str, object]] = []

        for file_path in sorted(self.datasets_dir.glob("*.csv")):
            config = configured_by_filename.get(file_path.name)
            row_count = self._count_csv_rows(file_path)
            disease_key = config.disease if config else ""
            inventory.append(
                {
                    "file_name": file_path.name,
                    "display_name": config.display_name if config else file_path.stem,
                    "configured_disease": disease_key or None,
                    "row_count": row_count,
                    "loaded_in_model": bool(config and disease_key in dataset_row_counts),
                    "training_sample_count": training_sample_counts.get(disease_key, 0),
                    "knowledge_chunk_count": knowledge_chunk_counts.get(disease_key, 0),
                    "status": (
                        "loaded"
                        if config and disease_key in dataset_row_counts
                        else "empty"
                        if row_count == 0
                        else "discovered_only"
                    ),
                }
            )

        return inventory

    def _count_csv_rows(self, file_path: Path) -> int:
        if not file_path.exists():
            return 0

        with file_path.open("r", encoding="utf-8-sig", newline="") as dataset_file:
            reader = csv.DictReader(dataset_file)
            return sum(1 for _ in reader)

    def _looks_like_warning_detail(self, section: str, field: str, value: str) -> bool:
        if self._looks_like_structured_blob(value):
            return False
        key = f"{section} {field}".lower()
        if not any(hint in key for hint in self.WARNING_HINTS):
            return False
        return self._looks_like_guidance_value(value)

    def _looks_like_care_detail(self, section: str, field: str, value: str) -> bool:
        if self._looks_like_structured_blob(value):
            return False
        key = f"{section} {field}".lower()
        if any(hint in key for hint in self.CARE_EXCLUDE_HINTS):
            return False
        if not any(hint in key for hint in self.CARE_HINTS):
            return False
        return self._looks_like_guidance_value(value)

    def _looks_like_medicine_detail(self, section: str, field: str, value: str) -> bool:
        if self._looks_like_structured_blob(value):
            return False
        key = f"{section} {field}".lower()
        if any(excluded in key for excluded in ("diagnosis", "resistance", "surveillance", "source", "metadata")):
            return False
        if any(hint in key for hint in self.MEDICINE_HINTS):
            return self._looks_like_guidance_value(value)
        return bool(self.MEDICATION_VALUE_PATTERN.search(value))

    def _looks_like_guidance_value(self, value: str) -> bool:
        cleaned = self._clean_text(value)
        if not cleaned:
            return False
        if self._looks_like_structured_blob(cleaned):
            return False
        if not any(character.isalpha() for character in cleaned):
            return False
        if len(cleaned) < 3:
            return False
        if len(cleaned.split()) > 14:
            return False
        return True

    def _looks_like_structured_blob(self, value: str) -> bool:
        cleaned = self._clean_text(value)
        if not cleaned:
            return False
        if cleaned.startswith(("{", "[")):
            return True
        if cleaned.count("{") >= 2 or cleaned.count("[") >= 2:
            return True
        return '"disease' in cleaned.lower() and "{" in cleaned

    def _clean_detail_items(self, values: Iterable[str]) -> list[str]:
        cleaned_items: list[str] = []
        for value in values:
            cleaned = self._clean_text(value)
            if not cleaned or self._looks_like_structured_blob(cleaned):
                continue
            if len(cleaned) > 120:
                continue
            if cleaned.count(":") > 2:
                continue
            if not any(character.isalpha() for character in cleaned):
                continue
            cleaned_items.append(cleaned)
        return self._dedupe_preserve_order(cleaned_items)

    def _parse_json_block(self, text: str) -> object | None:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    def _extract_strings_from_structure(
        self,
        value: object,
        include_object_keys: bool = False,
    ) -> list[str]:
        extracted: list[str] = []

        if isinstance(value, str):
            cleaned = self._clean_text(value.replace("_", " "))
            if self._looks_like_guidance_value(cleaned):
                extracted.append(cleaned)
            return extracted

        if isinstance(value, list):
            for item in value:
                extracted.extend(self._extract_strings_from_structure(item, include_object_keys))
            return extracted

        if isinstance(value, dict):
            for key, item in value.items():
                normalized_key = self._clean_text(str(key).replace("_", " "))
                if include_object_keys and self._looks_like_medicine_detail("", "", normalized_key):
                    extracted.append(normalized_key)
                extracted.extend(self._extract_strings_from_structure(item, include_object_keys))
        return extracted

    def _build_context_summary(
        self,
        response_language: str,
        log_date: object | None,
        food_type: str,
        water_intake_glasses: object | None,
        sleep_hours: object | None,
        sleep_quality: str,
        stress_level: str,
        energy_level: str,
    ) -> list[str]:
        summary: list[str] = []
        if log_date:
            summary.append(
                f"Check-in date: {log_date}" if response_language == "english"
                else f"Check-in date: {log_date}"
            )
        if food_type:
            food_labels = {
                "home": "Normal home food",
                "outside": "Outside food",
                "junk": "Junk / oily food",
            }
            value = food_labels.get(food_type, food_type)
            summary.append(
                f"Food pattern: {value}" if response_language == "english"
                else f"Khana pattern: {value}"
            )
        if water_intake_glasses not in (None, ""):
            summary.append(
                f"Water intake: {water_intake_glasses} glasses" if response_language == "english"
                else f"Pani intake: {water_intake_glasses} glasses"
            )
        if sleep_hours not in (None, ""):
            summary.append(
                f"Sleep: {sleep_hours} hours" if response_language == "english"
                else f"Neend: {sleep_hours} hours"
            )
        if sleep_quality:
            summary.append(
                f"Sleep quality: {sleep_quality.title()}" if response_language == "english"
                else f"Neend quality: {sleep_quality.title()}"
            )
        if stress_level:
            summary.append(
                f"Stress level: {stress_level.title()}" if response_language == "english"
                else f"Stress level: {stress_level.title()}"
            )
        if energy_level:
            summary.append(
                f"Energy level: {energy_level.title()}" if response_language == "english"
                else f"Energy level: {energy_level.title()}"
            )
        return summary

    def _slice_balanced_block(self, text: str, start_index: int) -> str:
        depth = 0
        for index in range(start_index, len(text)):
            character = text[index]
            if character == "{":
                depth += 1
            elif character == "}":
                depth -= 1
                if depth == 0:
                    return text[start_index : index + 1]
        return ""

    def _extract_strings_from_arrays(self, text: str) -> list[str]:
        values: list[str] = []
        for array_match in self.ARRAY_PATTERN.finditer(text):
            values.extend(self.QUOTED_VALUE_PATTERN.findall(array_match.group(1)))
        return values

    def _display_name_for(self, disease: str) -> str:
        for config in self.DATASETS:
            if config.disease == disease:
                return config.display_name
        return disease.replace("_", " ").title()

    def _dedupe_preserve_order(self, items: Iterable[str]) -> list[str]:
        deduped: list[str] = []
        seen: set[str] = set()
        for item in items:
            normalized = item.lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            deduped.append(item)
        return deduped

    def _normalize_for_matching(self, value: str) -> str:
        normalized = re.sub(r"[^a-z0-9]+", " ", str(value or "").lower())
        return re.sub(r"\s+", " ", normalized).strip()

    def _detect_response_language(self, *texts: str) -> str:
        combined = " ".join(self._clean_text(text) for text in texts if self._clean_text(text))
        if not combined:
            return "english"

        if self.HINDI_SCRIPT_PATTERN.search(combined):
            return "hinglish"

        normalized_words = set(self._normalize_for_matching(combined).split())
        hindi_hits = len(normalized_words & self.HINGLISH_MARKERS)
        english_hits = len(normalized_words & self.ENGLISH_MARKERS)

        if hindi_hits > 0 and hindi_hits >= english_hits:
            return "hinglish"
        return "english"

    def _extract_negated_symptoms_from_message(self, message: str) -> list[str]:
        normalized_message = self._normalize_for_matching(message)
        tokens = normalized_message.split()
        negated: list[str] = []
        seen: set[str] = set()

        for normalized_term, canonical_symptom in self._symptom_lookup:
            if not normalized_term:
                continue

            term_tokens = normalized_term.split()
            if not term_tokens:
                continue

            positions = self._find_token_sequence_positions(tokens, term_tokens)
            if not positions:
                continue

            if any(self._is_negated_occurrence(tokens, start, len(term_tokens)) for start in positions):
                normalized_canonical = canonical_symptom.lower()
                if normalized_canonical not in seen:
                    seen.add(normalized_canonical)
                    negated.append(canonical_symptom)

        return negated

    def _find_token_sequence_positions(self, tokens: list[str], term_tokens: list[str]) -> list[int]:
        positions: list[int] = []
        if not tokens or not term_tokens or len(term_tokens) > len(tokens):
            return positions

        last_start = len(tokens) - len(term_tokens) + 1
        for start in range(last_start):
            if tokens[start : start + len(term_tokens)] == term_tokens:
                positions.append(start)
        return positions

    def _is_negated_occurrence(self, tokens: list[str], start_index: int, term_length: int) -> bool:
        prefix_tokens = tokens[max(0, start_index - 2) : start_index]
        suffix_tokens = tokens[start_index + term_length : start_index + term_length + 2]
        return bool(self.NEGATION_MARKERS.intersection(prefix_tokens + suffix_tokens))

    def _fragment_contains_negation(self, fragment: str) -> bool:
        normalized_fragment = self._normalize_for_matching(fragment)
        if not normalized_fragment:
            return False
        return bool(self.NEGATION_MARKERS.intersection(normalized_fragment.split()))

    def _match_fragment_to_known_symptom(self, fragment: str) -> str | None:
        normalized_fragment = self._normalize_for_matching(fragment)
        if not normalized_fragment:
            return None

        for normalized_term, canonical_symptom in self._symptom_lookup:
            if normalized_term == normalized_fragment:
                return canonical_symptom

        best_match: str | None = None
        best_score = 0.0
        fragment_word_count = len(normalized_fragment.split())
        for normalized_term, canonical_symptom in self._symptom_lookup:
            if abs(len(normalized_term.split()) - fragment_word_count) > 1:
                continue
            if abs(len(normalized_term) - len(normalized_fragment)) > max(4, len(normalized_fragment) // 2):
                continue

            score = SequenceMatcher(None, normalized_fragment, normalized_term).ratio()
            if score > best_score:
                best_score = score
                best_match = canonical_symptom

        if best_score >= self.FUZZY_MATCH_THRESHOLD:
            return best_match
        return None

    def _clean_symptom_fragment(self, value: str) -> str:
        cleaned = self._clean_text(value)
        cleaned = re.sub(
            r"^(?:i have|i am having|i am|i feel|feeling|having|suffering from|mujhe|mujhko|mere ko|main|mai|bas|sirf|only)\s+",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(
            r"\s+(?:ho rahi hai|ho raha hai|ho rahe hain|lag rahi hai|lag raha hai|hai|hain)$",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        return self._clean_text(cleaned)

    def _clean_text(self, value: str) -> str:
        return re.sub(r"\s+", " ", str(value or "")).strip(" ,;")


disease_prediction_service = DiseasePredictionService()
