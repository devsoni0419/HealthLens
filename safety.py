EMERGENCY_KEYWORDS = [
    "chest pain", "heart attack", "stroke", "unconscious",
    "severe bleeding", "can't breathe", "breathless",
    "suicide", "overdose", "seizure", "fainted"
]

def check_emergency(text):
    text = text.lower()
    for word in EMERGENCY_KEYWORDS:
        if word in text:
            return True
    return False

def safety_wrapper(user_query, response):
    if check_emergency(user_query):
        return (
            "⚠️ This may be a medical emergency.\n"
            "Please seek immediate help or call emergency services.\n\n"
            + response
        )
    return response