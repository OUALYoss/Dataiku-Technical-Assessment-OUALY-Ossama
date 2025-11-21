CATEGORY_PATTERNS = {
    "PASSWORD_ACCESS": [
        "password", "login", "locked out", "can't access", "cannot access",
        "reset", "forgotten", "expired", "credentials", "authenticate",
        "sign in", "log in", "access denied"
    ],
    "SOFTWARE_ISSUES": [
        "crash", "error", "not working", "frozen", "slow", "bug",
        "update", "install", "uninstall", "corrupted", "glitch",
        "not responding", "hangs", "freezes"
    ],
    "NETWORK_CONNECTIVITY": [
        "wifi", "wi-fi", "internet", "connection", "vpn", "network",
        "offline", "disconnected", "timeout", "cannot connect",
        "no connection", "ethernet", "bandwidth"
    ],
    "HARDWARE_PROBLEMS": [
        "printer", "keyboard", "mouse", "monitor", "screen", "display",
        "computer", "device", "hardware", "speaker", "microphone",
        "camera", "webcam", "usb", "port"
    ],
    "EMAIL_ISSUES": [
        "email", "outlook", "gmail", "attachment", "calendar", "inbox",
        "meeting", "invite", "mail", "sent", "received", "sync",
        "distribution list", "mailbox"
    ]
}

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

def get_category_patterns():
    """Retourne tous les patterns de catégories"""
    return CATEGORY_PATTERNS

def get_priority_keywords():
    """Retourne les mots-clés de priorité"""
    return PRIORITY_KEYWORDS