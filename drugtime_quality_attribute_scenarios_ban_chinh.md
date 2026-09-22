# DrugTime Quality Attribute Scenarios

### Table 2. Quality Attributes – Security & Privacy
| Field | Details |
|---|---|
| **ID** | QA.01 |
| **Title** | Withdraw consent for a specific data-processing purpose |
| **Quality Attribute** | Security & Privacy (NFR01) |
| **Source(s) of Stimulus** | Authenticated Patient |
| **Stimulus** | The Patient withdraws consent for one processing purpose (e.g., sharing data with a Family Member, or AI-based meal suggestions) from the account settings screen. |
| **Environment** | Runtime, normal operation, device connected to the Internet. |
| **Artifacts** | Backend API (consent enforcement layer), Supabase (consent data), Mobile App (consent settings screen) |
| **System Response** | Record the consent withdrawal with a timestamp. The Backend API rejects any further data-processing operation under the withdrawn purpose. Other purposes remain unaffected. If the Patient requests data deletion, the request is queued for Admin approval. |
| **Response Measure(s)** | - 100% of requests under the withdrawn purpose are rejected after the withdrawal time (0 requests slip through).<br>- Consent withdrawal takes effect within ≤ 5 seconds.<br>- 100% of data-deletion requests appear in the Admin queue within ≤ 1 minute.<br>- 0 other purposes are unintentionally affected. |

### Table 3. Quality Attributes – Security & Privacy
| Field | Details |
|---|---|
| **ID** | QA.02 |
| **Title** | Block a Family Member from accessing data outside the consent scope |
| **Quality Attribute** | Security & Privacy (NFR01) |
| **Source(s) of Stimulus** | A Family Member who is unlinked, has been unlinked, or whose sharing permission has been revoked by the Patient (including attempts to tamper with the patient ID in the request). |
| **Stimulus** | Sends a request to view a Patient's adherence history, medication information, or interaction warnings without authorization. |
| **Environment** | Runtime, normal operation. |
| **Artifacts** | Backend API (authentication and authorization), Supabase (family-linking and consent data) |
| **System Response** | Validate the token, check the linking relationship and consent scope before returning any data. Reject the request (HTTP 403) and return no health data. Log the denied access attempt. |
| **Response Measure(s)** | - 100% of unauthorized requests are rejected.<br>- 0 health records are returned for unauthorized requests.<br>- Permission revocation takes effect within ≤ 5 seconds.<br>- The cross-patient authorization test suite (≥ 20 cases) passes 100%. |

### Table 4. Quality Attributes – Usability
| Field | Details |
|---|---|
| **ID** | QA.03 |
| **Title** | Confirm medication intake in Simple Mode |
| **Quality Attribute** | Usability (NFR02) |
| **Source(s) of Stimulus** | Elderly Patient with limited technology experience. |
| **Stimulus** | Receives a medication reminder notification and wants to confirm the dose was taken. |
| **Environment** | Runtime, Simple Mode enabled, using a mobile device (possibly in low-light conditions). |
| **Artifacts** | Mobile App – reminder and dose-confirmation screen in Simple Mode |
| **System Response** | Display a minimal interface with one large, high-contrast confirmation button and large text. After confirmation, show clear feedback that the dose has been recorded. |
| **Response Measure(s)** | - Confirmation completed in ≤ 2 taps and ≤ 10 seconds from opening the notification.<br>- First-time success rate ≥ 90% (tested with ≥ 5 elderly users).<br>- Mis-tap rate ≤ 5%.<br>- Primary text contrast ratio ≥ 7:1, tap target size ≥ 48 dp, primary font size ≥ 18 sp. |

### Table 5. Quality Attributes – Localization
| Field | Details |
|---|---|
| **ID** | QA.04 |
| **Title** | Drug-interaction warnings aligned with Vietnamese guidelines |
| **Quality Attribute** | Localization (NFR03) |
| **Source(s) of Stimulus** | Patient or Family Member (for a linked Patient) |
| **Stimulus** | Adds a new medication or requests a drug-drug/drug-food interaction check for the current medication list. |
| **Environment** | Runtime, normal operation, Internet connection available. |
| **Artifacts** | Interaction Module, interaction catalog (Decision 5948/QĐ-BYT, Vietnam National Drug Formulary 2022) |
| **System Response** | Check drug/food pairs against the Vietnamese interaction catalog. Display the warning with severity level, reference source, and a mandatory medical disclaimer. |
| **Response Measure(s)** | - 100% of contraindicated pairs present in the loaded Decision 5948 dataset are detected (0 false negatives on the test set).<br>- 100% of warnings display a reference source and disclaimer.<br>- The test set (≥ 30 sample pairs) is manually cross-checked against the source document and achieves 100% accuracy. |

### Table 6. Quality Attributes – Performance
| Field | Details |
|---|---|
| **ID** | QA.05 |
| **Title** | Process medication dose confirmation |
| **Quality Attribute** | Performance (NFR04) |
| **Source(s) of Stimulus** | Patient |
| **Stimulus** | Taps the confirm-dose-taken button (random, non-periodic request). |
| **Environment** | Normal operation, device online. |
| **Artifacts** | Mobile App, Backend API (adherence), Supabase |
| **System Response** | The Backend API processes the request synchronously, records the taken dose in the adherence history, and returns the result. The Mobile App displays confirmation feedback as soon as the result is received. |
| **Response Measure(s)** | - Time from tap to confirmation display: p95 ≤ 2 seconds.<br>- Successful recording rate ≥ 99%, 0 records lost. |

### Table 7. Quality Attributes – Performance
| Field | Details |
|---|---|
| **ID** | QA.06 |
| **Title** | Deliver medication reminders on time |
| **Quality Attribute** | Performance (NFR04) |
| **Source(s) of Stimulus** | Device's local notification scheduler |
| **Stimulus** | A scheduled dose time is reached (periodic event). |
| **Environment** | Normal operation; app running in background or closed; notification permission granted. |
| **Artifacts** | Mobile App – reminder module (local notification) |
| **System Response** | Display an alarm-style notification at the scheduled time, with a dose-confirmation action. |
| **Response Measure(s)** | - Deviation from the scheduled time ≤ 2 seconds.<br>- ≥ 99% of scheduled notifications are delivered on time in tests on both Android and iOS. |

### Table 8. Quality Attributes – Availability
| Field | Details |
|---|---|
| **ID** | QA.07 |
| **Title** | Maintain ≥ 99% uptime for core services |
| **Quality Attribute** | Availability (NFR05) |
| **Source(s) of Stimulus** | Patient and Family Member using core services at any time of day. |
| **Stimulus** | Requests to use core services throughout the operating cycle: reminder synchronization and scheduling, adherence tracking, and drug lookup. |
| **Environment** | Runtime. |
| **Artifacts** | Backend API (adherence tracking, drug lookup), Background Job Worker (scheduled reminders), Supabase |
| **System Response** | Core services continue serving user requests. The system monitors the status of each core service via periodic health checks and logs every downtime interval to compute uptime. |
| **Response Measure(s)** | - Uptime of each core service (reminders, adherence tracking, drug lookup) ≥ 99% per month, equivalent to ≤ 7.2 hours of downtime per 30 days.<br>- Health checks run at intervals of ≤ 1 minute.<br>- 100% of downtime intervals are logged. |

### Table 9. Quality Attributes – Availability
| Field | Details |
|---|---|
| **ID** | QA.08 |
| **Title** | Reminders continue to function during network loss |
| **Quality Attribute** | Availability (NFR05) |
| **Source(s) of Stimulus** | Physical environment (Patient's device loses Internet access or cannot reach the Backend). |
| **Stimulus** | Network connectivity is lost exactly when a dose is due or when the Patient confirms a dose. |
| **Environment** | Degraded mode (offline); the medication schedule was previously synced. |
| **Artifacts** | Mobile App – local notification scheduler, local storage |
| **System Response** | The app still delivers reminders via local notification. Dose confirmations are stored locally and shown as "pending sync". Once connectivity is restored, the app automatically syncs to the Backend. Functions that require Internet access (interaction checking, meal suggestions) display a connectivity-required message. |
| **Response Measure(s)** | - 100% of scheduled reminders are still delivered while offline.<br>- 0 dose confirmations are lost.<br>- Sync completes within ≤ 30 seconds after connectivity is restored. |

### Table 10. Quality Attributes – Auditability
| Field | Details |
|---|---|
| **ID** | QA.09 |
| **Title** | Log every access to sensitive data |
| **Quality Attribute** | Auditability (NFR06) |
| **Source(s) of Stimulus** | Family Member or Admin |
| **Stimulus** | Accesses a Patient's health data (adherence history, medication list, interaction warnings). |
| **Environment** | Runtime, normal operation. |
| **Artifacts** | Backend API, Admin module (access log), Supabase (log table) |
| **System Response** | For each access, record an entry containing the actor, role, timestamp, the Patient accessed, and the data scope. Denied access attempts are also logged. Admin can view and filter the log on the Admin Web Dashboard. |
| **Response Measure(s)** | - 100% of accesses produce a log entry with all three fields (actor, timestamp, data scope) (0 unlogged accesses in the test set).<br>- The log entry appears within ≤ 5 seconds of the access.<br>- Logging does not cause operations to exceed the 2-second limit defined in NFR04. |

### Table 11. Quality Attributes – Modifiability
| Field | Details |
|---|---|
| **ID** | QA.10 |
| **Title** | Add a new disease group in Phase 2 |
| **Quality Attribute** | Modifiability (NFR07) |
| **Source(s) of Stimulus** | Developer (per Phase 2 scope-expansion requirements) |
| **Stimulus** | A request to add a new disease group (beyond the Phase 1 groups) to the system. |
| **Environment** | Development time, MVP system already completed. |
| **Artifacts** | Medication Module, Interaction Module, catalog data, Admin Web Dashboard |
| **System Response** | Add the catalog data and disease-group configuration (via Admin Dashboard or migration) without changing the logic of other modules. Run the regression test suite and deploy. |
| **Response Measure(s)** | - Completed within ≤ 3 person-days.<br>- ≤ 2 modules modified (Medication, Interaction); 0 changes to the Reminder module.<br>- 100% of the existing regression test suite still passes. |

### Table 12. Quality Attributes – Modifiability
| Field | Details |
|---|---|
| **ID** | QA.11 |
| **Title** | Add a Zalo OA reminder channel |
| **Quality Attribute** | Modifiability (NFR07) |
| **Source(s) of Stimulus** | Developer |
| **Stimulus** | A request to add Zalo OA as a secondary reminder channel (Phase 2 feature). |
| **Environment** | Development time and deployment time. |
| **Artifacts** | Reminder Module (notification port), Backend API, Background Job Worker |
| **System Response** | Write a new Zalo OA adapter implementing the existing notification port and register it via configuration. The Reminder Module's business logic remains unchanged. Test the adapter using a mock of the Zalo OA API. |
| **Response Measure(s)** | - Completed within ≤ 5 person-days.<br>- Only 1 adapter and its configuration are added; ≤ 1 existing module affected (Reminder).<br>- 0 changes to domain logic; 100% of the existing regression test suite still passes. |