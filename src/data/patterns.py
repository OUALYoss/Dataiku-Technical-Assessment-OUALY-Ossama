TICKET_CATEGORIES = {
    "PASSWORD_ACCESS": [
        "password", "login", "locked out", "can't access", "reset", "forgotten",
        "credentials", "authentication", "sign in", "unlock", "account locked",
        "2fa", "mfa", "two-factor", "authenticator", "verification code",
        "vpn password", "expired password", "new user", "provisioning"
    ],
    "SOFTWARE_ISSUES": [
        "crash", "error", "not working", "frozen", "slow", "update", "install",
        "office", "excel", "word", "outlook", "teams", "zoom", "slack",
        "application", "program", "software", "app", "hanging", "not responding",
        "corrupted", "missing", "disappeared", "won't open", "won't load",
        "adobe", "pdf", "browser", "chrome", "edge", "extension", "add-in"
    ],
    "NETWORK_CONNECTIVITY": [
        "wifi", "internet", "connection", "vpn", "network", "offline",
        "can't connect", "disconnected", "no internet", "slow network",
        "remote desktop", "rdp", "shared drive", "network drive", "file server",
        "dns", "ip address", "ethernet", "lan", "wireless", "access point",
        "bandwidth", "speed", "latency", "timeout", "cannot ping"
    ],
    "HARDWARE_PROBLEMS": [
        "printer", "keyboard", "mouse", "monitor", "computer", "device",
        "laptop", "screen", "display", "broken", "damaged", "physical",
        "battery", "power", "charging", "won't turn on", "overheating",
        "flickering", "dead pixel", "keys stuck", "cursor jumping",
        "paper jam", "hardware", "peripheral", "usb", "port", "cable"
    ],
    "EMAIL_ISSUES": [
        "email", "outlook", "gmail", "attachment", "calendar", "meeting",
        "cannot send", "cannot receive", "spam", "junk", "sync",
        "calendar invite", "meeting request", "mailbox", "distribution list",
        "email client", "inbox", "outbox", "delivery failed", "bounce back",
        "mail server", "exchange", "smtp", "imap", "pop3"
    ]
}

# ==================== PRIORITY KEYWORDS ====================
PRIORITY_KEYWORDS = {
    "CRITICAL": [
        "entire floor", "all users", "company wide", "production down",
        "cannot work at all", "business critical", "data loss", "security breach",
        "server down", "system down", "complete outage"
    ],
    "HIGH": [
        "urgent", "asap", "critical", "emergency", "immediately",
        "right now", "client meeting", "presentation", "ceo", "important meeting",
        "affecting multiple users", "department down", "deadline today",
        "customer facing", "revenue impacting", "time sensitive"
    ],
    "MEDIUM": [
        "soon", "today", "important", "recurring", "multiple times",
        "keeps happening", "missed", "several users", "department",
        "need this week", "affects productivity", "scheduled meeting",
        "team affected", "business hours"
    ],
    "LOW": [
        "when possible", "no rush", "minor", "occasional", "sometimes",
        "intermittent", "not urgent", "whenever", "low priority",
        "convenience", "nice to have", "enhancement", "suggestion",
        "cosmetic", "single user", "personal device"
    ]
}

# ==================== PRIORITY RULES BY CATEGORY ====================
PRIORITY_RULES = {
    "PASSWORD_ACCESS": {
        "base_priority": "MEDIUM",
        "escalate_if": [
            "locked out", "multiple attempts", "urgent", "client meeting",
            "cannot access email", "new employee", "2fa not working"
        ],
        "deescalate_if": [
            "password change", "voluntary reset", "no deadline"
        ],
        "response_time": {
            "CRITICAL": "15 minutes",
            "HIGH": "30 minutes",
            "MEDIUM": "2 hours",
            "LOW": "24 hours"
        }
    },
    "SOFTWARE_ISSUES": {
        "base_priority": "MEDIUM",
        "escalate_if": [
            "crash", "data loss", "cannot work", "critical application",
            "affecting meeting", "video call", "presentation"
        ],
        "deescalate_if": [
            "minor bug", "cosmetic", "workaround available", "non-critical app"
        ],
        "response_time": {
            "CRITICAL": "15 minutes",
            "HIGH": "1 hour",
            "MEDIUM": "4 hours",
            "LOW": "48 hours"
        }
    },
    "NETWORK_CONNECTIVITY": {
        "base_priority": "HIGH",
        "escalate_if": [
            "entire floor", "conference room", "no internet", "vpn down",
            "multiple users", "affecting business", "remote workers"
        ],
        "deescalate_if": [
            "single user", "wifi slow", "personal device", "alternative available"
        ],
        "response_time": {
            "CRITICAL": "10 minutes",
            "HIGH": "30 minutes",
            "MEDIUM": "2 hours",
            "LOW": "24 hours"
        }
    },
    "HARDWARE_PROBLEMS": {
        "base_priority": "LOW",
        "escalate_if": [
            "shared printer", "server", "multiple users", "won't turn on",
            "data loss risk", "production equipment", "business critical device"
        ],
        "deescalate_if": [
            "personal device", "mouse", "keyboard", "cosmetic damage",
            "replacement available"
        ],
        "response_time": {
            "CRITICAL": "30 minutes",
            "HIGH": "2 hours",
            "MEDIUM": "8 hours",
            "LOW": "3 days"
        }
    },
    "EMAIL_ISSUES": {
        "base_priority": "MEDIUM",
        "escalate_if": [
            "cannot send", "lost emails", "calendar down", "distribution list",
            "client communication", "time-sensitive", "multiple users"
        ],
        "deescalate_if": [
            "spam", "signature", "out of office", "single email", "cosmetic"
        ],
        "response_time": {
            "CRITICAL": "20 minutes",
            "HIGH": "1 hour",
            "MEDIUM": "4 hours",
            "LOW": "24 hours"
        }
    }
}

# ==================== TIME-BASED PRIORITY MULTIPLIERS ====================
TIME_BASED_FACTORS = {
    "business_hours": {
        "weekday_9to5": 1.0,
        "weekday_evening": 0.7,
        "weekend": 0.5,
        "night": 0.3
    },
    "urgency_keywords": {
        "in 30 minutes": 2.0,
        "in 1 hour": 1.8,
        "in 2 hours": 1.5,
        "today": 1.3,
        "this week": 1.0,
        "no rush": 0.5
    }
}

# ==================== USER IMPACT SCORING ====================
IMPACT_FACTORS = {
    "user_count": {
        "single_user": 1,
        "team": 3,
        "department": 5,
        "entire_floor": 8,
        "company_wide": 10
    },
    "business_impact": {
        "convenience": 1,
        "productivity": 3,
        "customer_facing": 6,
        "revenue": 8,
        "security": 10
    }
}

# ==================== COMMON SOLUTIONS MAPPING ====================
COMMON_SOLUTIONS = {
    "PASSWORD_ACCESS": [
        "Reset password via Active Directory",
        "Unlock account",
        "Verify security questions",
        "Set up 2FA",
        "Check account permissions"
    ],
    "SOFTWARE_ISSUES": [
        "Restart application in safe mode",
        "Clear cache and reinstall",
        "Update to latest version",
        "Disable problematic add-ins",
        "Run repair tool"
    ],
    "NETWORK_CONNECTIVITY": [
        "Restart router/modem",
        "Forget and reconnect to network",
        "Update network drivers",
        "Check firewall settings",
        "Verify VPN credentials"
    ],
    "HARDWARE_PROBLEMS": [
        "Replace faulty hardware",
        "Clean and test device",
        "Update drivers",
        "Check physical connections",
        "Run hardware diagnostics"
    ],
    "EMAIL_ISSUES": [
        "Clear Outlook cache",
        "Force calendar sync",
        "Check mailbox size",
        "Remove and re-add account",
        "Verify email server settings"
    ]
}