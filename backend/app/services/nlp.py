"""
NLP service for extracting structured entities from clinical document text.

Uses spaCy's small English model (en_core_web_sm) as a free, general-purpose
baseline. It won't have the clinical vocabulary of a model like scispaCy, but
it reliably picks up dates, person/org names, and quantities/measurements,
which combined with keyword matching gives a usable first pass at structuring
a document. Swap in a clinical NER model here if you have GPU budget later.
"""
import re
import spacy

_nlp = None

# Lightweight keyword lists to flag clinically relevant terms that a generic
# NER model won't tag on its own. Extend these lists as needed.
CONDITION_KEYWORDS = [
    "diabetes", "hypertension", "asthma", "cancer", "anemia", "arthritis",
    "depression", "anxiety", "obesity", "covid-19", "pneumonia", "fracture",
    "infection", "migraine", "epilepsy", "stroke", "cardiac", "renal",
]

MEDICATION_PATTERN = re.compile(
    r"\b([A-Z][a-zA-Z]+)\s+(\d+(?:\.\d+)?)\s?(mg|mcg|ml|g|units?)\b"
)


def get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


def extract_entities(text: str) -> dict:
    if not text or not text.strip():
        return {"people": [], "dates": [], "organizations": [], "conditions": [], "medications": []}

    nlp = get_nlp()
    doc = nlp(text[:100_000])  # cap length for performance

    people = sorted({ent.text for ent in doc.ents if ent.label_ == "PERSON"})
    dates = sorted({ent.text for ent in doc.ents if ent.label_ == "DATE"})
    orgs = sorted({ent.text for ent in doc.ents if ent.label_ == "ORG"})

    text_lower = text.lower()
    conditions = sorted({kw for kw in CONDITION_KEYWORDS if kw in text_lower})

    medications = sorted({f"{m.group(1)} {m.group(2)}{m.group(3)}" for m in MEDICATION_PATTERN.finditer(text)})

    return {
        "people": people,
        "dates": dates,
        "organizations": orgs,
        "conditions": conditions,
        "medications": medications,
    }


def classify_document_type(text: str) -> str:
    """Very lightweight rule-based classifier. Replace with a fine-tuned
    classifier or a Gemini call for higher accuracy."""
    text_lower = text.lower()
    rules = [
        ("discharge_summary", ["discharge summary", "discharge diagnosis"]),
        ("lab_report", ["lab report", "laboratory results", "specimen", "reference range"]),
        ("prescription", ["rx", "prescription", "sig:", "dispense"]),
        ("radiology_report", ["radiology", "impression:", "x-ray", "mri", "ct scan"]),
        ("consultation_note", ["consultation", "chief complaint", "history of present illness"]),
    ]
    for doc_type, keywords in rules:
        if any(kw in text_lower for kw in keywords):
            return doc_type
    return "unknown"
