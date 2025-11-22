KB_ARTICLES = [
    # PASSWORD/ACCESS Articles
    {
        "kb_id": "KB-042",
        "title": "Password Reset Procedure",
        "category": "PASSWORD_ACCESS",
        "content": """
        1. Verify user identity via security questions
        2. Access Active Directory Users & Computers
        3. Right-click user account → Reset Password
        4. Set temporary password
        5. Check 'User must change password at next logon'
        6. Communicate temporary password securely
        """,
        "keywords": ["password", "reset", "login", "access", "locked"],
        "avg_resolution_time": "5-10 minutes",
        "success_rate": "98%"
    },
    {
        "kb_id": "KB-103",
        "title": "Account Lockout Resolution",
        "category": "PASSWORD_ACCESS",
        "content": """
        1. Open Active Directory Users & Computers
        2. Find user account
        3. Properties → Account tab
        4. Check 'Unlock account'
        5. Verify no security breach
        6. Document incident
        """,
        "keywords": ["locked", "account", "failed", "attempts", "unlock"],
        "avg_resolution_time": "3-5 minutes",
        "success_rate": "100%"
    },
    
    # SOFTWARE Articles
    {
        "kb_id": "KB-201",
        "title": "Microsoft Office Crash Troubleshooting",
        "category": "SOFTWARE_ISSUES",
        "content": """
        1. Start Office in Safe Mode (hold Ctrl while opening)
        2. Disable add-ins: File → Options → Add-ins
        3. Run Office Repair: Control Panel → Programs → Office → Change → Quick Repair
        4. If persists, try Online Repair
        5. Check for Windows Updates
        """,
        "keywords": ["crash", "office", "excel", "word", "frozen", "not responding"],
        "avg_resolution_time": "15-20 minutes",
        "success_rate": "85%"
    },
    
    # NETWORK Articles
    {
        "kb_id": "KB-301",
        "title": "WiFi Connection Troubleshooting",
        "category": "NETWORK_CONNECTIVITY",
        "content": """
        1. Forget and reconnect to network
        2. Run network troubleshooter
        3. Update network adapter drivers
        4. Reset TCP/IP: netsh int ip reset
        5. Check DHCP settings
        6. Verify with IT if MAC filtering is enabled
        """,
        "keywords": ["wifi", "wireless", "connection", "network", "internet"],
        "avg_resolution_time": "10-15 minutes",
        "success_rate": "90%"
    },
    
    # HARDWARE Articles
    {
        "kb_id": "KB-401",
        "title": "Printer Jam Resolution Guide",
        "category": "HARDWARE_PROBLEMS",
        "content": """
        1. Turn off printer
        2. Open all compartments
        3. Remove paper carefully (don't tear)
        4. Check for small pieces of paper
        5. Close all compartments
        6. Power on and test
        """,
        "keywords": ["printer", "jam", "paper", "stuck", "error"],
        "avg_resolution_time": "5-10 minutes",
        "success_rate": "95%"
    },
    
    # EMAIL Articles
    {
        "kb_id": "KB-501",
        "title": "Outlook Calendar Sync Issues",
        "category": "EMAIL_ISSUES",
        "content": """
        1. Check account settings on both devices
        2. Force sync: Send/Receive → Update Folder
        3. Clear Outlook cache
        4. Remove and re-add account on mobile
        5. Verify calendar permissions
        """,
        "keywords": ["calendar", "sync", "outlook", "mobile", "meeting", "invite"],
        "avg_resolution_time": "15-20 minutes",
        "success_rate": "80%"
    }
]
