# DUY TAN UNIVERSITY
## International School
### Capstone Project 1
### C1SE.07
# Project Proposal

**Version:** 4.1  
**Date:** September 17th, 2026  
**DrugTime**

**Submitted by:**  
Nguyen Quang Bao  
Nguyen Tan Duc  
Nguyen Van Nguyen  
Nguyen Ngoc Phuc  
Dang Ngo Ngoc Viet  

**Approved by:**  
B.Eng. Nguyen Trong Giap, Kaopiz Da Nang  

**Proposal Review Panel Representative:**  
Name ________________   Signature ______________   Date ______________  

**Capstone Project 1 - Mentor:**  
Name ________________   Signature ______________   Date ______________  

---

## PROJECT INFORMATION

| Category | Details |
| :--- | :--- |
| **Project acronym** | DrugTime |
| **Project Title** | Medication Reminder, Drug-Interaction Safety, and AI-Assisted Care Platform |
| **Start Date** | 10 Sep 2026 |
| **End Date** | 26 Dec 2026 |
| **Lead Institution** | International School, Duy Tan University |
| **Project Mentor** | B.Eng. Nguyen Trong Giap |
| **Scrum master / Project Leader** | Nguyen Ngoc Phuc |
| **Partner Organization** | Kaopiz Da Nang |
| **Project Web URL** | |

**Team members:**

| # | Name | Email | Tel |
| :--- | :--- | :--- | :--- |
| 1 | Nguyen Ngoc Phuc | phucnguyenngoc2005@gmail.com | 0943009865 |
| 2 | Nguyen Quang Bao | nguyenquangbao575@gmail.com | 0779598354 |
| 3 | Nguyen Tan Duc | nguyentanduc1445@gmail.com | 0899961445 |
| 4 | Nguyen Van Nguyen | nguyenvannguyen10@dtu.edu.vn | 0359796984 |
| 5 | Dang Ngo Ngoc Viet | vietdangg2005@gmail.com | 0904833187 |

---

## DOCUMENT APPROVALS

The following signatures are required for approval of this document.

| Name & Role | Signature | Date |
| :--- | :--- | :--- |
| **Nguyen Ngoc Phuc**<br>Student ID: 29219051745<br>Team Leader/Scrum Master | | |
| **Nguyen Quang Bao**<br>Student ID: 29211158850<br>Team Member | | |
| **Nguyen Tan Duc**<br>Student ID: 29211156669<br>Team Member | | |
| **Nguyen Van Nguyen**<br>Student ID: 29211364802<br>Team Member | | |
| **Dang Ngo Ngoc Viet**<br>Student ID: 29219064788<br>Team Member | | |

---

## REVISION HISTORY

| Version | Date | Comments | Author |
| :--- | :--- | :--- | :--- |
| 1.0 | September 10th, 2026 | Initial release, adapted from the DrugTime product specification | Team C1SE.07 |
| 2.0 | September 11th, 2026 | Update tech stack | Team C1SE.07 |
| 3.0 | September 12th, 2026 | Update application features and tech stack | Team C1SE.07 |
| 4.0 | September 14th, 2026 | Update project scope | Team C1SE.07 |
| 4.1 | September 14th, 2026 | Update project cost | Team C1SE.07 |

---

## TABLE OF CONTENTS

1. Project Title
2. Team Members
3. Supervisor(s)
4. Problem Statement
   - Business Need
5. Survey / Existing Solutions
6. Objectives and Scope
   - 6.1. Core Objective
   - 6.2. Phase 1 Scope (3-Month MVP for iOS & Android)
   - 6.3. Out of Scope for Phase 1 (Planned for Phase 2)
7. Key Features & Requirements
   - 7.1. Functional Requirements (FR)
   - 7.2. Non-Functional Requirements (NFR)
8. Constraints and Assumptions
   - 8.1. Constraints
   - 8.2. Economic / Budget
   - 8.3. Assumptions
9. Target Users / Stakeholders
10. Technology Stack
11. Methodology & Development Plan
    - 11.1. Development Methodology (Scrum)
    - 11.2. Tasks and Deliverables
    - 11.3. Development Schedule
12. System Architecture Overview
    - 12.1. Container / Component View
    - 12.2. Architecture Style
    - 12.3. Deployment View
    - 12.4. System Context Diagram
13. Potential Risks and Mitigation Strategies
14. Expected Outcomes / Deliverables
15. References

---

## 1. Project Title
DrugTime – Medication Reminder, Drug-Interaction Safety, and AI-Assisted Care Platform

## 2. Team Members

**Table 1: Team members’ information**

| Full Name | Student ID | Email | Role |
| :--- | :--- | :--- | :--- |
| Nguyen Ngoc Phuc | 29219051745 | phucnguyenngoc2005@gmail.com | Leader, Dev, QA |
| Nguyen Quang Bao | 29211158850 | Nguyenquangbao575@gmail.com | Dev, QA, DevOps |
| Nguyen Tan Duc | 29211156669 | nguyentanduc1445@gmail.com | Dev, QA, DevOps |
| Nguyen Van Nguyen | 29211364802 | Nguyenvannguyen10@dtu.edu.vn | BA, Dev, QA |
| Dang Ngo Ngoc Viet | 29219064788 | vietdangg2005@gmail.com | Dev, QA, DevOps |

## 3. Supervisor(s)
**Name:** B.Eng. Nguyen Trong Giap  
**Department/Company:** Kaopiz Da Nang  
**Email:** giapnt@kaopiz.com  

## 4. Problem Statement
A survey of 60 respondents in Da Nang found that 75% had forgotten to take a medication in the past week, while only 5% used a dedicated medication-reminder app. Most respondents took several medications prescribed by different doctors, with no single tool to reconcile schedules, check interactions specific to the Vietnamese drug catalogue, or involve a family caregiver in monitoring adherence.

**Business Need**
*   Patients on multi-drug regimens – especially elderly patients – frequently miss doses, and existing international apps do not reflect the Vietnamese drug formulary or interaction database.
*   Manual data entry of medications is error-prone; handwritten prescriptions are especially unreliable for OCR and are out of scope.
*   Patients and family members have not shared, real-time view of missed doses; caregivers often only find out after the fact.
*   Drug-drug and drug-food interaction information is scattered across paper references (“Dược thư Quốc gia Việt Nam”) and is not surfaced at the point where a patient needs it.
*   Independent and partner pharmacies have no digital channel to extend care beyond the point of sale, or to safely connect patients to a licensed pharmacist for follow-up questions.
*   Any platform that processes health data and cross-border transfers (e.g. OCR processed by a third-party cloud service) must comply with Vietnam's 2025 Personal Data Protection Law and Decree 356/2025/NĐ-CP, including purpose-separated consent, data retention limits, and impact assessments – requirements that existing consumer apps do not address for the Vietnamese market.

## 5. Survey / Existing Solutions

**Table 2: Comparison with existing medication-reminder apps**

| Capability | DrugTime | Medisafe | MyTherapy |
| :--- | :--- | :--- | :--- |
| Vietnamese drug-formulary matching (drugbank.vn / DAV) | X | | |
| Interaction database aligned to Vietnamese guidance (QĐ 5948/QĐ-BYT) | X | | |
| Multi-channel reminders (local + Zalo) | X | Push only | Push only |
| Voice-based dose confirmation | X | | |
| Partner-pharmacy QR medication entry | X | | |
| Verified-pharmacist connection | X | | Limited (partner programs) |
| Purpose-separated consent under VN PDPL 2025 | X | | |
| Family caregiver missed-dose alerts | X | X | X |

*(X = capability supported; blank = not supported)*

Medisafe and MyTherapy are the leading international medication-reminder apps, but neither is built around the Vietnamese drug catalogue or the QĐ 5948/QĐ-BYT interaction guidance, neither offers a QR-based entry path tied to a local partner-pharmacy network, and neither is designed around Vietnam's purpose-separated consent requirements. DrugTime is the only solution known to combine Vietnamese-formulary interaction checking, multi-channel reminders including Zalo, and a verified-pharmacist escalation path in one platform.

## 6. Objectives and Scope

### 6.1. Core Objective 
DrugTime aims to significantly reduce missed doses and bridge the gap left by international apps (e.g., Medisafe, MyTherapy) by providing localized, Vietnam-specific pharmacological safety checking.

### 6.2. Phase 1 Scope (3-Month MVP for iOS & Android):
*   **Core Medication Management:** Manual entry or blister-pack scanning (with mandatory manual verification), paired with alarm-style local notifications for dose confirmations, scheduled using the mobile framework’s built-in local-notification APIs
*   **Safety & Compliance:** Localized drug-drug and drug-food interaction warnings cross-referenced with the Vietnamese national drug catalogue (including medical disclaimers), alongside AI-driven dietary recommendations. Strict compliance with Vietnam's Law on Personal Data Protection (2025) and Decree 356/2025/NĐ-CP via purpose-separated user consent.
*   **User Accessibility:** A dedicated "Simple Mode" featuring a highly simplified, high-contrast UI.
*   **Caregiver & Admin Features:** Family account linking via QR or referral codes for real-time missed-dose alerts and adherence tracking, plus a basic Admin dashboard for catalogue management.
*   **Disease Coverage:** Data in Phase 1 only covers the following disease groups: chronic conditions such as Diabetes and Hypertension / Heart Disease, special conditions such as Pregnancy or Breastfeeding and other common conditions such as Fever, Flu, Sore Throat, Seasonal Allergies, and Conjunctivitis (Pink Eye).

### 6.3. Out of Scope for Phase 1 (Planned for Phase 2):
Advanced features such as OCR prescription scanning, partner-pharmacy integrations, Zalo OA reminders, voice-based confirmations, pharmacist consultations, refill/wearable alerts, and Premium subscriptions.

## 7. Key Features & Requirements
DrugTime addresses these needs with a mobile-first platform. The first three months (MVP, Phase 1) deliver ten core capabilities: 

### 7.1. Functional Requirements (FR)

**Table 3: Functional requirements**

| ID | Requirement / Feature Description |
| :--- | :--- |
| FR01 | User Registration/Login and purpose-separated consent for data processing. |
| FR02 | Add medication via manual input or on-device blister-pack scanning (requires manual confirmation). |
| FR03 | Schedule and deliver local (on-device) notification reminders for medication doses. |
| FR04 | Provide drug-drug and drug-food interaction warnings (with mandatory medical disclaimers). |
| FR05 | Generate suitable AI-based meal suggestions with explanations. |
| FR06 | Provide a high-contrast, minimal-UI "Simple Mode". |
| FR07 | Link family caregiver accounts via QR/referral codes to send real-time missed-dose alerts and basic adherence history. |
| FR08 | Admin catalog management: CRUD medication/interaction catalog, periodic synchronization from the Vietnamese Drug Regulatory Data Source |
| FR09 | Admin compliance operations: conduct DPIA, process data-deletion/consent-withdrawal requests, maintain a sensitive-data access log |
| FR10 | Family member extended access: multi-patient management and drug safety lookup for linked patients, scoped to explicit patient consent |

Consent is collected separately for each data-processing purpose and can be withdrawn at any time from account settings. Prescription-image OCR, partner-pharmacy QR/barcode entry, the Zalo OA reminder channel, voice-based dose confirmation, the "Ask a pharmacist" escalation, the partner-pharmacy promotions map and data sharing, refill reminders, wearable-device integration, a medication usage guide, and the Premium subscription are deferred to a Phase 2 extension after the MVP.

### 7.2. Non-Functional Requirements (NFR)

**Table 4: Non-functional requirements**

| ID | Type | Requirement / Feature Description |
| :--- | :--- | :--- |
| NFR01 | Security & Privacy | Interaction warnings must comply with Vietnam’s 2025 Personal Data Protection Law and Decree 356/2025/NĐ-CP through purpose-separated consent |
| NFR02 | Usability | A dedicated Simple Mode provides a simplified, high-contrast UI for low-tech-literacy users |
| NFR03 | Localization | Drug data and interaction checks are matched against the Vietnamese national drug catalogue and formulary (Duợc thư Quốc gia Việt Nam, QĐ 5948/QĐ-BYT) |
| NFR04 | Performance | Reminder notifications and dose-confirmation actions must be processed and delivered within 2 seconds under normal load |
| NFR05 | Availability | Core services (reminders, adherence tracking, drug lookup) must maintain at least 99% uptime |
| NFR06 | Auditability | Every access to a patient's sensitive health data by a Family Member or Admin must be logged with actor, timestamp, and data scope, and be reviewable by Admin |
| NFR07 | Modifiability | The system architecture must support adding new modules/features in Phase 2 (e.g., new disease groups, integrations) with minimal impact on existing components |

## 8. Constraints and Assumptions

### 8.1. Constraints

**Table 5. Project constraints**

| Constraint | Constraint Description | Guidelines for Acceptance |
| :--- | :--- | :--- |
| Legal and Regulatory | Personal-data processing must comply with Vietnam's Law on Personal Data Protection (2025) and Decree 356/2025/NĐ-CP. The platform does not provide medical advice or diagnosis; interaction warnings are automated look-ups only. | Purpose-separated consent, withdrawal, and deletion mechanisms are implemented; DPIA and cross-border-transfer assessment are completed before any sensitive-data flow or OCR flow is used in production. |
| Economic | The MVP is built on a near-zero budget using free or free-tier services, plus the Apple Developer Program (99 USD/year) now required for the in-scope iOS build. Zalo OA and the Premium tier are Phase 2 items with pricing and conversion-rate assumptions still unproven. | The Apple Developer Program renewal is budgeted from the outset; a willingness-to-pay survey for the Premium tier and a funding decision for Zalo OA are completed before those Phase 2 features are built out. |
| Environmental | The platform runs on Render's Web Service and Worker tiers rather than a distributed cluster. | No significant environmental impact is expected from the chosen hosting footprint. |
| Ethical | Patient health data (medication lists, adherence history, packaging photos) must be handled under purpose-separated consent; only the data needed for each stated purpose is collected. | Health data is encrypted at rest and access-controlled; the blister-pack scan is processed on-device for the MVP, so no packaging image leaves the device. Cloud-based OCR in Phase 2 will require separate, explicit consent that discloses the destination before any image is sent abroad. |
| Public health, safety, and welfare | Missed-dose reminders and interaction warnings directly affect patient safety; an incorrect or missed interaction warning could be a health risk. | Every interaction-warning screen carries a disclaimer directing the patient to consult a doctor or pharmacist; in-app escalation to a verified pharmacist is a Phase 2 feature. |
| Social and Global | Improves medication adherence and safety for elderly and chronic-disease patients, and gives independent pharmacies a digital channel to extend care. | Addresses a documented adherence gap (75% of surveyed patients missed a dose in the past week) for Vietnamese patients on multi-drug regimens. |
| Cultural | The system is designed for the Vietnamese pharmaceutical and healthcare context (Vietnamese drug catalogue, Zalo as a planned Phase 2 communication channel, Dược thư Quốc gia VN as the reference source). | Localization for Vietnamese language and the Vietnamese drug-formulary/interaction database is required throughout. |
| Sustainability | Human resources: 5 team members; ongoing operation after graduation would require continued catalogue synchronization and a small operations team. | Refers to sustainability of resources, i.e. continued maintenance and hand-off documentation. |

### 8.2. Economic / Budget

**Table 6. Cost per person/hour**

| Full Name | Role | Salary Rate (USD/hour) |
| :--- | :--- | :--- |
| Nguyen Ngoc Phuc | Team Leader / Scrum Master | 2 |
| Nguyen Quang Bao | Team Member | 2 |
| Nguyen Tan Duc | Team Member | 2 |
| Nguyen Van Nguyen | Team Member | 2 |
| Dang Ngo Ngoc Viet | Team Member | 2 |

**Table 7. Cost calculation basis**

| Description | Amount | Unit |
| :--- | :--- | :--- |
| Number of members | 5 | Person |
| Number of working hours per day | 5 | Hours |
| Number of working days (Monday to Friday, 10 Sep – 16 Dec 2026) | 70 | Days |
| Total working hours (5 x 5 x 70) | 1,750 | Hours |

**Table 8. Total cost estimation**

| No | Criteria | Quantity | Unit price (USD) | Total (USD) |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Working hours | 1,750 | 2 | 3,500 |
| 2 | AI tools | 3 × 3month | 22 | 198 |
| 3 | Contingency | 1 | 300 | 300 |
| | **Total** | | | **3,998** |

### 8.3. Assumptions:
*   Internet connection is required for drug interaction checks and meal suggestions; medication reminders can run offline once the schedule has been synced.
*   Mobile OS: Android (APK sideload) and iOS (TestFlight/Ad Hoc build/IPA sideload), both targeted in the MVP.
*   Web browsers for the admin/partner dashboard: Google Chrome, Microsoft Edge, Firefox.

## 9. Target Users / Stakeholders
DrugTime is designed primarily for elderly and chronic-disease patients in Vietnam who manage multiple concurrent medications (polypharmacy), together with the family members, pharmacies, and administrators who support them. The system’s stakeholders and their roles are:

**Patient:**
*   **Account & Consent Management**
    *   Register / Login
    *   Complete purpose-separated consent
    *   Manage health profile
    *   Withdraw consent / request data deletion
*   **Medication Management**
    *   Add medication (manual input)
    *   Scan blister pack
    *   Confirm medication
    *   Manage medication schedule
*   **Medication Reminder & Adherence**
    *   Receive reminder
    *   Confirm dose intake
    *   View adherence history
*   **Drug Safety Lookup**
    *   Look up medication information
    *   View drug–drug interaction warning
    *   View drug–food interaction warning
*   **Family Linking**
    *   Link family member
    *   Confirm data-sharing consent on linking
    *   Remove linked family member
    *   Revoke data-sharing permission
*   **AI Assistant**
    *   View AI meal suggestion with explanation
*   **Simple Mode**
    *   Switch to Simple Mode UI

**Family member:**
*   **Family Monitoring**
    *   Link to patient account
    *   Receive missed-dose alert
    *   View adherence history
    *   Manage multiple linked patients
*   **Drug Safety Lookup**
    *   Look up medication information of linked patient
    *   View drug–drug interaction warning of linked patient
    *   View drug–food interaction warning of linked patient
*   **AI Assistant**
    *   View AI meal suggestion with explanation for linked patient

**Partner pharmacy staff (Phase 2):**
*   Register and be approved by the Admin (valid pharmacy business licence).
*   Issue a standardized QR/barcode at the point of sale.
*   Post promotions on the in-app map. 
*   Receive anonymized foot-traffic data, only for patients who opted in. 

**Partner pharmacist (Phase 2):**
*   Register and be verified by the Admin (valid pharmacy practising certificate) before being granted access to the question queue.
*   Answer patient questions escalated from the “Ask a pharmacist” feature through a dedicated queue interface.

**Admin:**
*   **Catalog Management**
    *   Manage medication catalog
    *   Manage interaction catalog
    *   Synchronize catalog from external sources
*   **Compliance Oversight**
    *   Conduct DPIA for new sensitive-data flows
    *   Review PDPL 2025 / Decree 356 compliance
    *   Process data deletion / consent withdrawal requests
    *   View sensitive-data access log

## 10. Technology Stack
*   **Mobile app:** Flutter, native build for both Android and iOS. 
*   **Admin web dashboard:** React + Next.js, deployed on Vercel.
*   **Backend:** Python, FastAPI.
*   **Database and storage:** Supabase (PostgreSQL + pgvector + Storage).
*   **Background jobs:** RQ with Redis (e.g. scheduled reminders, catalogue synchronization).
*   **Blister-pack scan:** on-device text recognition (Google ML Kit) followed by fuzzy matching against the licensed drug-name database to resolve the recognized text to a catalogue entry, so no packaging image leaves the device. Cloud-based prescription-image OCR (Google Vision) is deferred to Phase 2.
*   **Secondary reminder channel:** Zalo OA API (paid) — deferred to Phase 2; the MVP uses on-device local notifications only.
*   **Voice dose confirmation:** on-device speech-to-text — deferred to Phase 2; the MVP uses button confirmation only.
*   **AI meal suggestion and drug-drug & drug-food interaction warning:** LLM-based meal suggestions plus drug-drug/drug-food interaction checks.
*   **Version control:** GitHub. 
*   **Team management:** Jira, Slack, Google Drive, Microsoft OneDrive.

## 11. Methodology & Development Plan

### 11.1. Development Methodology (Scrum)
Scrum is an iterative and incremental agile framework for managing software development. The implementation phase of this project is organized into six two-week sprints, as described in Table 8.
Each sprint begins with sprint planning, includes daily stand-up meetings, and ends with a sprint review and a sprint retrospective.
Decision-making authority on implementation detail is delegated to the two development tracks, while scope changes are agreed with the mentor at each sprint review.
The framework was selected for the following reasons:
*   The project can respond easily to requirement changes as the DrugTime product specification is refined.
*   Integration problems between the mobile app, backend, and external services are identified early.
*   The most valuable and legally sensitive features (consent, reminders, interaction warnings) are delivered first.
*   The delivered increment better matches the needs of patients, family members, and partner pharmacies.
*   Improved productivity.

### 11.2. Tasks and Deliverables

**Table 9. Tasks and deliverables**

| No. | Task name | Description |
| :--- | :--- | :--- |
| **1.** | **Initiation** | |
| 1.1 | Requirement gathering and analysis | Collect business needs from the DrugTime product specification, identify stakeholders (patients, family members, partner pharmacies, partner pharmacists, Admin) and agree the in-scope feature set. |
| 1.2 | Proposal preparation and submission | Produce this proposal and the initial schedule. |
| 1.3 | Proposal presentation and approval | Present the proposal to the review panel and obtain approval to proceed. |
| **2.** | **Planning and design** | |
| 2.1 | Project plan | Baseline the schedule, work breakdown, team roles, and risk register. |
| 2.2 | Architecture Design Document | Produce the context, container, and component views, quality-attribute scenarios, and technical constraints for the modular-monolith architecture. |
| 2.3 | Database design documents | Produce the entity-relationship diagrams and table specifications for the medication, interaction, reminder, partner, and admin data. |
| **3.** | **Implementation** | |
| 3.1 | Sprint 1 – Platform, Identity & Core Data | Platform setup (CI/CD, database, Xcode); auth and onboarding; consent flows (PDPL 2025); drug-data source sync job; preliminary DPIA draft. |
| 3.2 | Sprint 2 – Core Reminders | Medication entry and schedule CRUD; local notifications and dose confirmation; health profile CRUD; catalogue CRUD with Admin dashboard; Patient–Family Member linking data model. |
| 3.3 | Sprint 3 – Adherence Tracking & Family Connection | Adherence history; account linking via QR/referral code (with unlink and sharing toggle); missed-dose detection and Family Member alerts; multi-patient switcher for Family Member. |
| 3.4 | Sprint 4 – Medical Safety | Medication look-up; drug-drug/drug-food interaction checks with mandatory disclaimer; scoped access for Family Member; cross-device (Android/iOS) testing. |
| 3.5 | Sprint 5 – High-Risk / Complex Features | Blister-pack scan (OCR) with manual confirmation; Simple Mode (high-contrast, single-button UI); consent-withdrawal/data-deletion flow with Admin approval queue; sensitive-data access log. |
| 3.6 | Sprint 6 – AI & Final Polish | AI-based meal-suggestion feature with mandatory disclaimer; DPIA finalized and signed off; compliance checklist review; full-system regression testing and bug-fixing across Android and iOS |
| **4.** | **Integration and release** | |
| 4.1 | System integration and end-to-end testing | Integrate all modules, execute end-to-end scenarios (onboarding → reminder → confirmation → family alert → interaction lookup → AI meal suggestion), and fix defects. |
| 4.2 | Final submission | Package the source code, documentation, and deployment for final submission. |
| 4.3 | Retrospective and defense preparation | Hold the project retrospective and prepare the defense presentation and demo. |
| **5.** | **Capstone defense** | Present and defend the completed system before the review panel. |

### 11.3. Development Schedule

**Table 10. Project master plan**

| NO | Task Name | Duration | Start | Finish |
| :--- | :--- | :--- | :--- | :--- |
| **1.** | **Initiation** | **3 days** | **10-Sep-2026** | **13-Sep-2026** |
| 1.1 | Requirement gathering and analysis | 1 day | 10-Sep-2026 | 11-Sep-2026 |
| 1.2 | Proposal preparation and submission | 1 day | 11-Sep-2026 | 12-Sep-2026 |
| 1.3 | Proposal presentation and project approval | 1 day | 12-Sep-2026 | 13-Sep-2026 |
| **2.** | **Planning and Design** | **13 days** | **12-Sep-2026** | **25-Sep-2026** |
| 2.1 | Project plan preparation | 2 days | 12-Sep-2026 | 14-Sep-2026 |
| 2.2 | Architecture Design Document | 4 days | 14-Sep-2026 | 18-Sep-2026 |
| 2.3 | Database design documents | 4 days | 21-Sep-2026 | 25-Sep-2026 |
| **3.** | **Implementation** | **84 days** | **14-Sep-2026** | **06-Dec-2026** |
| 3.1 | Sprint 1 – Platform, Identity & Core Data | 14 days | 14-Sep-2026 | 27-Sep-2026 |
| 3.2 | Sprint 2 – Core Reminders | 14 days | 28-Sep-2026 | 11-Oct-2026 |
| 3.3 | Sprint 3 – Adherence Tracking & Family Connection | 14 days | 12-Oct-2026 | 25-Oct-2026 |
| 3.4 | Sprint 4 – Medical Safety | 14 days | 26-Oct-2026 | 08-Nov-2026 |
| 3.5 | Sprint 5 – High-Risk / Complex Features | 14 days | 09-Nov-2026 | 22-Nov-2026 |
| 3.6 | Sprint 6 – AI & Final Polish | 14 days | 23-Nov-2026 | 06-Dec-2026 |
| **4.** | **Integration and Release** | **10 days** | **07-Dec-2026** | **16-Dec-2026** |
| 4.1 | System integration and end-to-end testing | 3 days | 07-Dec-2026 | 09-Dec-2026 |
| 4.2 | Final submission | 4 days | 10-Dec-2026 | 13-Dec-2026 |
| 4.3 | Project retrospective and defense preparation | 3 days | 14-Dec-2026 | 16-Dec-2026 |
| **5.** | **Capstone Defense** | **10 days** | **17-Dec-2026** | **26-Dec-2026** |

## 12. System Architecture Overview

### 12.1. Container / Component View
The system has six main containers:
*   **Mobile App (Patient & Family Member):** Flutter app for Android and iOS — on-device text recognition (Google ML Kit) and fuzzy matching, medication entry, reminders, dose confirmation, adherence history, interaction look-up, and Simple Mode.
*   **Admin Web Dashboard:** React + Next.js, used by the Admin to manage the medication and interaction catalogues.
*   **Backend API:** Python + FastAPI. Owns all business logic and enforces purpose-separated consent before any data action.
*   **Background Job Worker:** RQ + Redis, handles scheduled reminders and catalogue synchronization asynchronously so they don't block the API. When a scheduled check detects a missed dose, the worker triggers a push notification via Firebase Cloud Messaging (FCM) to the linked family caregiver's device.
*   **Redis (Render Key Value):** Job queue backing the Background Job Worker.
*   **Supabase (PostgreSQL + pgvector + Storage):** Primary data store — structured application data, vector-based interaction look-ups, and file/object storage.

Only the Backend API and the Background Job Worker read and write the Supabase database and Redis queue. The Mobile App and the Admin Web Dashboard access data exclusively through the Backend API, so that purpose-separated consent, family-link authorization and sensitive-data audit logging are enforced in a single place.

### 12.2. Architecture Style
The Backend API is a modular monolith: one deployable process, split into independent modules (medication, interaction, reminder, partner, admin), each owning its own data. This keeps the codebase organized like separate services without the operational overhead of real microservices — not justified for a 5-person team on a 3-month timeline.
Inside each module, a light hexagonal (ports-and-adapters) structure separates business logic from infrastructure: domain logic (e.g. how an interaction warning is generated) stays independent of frameworks, so it can be tested or changed without touching how data is stored or how notifications are sent.
Synchronous calls (FastAPI) are used where medical-data integrity must be immediate (e.g. saving a confirmed medication). Asynchronous jobs (RQ) are used where an instant response isn't needed (e.g. sending a scheduled reminder).

### 12.3. Deployment View
The Backend API runs as a Render Web Service and the Job Worker runs as a separate Render Background Worker, with Redis provisioned as a Render Key Value instance; Render handles automatic HTTPS. Supabase is used as a managed external service rather than self-hosted. This setup keeps cost near zero for the MVP, trading off horizontal scaling and high availability — acceptable for a 3-month timeline with a limited user base (see Section 8, Constraints and Assumptions).

### 12.4. System Context Diagram
*Figure 1. System context diagram*

**Actors:**

*   **Patient:**
    *   Account & Consent Management (Register / Login, Complete purpose-separated consent, Manage health profile, Withdraw consent / request data deletion)
    *   Medication Management (Add medication (manual input), Scan blister pack, Confirm medication, Manage medication schedule)
    *   Medication Reminder & Adherence (Receive reminder, Confirm dose intake, View adherence history)
    *   Drug Safety Lookup (Look up medication information, View drug–drug interaction warning, View drug–food interaction warning)
    *   Family Linking (Link family member, Confirm data-sharing consent on linking, Remove linked family member, Revoke data-sharing permission)
    *   Meal suggestion (View AI meal suggestion with explanation)
    *   Simple Mode (Switch to Simple Mode UI)
*   **Family member:**
    *   Family Monitoring (Link to patient account, Receive missed-dose alert, View adherence history, Manage multiple linked patients)
    *   Drug Safety Lookup (Look up medication information of linked patient, View drug–drug interaction warning of linked patient, View drug–food interaction warning of linked patient)
    *   AI Assistant (View AI meal suggestion with explanation for linked patient)
*   **Admin:**
    *   Catalog Management (Manage medication catalog, Manage interaction catalog, Synchronize catalog from external sources)
    *   Compliance Oversight (Conduct DPIA for new sensitive-data flows, Review PDPL 2025 / Decree 356 compliance, Process data deletion / consent withdrawal requests, View sensitive-data access log)

**External systems:**
*   **Supabase (Database + Storage):** stores patient profiles, medication schedules, and adherence history. The hosting region must be confirmed to determine whether a cross-border transfer assessment is required. 
*   **Firebase Cloud Messaging (FCM):** delivers push notifications to the linked family caregiver's device when a scheduled check detects a missed dose. 
*   **Vietnamese Drug Regulatory Data Source:** three official Vietnamese references, synchronized periodically into the medication and interaction catalogues: 
    *   dichvucong.dav.gov.vn / drugbank.vn (Cục Quản lý Dược): source for the officially licensed drug catalogue used for QR/OCR matching.
    *   tuongtacthuoc.ehealth.gov.vn (QĐ 5948/QĐ-BYT): source for the drug-drug interaction catalogue.
    *   Dược thư Quốc gia Việt Nam 2022: source for medication look-up content and food-interaction warnings.

## 13. Potential Risks and Mitigation Strategies
The following risks were identified during project initiation. Each risk is reviewed with the mentor at every status report and the register is updated in the project plan.

**Table 11. Risk register**

| ID | Risk | Impact | Likelihood | Mitigation |
| :--- | :--- | :--- | :--- | :--- |
| R-01 | The on-device blister-pack scan fails to match an entry against the licensed drug catalogue. | Medium | High | A manual-input fallback with full-text search is always available when automated matching fails; unmatched items are logged for the Admin's catalogue-synchronization review. |
| R-02 | An interaction warning is treated by a patient as medical advice rather than an automated look-up. | High | Medium | A disclaimer is shown on every interaction-warning screen directing the patient to consult a doctor or pharmacist; the in-app Ask-a-pharmacist escalation is a Phase 2 feature. |
| R-03 | Free-tier limits on Supabase are reached during the demo period. | Medium | Medium | Usage is monitored against each provider's free-tier quota; on-device blister-pack scanning has no cloud quota to exhaust, and manual input remains available as a fallback. |
| R-04 | Cross-border data-transfer and DPIA obligations under the 2025 Personal Data Protection Law are not completed before a sensitive-data flow goes live. | High | Medium | The DPIA and cross-border-transfer assessment (covering the AI meal-suggestion API) are scheduled as explicit Sprint 1 and Sprint 6 deliverables, owned by the AI/Admin & Platform track, and reviewed with the mentor. |
| R-05 | A team member becomes unavailable during the examination period. | Medium | Medium | Each of the two development tracks is owned by at least two members; setup instructions and design decisions are documented in the shared repository. |
| R-06 | Documentation deadlines (Architecture Design Document, Database Design Document) overlap with the first implementation sprint. | Medium | High | Documentation tasks are scheduled in parallel and assigned so that implementation on the other track continues without interruption. |
| R-07 | The AI meal-suggestion feature recommends a meal that is unsafe or unsuitable for a patient’s medications. | High | Low | Every suggestion carries the same medical disclaimer as interaction warnings and states it is not medical or dietary advice; the feature only suggests, it does not restrict or prescribe, and patients are directed to consult a doctor or pharmacist for dietary changes tied to a medical condition. |

## 14. Expected Outcomes / Deliverables
DrugTime brings together medication reminders, Vietnamese-formulary drug-interaction checking, and an AI-based meal-suggestion feature under a single, consent-driven platform built for Vietnamese patients managing multiple medications. The 3-month MVP (Phase 1) delivers manual and blister-pack-scan medication entry, local-notification reminders, real-time family alerts, a basic Admin dashboard, and an Simple Mode UI for both Android and iOS, while treating purpose-separated consent and data-protection compliance as first-class requirements rather than an afterthought. Partner-pharmacy connections, pharmacist escalation, Zalo reminders, voice confirmation, and the Premium tier are planned for a Phase 2 extension once the MVP is validated. The goal is to reduce missed doses, keep family caregivers informed in real time, and give patients a safer, more transparent way to manage multi-drug regimens than the international apps available today.

**Table 12. Key deliverables required by the Capstone schedule**

| No | Deliverable | Due date |
| :--- | :--- | :--- |
| 1 | Project Proposal | 13 Sep 2026 |
| 2 | Project Plan | 14 Sep 2026 |
| 3 | Architecture Design Document | 18 Sep 2026 |
| 4 | Database Design Document | 25 Sep 2026 |
| 5 | Midterm Report | 07 Nov 2026 |
| 6 | Final Submission | 13 Dec 2026 |
| 7 | Capstone Defense | 17 - 26 Dec 2026 |

## 15. References
[1]. University International School, Software Development Standards for the Guidance and Control of Capstone Projects, Da Nang, Viet Nam, 2026.  
[2]. National Assembly of Viet Nam, Law on Personal Data Protection, 2025.  
[3]. Government of Viet Nam, Decree No. 356/2025/NĐ-CP on Personal Data Protection.  
[4]. Bộ Y tế, Dược thư Quốc gia Việt Nam, tập 1 & 2, 2022.  
[5]. Bộ Y tế, Quyết định 5948/QĐ-BYT về việc ban hành Danh mục tương tác thuốc chống chỉ định trong thực hành lâm sàng tại các cơ sở khám bệnh, chữa bệnh. https://tuongtacthuoc.ehealth.gov.vn/.  
[6]. Cục Quản lý Dược, Danh mục thuốc lưu hành. https://dichvucong.dav.gov.vn/; drugbank.vn (accessed September 2026).  
[7]. Google, Cloud Vision API Documentation. https://cloud.google.com/vision (accessed September 2026).  
[8]. flutter_local_notifications, Flutter Local Notifications Plugin Documentation. https://pub.dev/packages/flutter_local_notifications (accessed September 2026).  
[9]. Zalo, Zalo Official Account Platform Documentation. https://developers.zalo.me/ (accessed September 2026).  
[10]. Supabase, Supabase Documentation. https://supabase.com/docs (accessed September 2026).  
[11]. Flutter, Flutter Documentation. https://docs.flutter.dev/ (accessed September 2026).  
[12]. FastAPI, FastAPI Documentation. https://fastapi.tiangolo.com/ (accessed September 2026).  
[13]. K. Schwaber and J. Sutherland, The Scrum Guide, November 2020. https://www.scrum.org/resources/scrum-guide (accessed September 2026).  
[14]. Medisafe Inc., Medisafe Medication Management App. https://www.medisafe.com/ (accessed September 2026).  
[15]. smartpatient GmbH, MyTherapy Medication Reminder App. https://www.mytherapyapp.com/ (accessed September 2026).