
# Mots-clés pour la priorité
PRIORITY_KEYWORDS = {
    "HIGH": [
        "urgent", "asap", "critical", "emergency", "immediately",
        "right now", "client meeting", "presentation", "ceo", "important meeting",
        "production down", "all users affected", "company wide"
    ],
    "MEDIUM": [
        "soon", "today", "important", "recurring", "multiple times",
        "keeps happening", "missed", "several users", "department"
    ],
    "LOW": [
        "when possible", "no rush", "minor", "occasional", "sometimes",
        "intermittent", "not urgent", "whenever", "low priority"
    ]
}

# Règles de priorité par catégorie
PRIORITY_RULES = {
    "PASSWORD_ACCESS": {
        "base_priority": "MEDIUM",
        "escalate_if": ["locked out", "multiple attempts", "urgent"],
        "deescalate_if": ["password change", "new user"]
    },
    "SOFTWARE_ISSUES": {
        "base_priority": "MEDIUM", 
        "escalate_if": ["crash", "data loss", "cannot work"],
        "deescalate_if": ["minor bug", "cosmetic"]
    },
    "NETWORK_CONNECTIVITY": {
        "base_priority": "HIGH",
        "escalate_if": ["entire floor", "conference room", "no internet"],
        "deescalate_if": ["single user", "wifi slow"]
    },
    "HARDWARE_PROBLEMS": {
        "base_priority": "LOW",
        "escalate_if": ["shared printer", "server", "multiple users"],
        "deescalate_if": ["personal device", "mouse", "keyboard"]
    },
    "EMAIL_ISSUES": {
        "base_priority": "MEDIUM",
        "escalate_if": ["cannot send", "lost emails", "calendar down"],
        "deescalate_if": ["spam", "signature", "out of office"]
    }
}

