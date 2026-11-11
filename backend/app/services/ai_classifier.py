"""
app/services/ai_classifier.py
Rule-based AI category suggestion for complaint images/text
Village Complaint Redressal System - Vemavaram Village

NOTE: This is a keyword-based classifier.
      Replace with a real ML model (e.g. Google Vision API) for production.
"""

from typing import Optional

# Keyword → category mapping (order matters — more specific first)
CATEGORY_KEYWORDS = {
    "Road Issues": [
        "pothole", "road", "crack", "broken", "tar", "asphalt",
        "pavement", "path", "street damage", "bump", "uneven"
    ],
    "Streetlight Issues": [
        "light", "streetlight", "lamp", "dark", "pole", "bulb",
        "electric pole", "no light", "night", "broken light"
    ],
    "Water Supply Problems": [
        "water", "tap", "pipe", "supply", "drinking water", "leak",
        "no water", "muddy water", "contaminated", "overflow tap"
    ],
    "Drainage Problems": [
        "drain", "drainage", "blockage", "flood", "waterlog", "stagnant",
        "overflow", "sewer", "gutter", "nullah"
    ],
    "Garbage Collection Issues": [
        "garbage", "waste", "trash", "litter", "dump", "dustbin",
        "rubbish", "solid waste", "collection", "bin"
    ],
    "Sanitation Issues": [
        "toilet", "sanitation", "hygiene", "public toilet", "open defecation",
        "latrine", "smell", "stink", "filth", "cleanliness"
    ],
}


def classify_complaint(title: str = "", description: str = "") -> dict:
    """
    Suggest a complaint category, priority, and department based on title + description text.
    """
    text = f"{title} {description}".lower()
    
    # Priority Keywords
    priority = "Medium"
    if any(w in text for w in ["fire", "accident", "emergency", "danger", "critical", "blood"]):
        priority = "Critical"
    elif any(w in text for w in ["flood", "block", "no water", "broken", "severe", "days", "urgent"]):
        priority = "High"
    elif any(w in text for w in ["minor", "small", "paint", "dirty"]):
        priority = "Low"

    scores = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[category] = score

    # Default return
    result = {"category": None, "priority": priority, "department": "General Administration"}

    if scores:
        best_category = max(scores, key=scores.get)
        result["category"] = best_category
        
        # Determine department based on category
        dept_map = {
            "Road Issues": "Infrastructure",
            "Streetlight Issues": "Electrical",
            "Water Supply Problems": "Water & Sanitation",
            "Drainage Problems": "Water & Sanitation",
            "Garbage Collection Issues": "Waste Management",
            "Sanitation Issues": "Health & Sanitation"
        }
        result["department"] = dept_map.get(best_category, "General Administration")

    return result


def classify_image_description(image_labels: list) -> Optional[str]:
    """
    Classify based on Google Vision API labels (list of strings).
    Pass Vision API label descriptions here for ML-enhanced classification.
    Falls back to keyword matching on label text.
    """
    combined_text = " ".join(image_labels).lower()
    return classify_complaint(description=combined_text).get("category")
