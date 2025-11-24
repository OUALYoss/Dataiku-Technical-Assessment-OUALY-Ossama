KB_ARTICLES = [
    # ==================== PASSWORD_ACCESS (5 articles) ====================
    {
        "kb_id": "KB-042",
        "title": "Password Reset Procedure",
        "category": "PASSWORD_ACCESS",
        "content": """
        Standard password reset procedure for user accounts:
        1. Verify user identity via security questions or alternate email
        2. Access Active Directory Users & Computers
        3. Navigate to the user's organizational unit
        4. Right-click user account → Reset Password
        5. Set temporary password (minimum 12 characters, must include uppercase, lowercase, number, special character)
        6. Check 'User must change password at next logon' box
        7. Communicate temporary password securely (never via email)
        8. Document the reset in ServiceNow with ticket number
        9. Follow up with user to confirm successful login
        Common issues: User typing password incorrectly, caps lock enabled, password doesn't meet complexity requirements
        """,
        "keywords": ["password", "reset", "login", "access", "locked", "credentials", "authentication"],
        "avg_resolution_time": "5-10 minutes",
        "success_rate": "98%",
        "related_articles": ["KB-103", "KB-156", "KB-089"]
    },
    {
        "kb_id": "KB-103",
        "title": "Account Lockout Resolution",
        "category": "PASSWORD_ACCESS",
        "content": """
        Procedure to unlock locked user accounts:
        1. Open Active Directory Users & Computers
        2. Find user account in appropriate OU
        3. Right-click → Properties → Account tab
        4. Check 'Unlock account' checkbox
        5. Verify no security breach by checking recent login attempts
        6. Review failed login locations and times
        7. If suspicious activity detected, escalate to security team
        8. Document incident in security log
        9. Educate user on password best practices
        Note: Accounts auto-lock after 3 failed attempts. Auto-unlock after 30 minutes if not manually unlocked.
        Prevention: Enable password manager, implement biometric authentication where possible
        """,
        "keywords": ["locked", "account", "failed", "attempts", "unlock", "lockout", "security"],
        "avg_resolution_time": "3-5 minutes",
        "success_rate": "100%",
        "related_articles": ["KB-042", "KB-089"]
    },
    {
        "kb_id": "KB-156",
        "title": "VPN Credential Management",
        "category": "PASSWORD_ACCESS",
        "content": """
        VPN authentication troubleshooting and credential reset:
        1. Verify VPN client is latest version (FortiClient 7.x)
        2. Check if user credentials match Active Directory
        3. For password reset: Use standard AD reset procedure
        4. For MFA issues: Verify token sync in Azure MFA portal
        5. Test connection from VPN server logs
        6. Common issues: Expired certificates, incorrect server address, firewall blocking
        7. Remote workers: Ensure home router allows VPN ports (UDP 500, 4500)
        8. If persists: Clear VPN cache and reinstall client
        Prevention: Set up automatic credential sync, enable certificate auto-renewal
        """,
        "keywords": ["vpn", "remote", "access", "credentials", "authentication", "fortinet", "mfa"],
        "avg_resolution_time": "10-15 minutes",
        "success_rate": "92%",
        "related_articles": ["KB-042", "KB-301"]
    },
    {
        "kb_id": "KB-089",
        "title": "Two-Factor Authentication Troubleshooting",
        "category": "PASSWORD_ACCESS",
        "content": """
        Resolving 2FA/MFA issues:
        1. Verify user's phone number in Azure AD
        2. Check if user has backup authentication methods configured
        3. For SMS issues: Test with alternate phone number
        4. For authenticator app: Resync time on device (Settings → Date & Time → Automatic)
        5. Generate backup codes for user
        6. If device lost: Remove old device from MFA settings and register new one
        7. Temporary bypass: Can be granted for 24 hours in emergency (requires manager approval)
        8. Document all MFA changes for security audit
        Common issues: Time drift on phone, app not updated, SIM card issues
        """,
        "keywords": ["2fa", "mfa", "authentication", "sms", "authenticator", "security", "verification"],
        "avg_resolution_time": "8-12 minutes",
        "success_rate": "95%",
        "related_articles": ["KB-042", "KB-156"]
    },
    {
        "kb_id": "KB-234",
        "title": "New User Account Provisioning",
        "category": "PASSWORD_ACCESS",
        "content": """
        Complete setup for new employee accounts:
        1. Receive request from HR with start date and department
        2. Create AD account using standard naming convention (firstname.lastname)
        3. Assign to appropriate security groups based on role
        4. Set up email account in Exchange Online
        5. Generate temporary password (must be complex)
        6. Configure access to shared drives based on department
        7. Set up VPN access if remote worker
        8. Create accounts in company systems (CRM, Slack, Zoom, etc.)
        9. Prepare welcome email with all credentials and getting started guide
        10. Schedule follow-up call for day 1 to ensure everything works
        Timeline: Complete 1 day before start date
        """,
        "keywords": ["new", "hire", "user", "account", "provisioning", "onboarding", "setup"],
        "avg_resolution_time": "30-45 minutes",
        "success_rate": "100%",
        "related_articles": ["KB-042", "KB-156"]
    },
    
    # ==================== SOFTWARE_ISSUES (6 articles) ====================
    {
        "kb_id": "KB-201",
        "title": "Microsoft Office Crash Troubleshooting",
        "category": "SOFTWARE_ISSUES",
        "content": """
        Comprehensive Office application crash resolution:
        1. Start Office application in Safe Mode (hold Ctrl while opening)
        2. If opens: Problem is likely add-in related
        3. Disable add-ins: File → Options → Add-ins → Manage COM Add-ins → Uncheck all
        4. Enable one by one to identify problematic add-in
        5. Run Office Repair: Control Panel → Programs → Microsoft Office → Change → Quick Repair
        6. If Quick Repair fails: Try Online Repair (requires internet, takes 20-30 min)
        7. Check for Windows Updates and install all available updates
        8. Clear Office cache: Delete contents of %localappdata%\\Microsoft\\Office\\16.0
        9. If specific file crashes: File may be corrupted, try opening on different computer
        10. Last resort: Uninstall Office completely, restart, reinstall fresh
        Prevention: Keep Office updated, limit third-party add-ins, regular restarts
        """,
        "keywords": ["crash", "office", "excel", "word", "powerpoint", "outlook", "frozen", "not responding", "hang"],
        "avg_resolution_time": "15-30 minutes",
        "success_rate": "85%",
        "related_articles": ["KB-207", "KB-501"]
    },
    {
        "kb_id": "KB-207",
        "title": "Outlook Performance Optimization",
        "category": "SOFTWARE_ISSUES",
        "content": """
        Resolving slow Outlook performance:
        1. Check mailbox size (should be under 10GB)
        2. Archive old emails: Create archive PST file for emails older than 1 year
        3. Compact OST file: File → Account Settings → Data Files → Settings → Compact Now
        4. Disable unnecessary add-ins (major cause of slowness)
        5. Turn off RSS feeds if not used
        6. Reduce synchronization: Sync only last 6 months instead of all time
        7. Disable hardware graphics acceleration: File → Options → Advanced → Display
        8. Clear Outlook cache: Delete OST file and let it rebuild (backup first!)
        9. Check for corrupt add-ins using SARA tool (Microsoft Support and Recovery Assistant)
        10. Consider switching to Outlook web if desktop continues to be slow
        Prevention: Regular archiving, disable auto-archive, keep attachments small
        """,
        "keywords": ["outlook", "slow", "performance", "lag", "freeze", "email", "optimization"],
        "avg_resolution_time": "20-25 minutes",
        "success_rate": "90%",
        "related_articles": ["KB-201", "KB-501", "KB-502"]
    },
    {
        "kb_id": "KB-315",
        "title": "Microsoft Teams Troubleshooting Guide",
        "category": "SOFTWARE_ISSUES",
        "content": """
        Comprehensive Teams issue resolution:
        1. Clear Teams cache: Close Teams → Delete %appdata%\\Microsoft\\Teams\\Cache → Restart
        2. For sync issues: Sign out and sign back in
        3. For video/audio: Test devices in Settings → Devices
        4. Update to latest version: Check for updates in Teams settings
        5. Network connectivity: Teams requires 1.5 Mbps for video calls
        6. Firewall: Ensure ports 3478-3481 UDP are open
        7. For message loading issues: Switch to Teams web to verify server-side issue
        8. Screen sharing not working: Update graphics drivers
        9. If all fails: Uninstall Teams, delete all cache folders, reinstall fresh
        10. Known issue: Background blur requires Windows 10 1903+ and compatible CPU
        Prevention: Keep Teams updated, close when not in use, limit background apps
        """,
        "keywords": ["teams", "video", "call", "meeting", "chat", "collaboration", "microsoft", "conference"],
        "avg_resolution_time": "10-20 minutes",
        "success_rate": "88%",
        "related_articles": ["KB-318", "KB-301"]
    },
    {
        "kb_id": "KB-318",
        "title": "Zoom Audio and Video Troubleshooting",
        "category": "SOFTWARE_ISSUES",
        "content": """
        Fixing Zoom audio/video issues:
        1. Check device permissions: System Settings → Privacy → Camera/Microphone → Allow Zoom
        2. Test audio: Join test meeting at zoom.us/test
        3. Select correct audio device: Click arrow next to mute button → Select device
        4. Update Zoom to latest version (critical for bug fixes)
        5. For echo: Use headphones, disable 'Original Sound'
        6. For robotic audio: Lower video quality, close bandwidth-heavy apps
        7. Camera not working: Close other apps using camera (Teams, Skype, etc.)
        8. Virtual background not working: Requires green screen or compatible hardware
        9. Check firewall: Zoom needs ports 8801-8810 TCP
        10. Last resort: Uninstall Zoom, remove config files, reinstall
        Prevention: Test before important meetings, keep Zoom updated, use wired internet for stability
        """,
        "keywords": ["zoom", "video", "audio", "microphone", "camera", "meeting", "conference", "call"],
        "avg_resolution_time": "8-15 minutes",
        "success_rate": "92%",
        "related_articles": ["KB-315", "KB-301"]
    },
    {
        "kb_id": "KB-412",
        "title": "Adobe Reader PDF Issues",
        "category": "SOFTWARE_ISSUES",
        "content": """
        Resolving PDF opening and display problems:
        1. Update Adobe Reader to latest version
        2. For blank PDFs: Disable Protected Mode (Edit → Preferences → Security → Uncheck Protected Mode)
        3. Repair Adobe installation: Help → Repair Adobe Reader Installation
        4. Set as default PDF reader: Right-click PDF → Open with → Choose default program
        5. For corrupted PDFs: Try opening in Chrome or Edge browser
        6. Clear Adobe cache: Delete files in %localappdata%\\Adobe\\Acrobat\\DC
        7. For printing issues: Update printer driver, print as image
        8. Can't fill forms: Enable JavaScript in preferences
        9. Alternative: Try PDF-XChange or Foxit Reader
        Prevention: Keep Reader updated, don't open suspicious PDFs, use browser for simple viewing
        """,
        "keywords": ["pdf", "adobe", "reader", "document", "file", "open", "view", "acrobat"],
        "avg_resolution_time": "10-15 minutes",
        "success_rate": "85%",
        "related_articles": ["KB-201"]
    },
    {
        "kb_id": "KB-523",
        "title": "Browser Issues and Extensions",
        "category": "SOFTWARE_ISSUES",
        "content": """
        Chrome/Edge browser troubleshooting:
        1. Clear cache and cookies: Settings → Privacy → Clear browsing data
        2. For slow browser: Disable unused extensions
        3. For crashes: Check for conflicting software (antivirus, VPN)
        4. Update to latest version: Help → About Chrome
        5. Reset browser settings: Settings → Advanced → Reset
        6. For extension issues: Try incognito mode (extensions disabled by default)
        7. Create new profile if current profile is corrupted
        8. Check for malware: Run Windows Defender scan
        9. For SSL errors: Check system date/time is correct
        10. For specific site issues: Clear site cookies, try different browser
        Prevention: Keep browser updated, only install trusted extensions, regular cleanup
        """,
        "keywords": ["browser", "chrome", "edge", "extension", "plugin", "website", "internet", "web"],
        "avg_resolution_time": "12-18 minutes",
        "success_rate": "90%",
        "related_articles": ["KB-301"]
    },
    
    # ==================== NETWORK_CONNECTIVITY (6 articles) ====================
    {
        "kb_id": "KB-301",
        "title": "WiFi Connection Troubleshooting",
        "category": "NETWORK_CONNECTIVITY",
        "content": """
        Complete WiFi connectivity issue resolution:
        1. Forget network and reconnect: Network settings → Forget network → Reconnect with password
        2. Run Windows network troubleshooter: Settings → Network → Troubleshoot
        3. Update network adapter drivers: Device Manager → Network adapters → Update driver
        4. Reset TCP/IP stack: Run as admin: netsh int ip reset
        5. Flush DNS cache: ipconfig /flushdns
        6. Reset Winsock: netsh winsock reset
        7. Check DHCP settings: Ensure 'Obtain IP automatically' is selected
        8. Verify with IT if MAC filtering is enabled on access point
        9. Try different frequency: Switch between 2.4GHz and 5GHz
        10. For conference rooms: Check if AP is online, verify SSID broadcasting
        11. Signal strength: -30 to -50 dBm excellent, -70+ poor (check with WiFi analyzer)
        12. Last resort: Uninstall network adapter driver and let Windows reinstall
        Prevention: Keep drivers updated, avoid interference from microwaves/Bluetooth, optimal AP placement
        """,
        "keywords": ["wifi", "wireless", "connection", "network", "internet", "access point", "ssid", "signal"],
        "avg_resolution_time": "10-20 minutes",
        "success_rate": "90%",
        "related_articles": ["KB-302", "KB-305", "KB-156"]
    },
    {
        "kb_id": "KB-302",
        "title": "VPN Connection Issues",
        "category": "NETWORK_CONNECTIVITY",
        "content": """
        Resolving VPN connectivity and stability problems:
        1. Verify internet connection works without VPN
        2. Check VPN credentials are current (not expired)
        3. Update VPN client to latest version
        4. Try different VPN protocol (OpenVPN, IPsec, L2TP)
        5. Disable firewall temporarily to test if it's blocking
        6. For disconnections: Check 'Reconnect on link failure' in settings
        7. Router settings: Enable VPN passthrough, forward ports 500, 4500 UDP
        8. For slow VPN: Try connecting to different server region
        9. Split tunneling: Only route necessary traffic through VPN
        10. Check VPN server status: Contact network team if server issues
        11. Clear VPN cache and logs, restart client
        Prevention: Use wired connection when possible, close bandwidth-heavy apps, regular client updates
        """,
        "keywords": ["vpn", "remote", "connection", "disconnect", "slow", "virtual private network", "tunnel"],
        "avg_resolution_time": "15-25 minutes",
        "success_rate": "85%",
        "related_articles": ["KB-301", "KB-156"]
    },
    {
        "kb_id": "KB-305",
        "title": "Network Drive Access Issues",
        "category": "NETWORK_CONNECTIVITY",
        "content": """
        Troubleshooting shared network drive access:
        1. Verify you have permission to access the share
        2. Check network connectivity: Can you ping the file server?
        3. Try accessing via IP address instead of name: \\\\192.168.1.10\\share
        4. Clear cached credentials: Control Panel → Credential Manager → Remove old credentials
        5. Reconnect network drive: net use Z: \\\\server\\share /persistent:yes
        6. Check DNS: Ensure server name resolves correctly
        7. For 'Network path not found': Check if server is online, verify firewall rules
        8. Enable SMB protocol if disabled: Windows Features → SMB 1.0/CIFS File Sharing
        9. Check disk space on server (might be full)
        10. Verify with network team that your IP isn't blocked
        Prevention: Map drives properly with persistent connections, document UNC paths, regular access testing
        """,
        "keywords": ["network drive", "shared", "folder", "file server", "unc path", "smb", "cifs", "access denied"],
        "avg_resolution_time": "12-18 minutes",
        "success_rate": "88%",
        "related_articles": ["KB-301", "KB-302"]
    },
    {
        "kb_id": "KB-308",
        "title": "Slow Network Performance Diagnosis",
        "category": "NETWORK_CONNECTIVITY",
        "content": """
        Identifying and resolving slow network issues:
        1. Run speed test: speedtest.net (compare with expected speeds)
        2. Check bandwidth usage: Task Manager → Performance → Network
        3. Identify bandwidth hogs: Resource Monitor → Network tab
        4. For WiFi: Use wired connection to compare speeds
        5. Check for ISP outages or throttling
        6. Router/modem restart: Power cycle for 60 seconds
        7. Check DNS: Try Google DNS (8.8.8.8) or Cloudflare (1.1.1.1)
        8. QoS settings: Prioritize business applications
        9. For whole floor: Check switch/router serving that floor
        10. Network congestion: Peak hours (9-11am, 1-3pm) may be slower
        11. Cable issues: Test with known good ethernet cables
        12. Escalate if affecting multiple users or departments
        Prevention: Regular network monitoring, bandwidth management, infrastructure upgrades
        """,
        "keywords": ["slow", "network", "internet", "speed", "bandwidth", "performance", "latency", "lag"],
        "avg_resolution_time": "20-30 minutes",
        "success_rate": "75%",
        "related_articles": ["KB-301", "KB-302"]
    },
    {
        "kb_id": "KB-311",
        "title": "Ethernet Port and Cable Issues",
        "category": "NETWORK_CONNECTIVITY",
        "content": """
        Diagnosing wired ethernet connection problems:
        1. Check if cable is properly seated in both ends
        2. Try different ethernet cable (test with known working cable)
        3. Test port with different device to isolate issue
        4. Check link lights on port (should have green light)
        5. Update network adapter driver
        6. Check Device Manager for adapter errors or warnings
        7. Test on different port if available
        8. Verify VLAN settings if applicable
        9. Check switch port status with network team
        10. For PoE devices: Verify switch port provides sufficient power
        11. Cable testing: Use cable tester to check for breaks
        Prevention: Use quality Cat6 cables, proper cable management, label ports, regular port testing
        """,
        "keywords": ["ethernet", "cable", "wired", "port", "network adapter", "lan", "connection"],
        "avg_resolution_time": "10-15 minutes",
        "success_rate": "92%",
        "related_articles": ["KB-301", "KB-305"]
    },
    {
        "kb_id": "KB-314",
        "title": "Remote Desktop Connection Troubleshooting",
        "category": "NETWORK_CONNECTIVITY",
        "content": """
        Resolving RDP connection issues:
        1. Verify target computer allows remote connections: System Properties → Remote → Allow
        2. Confirm user has remote desktop permissions
        3. Check computer is online: Can you ping it?
        4. Verify RDP port 3389 is open through firewall
        5. Use computer name or IP address to connect
        6. For VPN users: Ensure VPN is connected and stable
        7. Check if Remote Desktop service is running: services.msc → Remote Desktop Services
        8. Try alternative RDP client (Microsoft Remote Desktop app)
        9. Network timeout: Increase timeout in RDP settings
        10. For 'Certificate' errors: Accept certificate or add to trusted
        11. Check Group Policy: Remote Desktop may be disabled by policy
        Prevention: Keep target computer awake, document IP addresses, regular RDP testing
        """,
        "keywords": ["remote desktop", "rdp", "remote", "connection", "terminal services", "desktop sharing"],
        "avg_resolution_time": "15-20 minutes",
        "success_rate": "87%",
        "related_articles": ["KB-302", "KB-301", "KB-156"]
    },
    
    # ==================== HARDWARE_PROBLEMS (5 articles) ====================
    {
        "kb_id": "KB-401",
        "title": "Printer Jam Resolution Guide",
        "category": "HARDWARE_PROBLEMS",
        "content": """
        Complete printer paper jam resolution:
        1. Turn off printer and unplug from power
        2. Open all accessible compartments (front, back, top)
        3. Remove paper carefully without tearing (pull in direction of paper path)
        4. Check for small torn pieces of paper hiding in rollers
        5. Remove toner cartridge to check behind it
        6. Use flashlight to inspect all paper path areas
        7. Gently rotate rollers to ensure they move freely
        8. Close all compartments securely
        9. Plug in and power on printer
        10. Run a test print
        11. If error persists: Clear print queue, restart print spooler service
        12. For recurring jams: Check paper quality, adjust guides, clean rollers
        Prevention: Use correct paper type, don't overfill tray, keep printer clean, replace worn rollers
        """,
        "keywords": ["printer", "jam", "paper", "stuck", "error", "printing", "cartridge"],
        "avg_resolution_time": "5-15 minutes",
        "success_rate": "95%",
        "related_articles": ["KB-403", "KB-405"]
    },
    {
        "kb_id": "KB-403",
        "title": "Monitor Display Issues",
        "category": "HARDWARE_PROBLEMS",
        "content": """
        Troubleshooting monitor problems (flickering, no display, artifacts):
        1. Check all cable connections (power, video cable)
        2. Try different cable (HDMI, DisplayPort, DVI)
        3. Test monitor with different computer
        4. Test computer with different monitor
        5. Update graphics card drivers
        6. Adjust refresh rate: Display Settings → Advanced → Monitor → 60Hz
        7. For flickering: Remove electromagnetic interference sources
        8. Check monitor settings: Auto-adjust, factory reset
        9. For dead pixels: Try pixel fixing software
        10. For color issues: Calibrate display, check color profiles
        11. Loose cable connections often cause intermittent issues
        Prevention: Use quality cables, proper ventilation, regular cleaning, brightness not too high
        """,
        "keywords": ["monitor", "display", "screen", "flickering", "artifact", "dead pixel", "no signal"],
        "avg_resolution_time": "15-25 minutes",
        "success_rate": "82%",
        "related_articles": ["KB-408"]
    },
    {
        "kb_id": "KB-405",
        "title": "Keyboard and Mouse Problems",
        "category": "HARDWARE_PROBLEMS",
        "content": """
        Fixing keyboard and mouse issues:
        KEYBOARD:
        1. For stuck keys: Remove keycap, clean with compressed air
        2. For unresponsive keys: Test with on-screen keyboard to rule out hardware
        3. Try keyboard on different computer
        4. Update keyboard driver in Device Manager
        5. Check for liquid damage (if spilled, let dry completely for 48 hours)
        6. For wireless: Replace batteries, reconnect via Bluetooth
        7. Check keyboard layout settings (may have switched to different language)
        
        MOUSE:
        1. Clean optical sensor with dry cloth
        2. Try different USB port
        3. Update mouse driver
        4. Adjust pointer speed: Mouse settings → Pointer options
        5. For wireless: Replace batteries, reconnect dongle
        6. For erratic movement: Clean mousepad, test on different surface
        7. Disable touchpad if causing conflicts
        Prevention: Regular cleaning, gentle use, keep liquids away, quality peripherals
        """,
        "keywords": ["keyboard", "mouse", "keys", "typing", "cursor", "pointer", "input device", "peripheral"],
        "avg_resolution_time": "10-20 minutes",
        "success_rate": "90%",
        "related_articles": ["KB-408"]
    },
    {
        "kb_id": "KB-408",
        "title": "Laptop Power and Battery Issues",
        "category": "HARDWARE_PROBLEMS",
        "content": """
        Diagnosing and resolving laptop power problems:
        1. For won't power on: Hold power button 30 seconds, try power without battery
        2. Check AC adapter: Test with multimeter or try different adapter
        3. Inspect power jack for damage or loose connection
        4. Remove all peripherals and try powering on
        5. For battery not charging: Update battery driver, calibrate battery
        6. Check battery health: powercfg /batteryreport in command prompt
        7. Battery swelling: Immediate replacement required (safety hazard)
        8. BIOS update may fix some power issues
        9. For overheating shutdowns: Clean vents, replace thermal paste, elevate laptop
        10. Check power settings: Balanced or High Performance mode
        11. For recurring shutdowns: Check Windows Event Viewer for errors
        Prevention: Regular cleaning, use on hard surface, don't block vents, original AC adapter
        """,
        "keywords": ["laptop", "battery", "power", "charging", "shutdown", "overheat", "won't turn on"],
        "avg_resolution_time": "20-30 minutes",
        "success_rate": "80%",
        "related_articles": ["KB-411"]
    },
    {
        "kb_id": "KB-411",
        "title": "Hardware Diagnostic Tools and Tests",
        "category": "HARDWARE_PROBLEMS",
        "content": """
        Using built-in diagnostics to identify hardware issues:
        1. Windows Memory Diagnostic: Search 'memory diagnostic' → Restart and test
        2. Check Disk: chkdsk C: /f /r (checks for drive errors)
        3. HP/Dell Diagnostics: Press F12 at boot → Diagnostics
        4. CPU/GPU stress test: Prime95, FurMark (monitor temperatures)
        5. Hard drive health: CrystalDiskInfo (check SMART status)
        6. RAM test: MemTest86 (run overnight for thorough test)
        7. Monitor cables: Swap cables to identify bad cable
        8. Device Manager: Check for yellow exclamation marks
        9. Event Viewer: Look for hardware error events
        10. BIOS: Check hardware is detected correctly
        Common signs of failing hardware: BSODs, random restarts, artifacts, slow performance
        """,
        "keywords": ["diagnostic", "hardware test", "troubleshoot", "failing hardware", "bsod", "memory test"],
        "avg_resolution_time": "30-60 minutes",
        "success_rate": "85%",
        "related_articles": ["KB-403", "KB-405", "KB-408"]
    },
    
    # ==================== EMAIL_ISSUES (3 articles) ====================
    {
        "kb_id": "KB-501",
        "title": "Outlook Calendar Sync Issues",
        "category": "EMAIL_ISSUES",
        "content": """
        Resolving calendar synchronization problems:
        1. Check account settings on all devices match
        2. Force manual sync: Send/Receive → Update Folder
        3. Clear Outlook cache: Delete OST file (will rebuild automatically)
        4. Remove and re-add account on mobile device
        5. Verify calendar permissions: Right-click calendar → Properties → Permissions
        6. Check if calendar is shared: Sharing issues can prevent sync
        7. For Exchange: Verify with IT that account isn't in retention hold
        8. Enable calendar sync in mobile app settings
        9. Check for calendar sync conflicts in web Outlook
        10. Verify timezone settings match across all devices
        11. For recurring meeting issues: Delete and recreate series
        Prevention: Regular sync checks, don't exceed calendar item limit (5000 items), clean up old appointments
        """,
        "keywords": ["calendar", "sync", "outlook", "mobile", "meeting", "invite", "appointment", "scheduling"],
        "avg_resolution_time": "15-20 minutes",
        "success_rate": "80%",
        "related_articles": ["KB-207", "KB-502"]
    },
    {
        "kb_id": "KB-502",
        "title": "Email Delivery and Spam Issues",
        "category": "EMAIL_ISSUES",
        "content": """
        Troubleshooting email delivery and spam filtering:
        FOR INCOMING SPAM:
        1. Mark as spam: Right-click → Junk → Block Sender
        2. Create rules: Move emails from specific domains to junk
        3. Check Safe Senders list: Junk Email Options → Safe Senders
        4. Report phishing attempts to IT security team
        5. Never click links in suspicious emails
        
        FOR LEGITIMATE EMAILS IN SPAM:
        1. Mark as Not Junk: Right-click → Junk → Not Junk
        2. Add sender to Safe Senders: Right-click → Junk → Add sender
        3. Check Junk folder regularly
        4. Create inbox rule to prevent certain senders going to junk
        5. Ask sender to resend (may have been flagged due to content)
        
        FOR SENDING ISSUES:
        1. Check recipient address is correct
        2. Verify attachment size under limit (25MB usually)
        3. Check if recipient blocked your domain
        4. Review SPF/DKIM records with IT if consistent issues
        Prevention: Be cautious with unknown senders, regular training on phishing, whitelist important contacts
        """,
        "keywords": ["email", "spam", "junk", "delivery", "phishing", "blocked", "undelivered", "bounce"],
        "avg_resolution_time": "10-15 minutes",
        "success_rate": "90%",
        "related_articles": ["KB-503"]
    },
    {
        "kb_id": "KB-503",
        "title": "Email Attachment and Size Issues",
        "category": "EMAIL_ISSUES",
        "content": """
        Handling email attachment problems:
        FOR SENDING LARGE FILES:
        1. Maximum size: Most servers limit to 25-30MB
        2. Use OneDrive/SharePoint: Share link instead of attaching
        3. Compress files: ZIP files to reduce size
        4. Split large files: Use file splitter tool
        5. Use FTP or file transfer service for very large files
        6. Check with IT for organization's file sharing solution
        
        FOR ATTACHMENT ERRORS:
        1. 'File too large': Use cloud storage link
        2. 'File type blocked': Change extension or ZIP first
        3. Can't open attachment: Ensure recipient has appropriate software
        4. Attachment missing: Check if stuck in Outbox
        5. For corrupted attachments: Resend or use different format
        
        FOR RECEIVING:
        1. Large attachments may take time to download
        2. Check mailbox size limit (may be full)
        3. Save attachments locally to free mailbox space
        4. Archive emails with large attachments
        Prevention: Regular mailbox cleanup, use cloud storage, compress files, document file sharing procedures
        """,
        "keywords": ["attachment", "file", "size", "limit", "send", "receive", "blocked", "large file"],
        "avg_resolution_time": "10-15 minutes",
        "success_rate": "95%",
        "related_articles": ["KB-207", "KB-502"]
    }
]