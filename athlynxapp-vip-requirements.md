# 🦁 ATHLYNXAPP.VIP - Design & Feature Requirements
## Athlynx-AI-VIP-Start-Up-Launch-2026-#14 Phase 1

**Source**: https://athlynxapp.vip/
**Captured**: January 12, 2026

---

## BRANDING

- **Logo**: ATHLYNX with lion icon - "THE ATHLETE'S PLAYBOOK"
- **Colors**: 
  - Primary: Deep Navy Blue (#0A1628)
  - Accent: Cyan/Turquoise gradient (#00D4FF to #0099FF)
  - Secondary: Gold/Yellow for highlights
  - Text: White on dark backgrounds
- **Tagline**: "Dreams Do Come True 2026"
- **Parent Company**: Dozier Holdings Group

---

## HEADER SECTION

- Top bar: "THE FUTURE OF ATHLETE SUCCESS"
- Navigation:
  - ATHLYNX logo (left)
  - Parent Company: Dozier Holdings Group (center)
  - Founders button
  - Portal Login button
- Status bar: "LIVE PLATFORM • HIPAA-compliant • Protecting our precious cargo"
- Update notice: "SITE UPDATING LIVE DAILY"

---

## HERO SECTION

- Main card with ATHLYNX logo
- "THE LEGENDARY TRAINER" badge
- "The mastermind behind the champion."
- "Building champions, training winners, and creating empires."

---

## KEY SECTIONS

### 1. The Vision
- "DREAMS DO COME TRUE"
- "ATHLYNX: The Perfect Storm"
- VIP Code entry option

### 2. The Empire
- "PASSIVE INCOME EMPIRE"
- "12 Companies • Global Reach • Infinite Potential"

### 3. 10 Apps Grid
1. Portal
2. Messenger
3. Diamond Grind
4. Warriors Playbook
5. Transfer Portal
6. NIL Vault
7. AI Sales
8. Faith
9. AI Recruiter
10. AI Content

### 4. Media Gallery
- NIL Portal - Football
- Diamond Grind - Baseball
- Softmor AI
- DHG Empire
- NIL Portal - Youth
- ATHLYNX Introduction

### 5. Countdown Timer
- "LAUNCHING IN FEBRUARY 1, 2026"
- Days, Hours, Minutes, Seconds
- "FOUNDING MEMBER SPOTS LIMITED TO 10,000"

### 6. The Perfect Storm - Dynasty Section
- The Visionary Owner (Robert Kraft comparison)
- The System (Bill Belichick/Manus AI)
- The Underdog (Tom Brady comparison)

### 7. Mission & Vision
- Mission: Democratize athlete success
- Vision: Operating system for every athlete's career by 2030
- Executive Summary: $50B opportunity

### 8. VIP Waitlist Form
- Full Name
- Email
- Phone
- Role selector (Athlete, Parent, Coach, Brand)
- Sport selector (Baseball, Football, Basketball, Soccer, Track & Field, Volleyball)
- "CLAIM MY VIP SPOT" button

### 9. VIP Code Entry
- For existing VIP members
- Unlocks all 6 apps
- Features: Social Network, NIL Deals, Messaging, Analytics, Compliance

### 10. Voting Section
- Site A vs Site B comparison
- Social media voting integration

### 11. Community Feedback
- What do you LOVE?
- What could be BETTER?
- Email for updates
- Submit Feedback button

---

## PAGES

1. **/** - Home (main landing)
2. **/our-story** - Family/Founder story
3. **/founders** - Founders page
4. **/portal** - Portal login

---

## TECHNICAL REQUIREMENTS (Python + Julia Stack)

### FastAPI Backend Routes Needed:
- GET / - Home page (Jinja2 template)
- GET /our-story - Our Story page
- GET /founders - Founders page
- POST /api/waitlist/join - Join waitlist
- GET /api/waitlist/count - Get waitlist count
- POST /api/vip/verify - Verify VIP code
- POST /api/feedback - Submit feedback
- POST /api/vote - Submit vote (Site A vs B)
- GET /api/countdown - Get countdown data

### Database Tables:
- waitlist (existing)
- vip_codes
- feedback
- votes
- analytics_events

### Julia Monitoring:
- Real-time waitlist analytics
- Vote tracking
- Feedback analysis
- System health

---

## FOOTER

- © 2026 Dozier Holdings Group, LLC
- "MIC DROP. FOCKER OUT."

---

**Dreams Do Come True 2026! 🦁**
