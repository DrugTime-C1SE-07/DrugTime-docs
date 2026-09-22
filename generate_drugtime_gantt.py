# -*- coding: utf-8 -*-
"""
DrugTime Gantt Chart Generator
Generates:
1. Excel Gantt Chart (DrugTime_Gantt_Chart.xlsx) matching Activity Template
2. Interactive Frappe Gantt Dashboard (DrugTime_Gantt_Dashboard.html)
3. Markwhen Timeline (DrugTime_Timeline.mw)
4. Mermaid Diagram (DrugTime_Gantt_Chart.mmd and DrugTime_Gantt_Chart.md)
"""

import os
from datetime import date, timedelta
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

BASE_DIR = r"e:\DrugTIme_main\docs"

# ==============================================================================
# 1. DATA DEFINITION
# ==============================================================================

# Calendar: 16 weeks, Mon 2026-09-07 to Fri 2026-12-25 (80 workdays)
START_CAL_DATE = date(2026, 9, 7)
CAL_DATES = []
curr = START_CAL_DATE
while len(CAL_DATES) < 80:
    if curr.weekday() < 5:  # Mon to Fri
        CAL_DATES.append(curr)
    curr += timedelta(days=1)

DATE_TO_COL_IDX = {d.isoformat(): 9 + i for i, d in enumerate(CAL_DATES)}

# Master Schedule & Backlog Data
# Structure: (task_id, name, owner, start_date, due_date, duration_days, pct_complete, phase_name, tag, deps)
TASKS_DATA = [
    # --- PHASE 1: INITIATION & ARCHITECTURE DESIGN ---
    {"is_milestone": True, "id": "1", "name": "Project Initiation & Stakeholder Alignment", "owner": "Team 1", "start": "2026-09-10", "due": "2026-09-13", "duration": 3, "pct": 100, "phase": "Phase 1"},
    {"is_milestone": False, "id": "1.1", "name": "Requirement Gathering & Stakeholder Needs (Patients/Caregivers/Pharmacies)", "owner": "Nguyen Van Nguyen", "start": "2026-09-10", "due": "2026-09-11", "duration": 2, "pct": 100, "phase": "Phase 1", "tag": "req", "deps": ""},
    {"is_milestone": False, "id": "1.2", "name": "Project Proposal Preparation & Cost/Budget Estimation ($3,998)", "owner": "Nguyen Ngoc Phuc", "start": "2026-09-11", "due": "2026-09-12", "duration": 2, "pct": 100, "phase": "Phase 1", "tag": "proposal", "deps": "1.1"},
    {"is_milestone": False, "id": "1.3", "name": "Proposal Presentation & Capstone Review Panel Approval", "owner": "Team 1", "start": "2026-09-12", "due": "2026-09-13", "duration": 2, "pct": 100, "phase": "Phase 1", "tag": "proposal", "deps": "1.2"},

    {"is_milestone": True, "id": "2", "name": "Planning & Architecture Design", "owner": "Team 1", "start": "2026-09-12", "due": "2026-09-25", "duration": 13, "pct": 100, "phase": "Phase 1"},
    {"is_milestone": False, "id": "2.1", "name": "Project Plan Preparation, Work Breakdown & Risk Register", "owner": "Nguyen Ngoc Phuc", "start": "2026-09-12", "due": "2026-09-14", "duration": 3, "pct": 100, "phase": "Phase 1", "tag": "planning", "deps": ""},
    {"is_milestone": False, "id": "2.2", "name": "Architecture Design Document (Context/Container/Component & Non-functional)", "owner": "Duc, Bao, Viet", "start": "2026-09-14", "due": "2026-09-18", "duration": 5, "pct": 100, "phase": "Phase 1", "tag": "arch", "deps": "2.1"},
    {"is_milestone": False, "id": "2.3", "name": "Database Design Documents & Entity-Relationship Specifications (Schema v2)", "owner": "Phuc, Nguyen", "start": "2026-09-21", "due": "2026-09-25", "duration": 5, "pct": 100, "phase": "Phase 1", "tag": "database", "deps": "2.2"},

    # --- PHASE 2: IMPLEMENTATION (SPRINT 1 TO SPRINT 6) ---
    {"is_milestone": True, "id": "3", "name": "Sprint 1 - Platform, Identity & Core Data", "owner": "Team 1", "start": "2026-09-14", "due": "2026-09-27", "duration": 14, "pct": 35, "phase": "Phase 2"},
    {"is_milestone": False, "id": "3.01", "name": "[1.01] PB08: Design ERD (patient, medication, consent, catalog tables)", "owner": "Phuc, Nguyen", "start": "2026-09-14", "due": "2026-09-16", "duration": 3, "pct": 100, "phase": "Sprint 1", "tag": "database", "deps": ""},
    {"is_milestone": False, "id": "3.02", "name": "[1.02] PB08: Write Supabase migration scripts", "owner": "Phuc, Nguyen", "start": "2026-09-16", "due": "2026-09-18", "duration": 3, "pct": 75, "phase": "Sprint 1", "tag": "database", "deps": "3.01"},
    {"is_milestone": False, "id": "3.03", "name": "[1.03] PB08: Review & test migrations on clean DB", "owner": "Viet, Bao, Duc", "start": "2026-09-18", "due": "2026-09-21", "duration": 2, "pct": 20, "phase": "Sprint 1", "tag": "database", "deps": "3.02"},
    {"is_milestone": False, "id": "3.04", "name": "[1.04] PB07: Setup GitHub Actions (lint + test on PR)", "owner": "Nguyen Quang Bao", "start": "2026-09-14", "due": "2026-09-17", "duration": 4, "pct": 80, "phase": "Sprint 1", "tag": "devops", "deps": ""},
    {"is_milestone": False, "id": "3.05", "name": "[1.05] PB07: Setup auto-deploy to Oracle Cloud VM & Caddy reverse proxy", "owner": "Nguyen Tan Duc", "start": "2026-09-17", "due": "2026-09-21", "duration": 3, "pct": 60, "phase": "Sprint 1", "tag": "devops", "deps": "3.04"},
    {"is_milestone": False, "id": "3.06", "name": "[1.07] PB29: Confirm Mac access + configure free Apple ID in Xcode", "owner": "Duc, Phuc", "start": "2026-09-18", "due": "2026-09-21", "duration": 2, "pct": 50, "phase": "Sprint 1", "tag": "mobile", "deps": ""},
    {"is_milestone": False, "id": "3.07", "name": "[1.08] PB29: Configure Xcode project + automatic signing", "owner": "Duc, Phuc", "start": "2026-09-21", "due": "2026-09-23", "duration": 3, "pct": 20, "phase": "Sprint 1", "tag": "mobile", "deps": "3.06"},
    {"is_milestone": False, "id": "3.08", "name": "[1.09] PB29: Test: build & run app on real device via Xcode (debugging)", "owner": "Duc, Phuc", "start": "2026-09-23", "due": "2026-09-25", "duration": 3, "pct": 0, "phase": "Sprint 1", "tag": "mobile", "deps": "3.07"},
    {"is_milestone": False, "id": "3.09", "name": "[1.10] PB01: Backend: Supabase Auth integration (register/login API)", "owner": "Nguyen, Bao", "start": "2026-09-21", "due": "2026-09-23", "duration": 3, "pct": 40, "phase": "Sprint 1", "tag": "backend", "deps": "3.02"},
    {"is_milestone": False, "id": "3.10", "name": "[1.11] PB01: Mobile: Register/Login UI screens (Flutter)", "owner": "Bao, Duc", "start": "2026-09-21", "due": "2026-09-24", "duration": 4, "pct": 30, "phase": "Sprint 1", "tag": "mobile", "deps": "3.06"},
    {"is_milestone": False, "id": "3.11", "name": "[1.12] PB01: Mobile-Backend integration + error handling", "owner": "Bao, Duc", "start": "2026-09-24", "due": "2026-09-25", "duration": 2, "pct": 0, "phase": "Sprint 1", "tag": "mobile", "deps": "3.09, 3.10"},
    {"is_milestone": False, "id": "3.12", "name": "[1.13] PB01: Test: unit + widget test (Auth flow)", "owner": "Bao, Duc", "start": "2026-09-25", "due": "2026-09-25", "duration": 1, "pct": 0, "phase": "Sprint 1", "tag": "qa", "deps": "3.11"},
    {"is_milestone": False, "id": "3.13", "name": "[1.14] PB02: Backend: consents table + grant/revoke API per purpose (PDPL 2025)", "owner": "Viet, Phuc", "start": "2026-09-21", "due": "2026-09-23", "duration": 3, "pct": 30, "phase": "Sprint 1", "tag": "backend", "deps": "3.02"},
    {"is_milestone": False, "id": "3.14", "name": "[1.15] PB02: Mobile: consent UI (per-purpose toggles, no 'Accept All')", "owner": "Viet, Phuc", "start": "2026-09-23", "due": "2026-09-25", "duration": 3, "pct": 0, "phase": "Sprint 1", "tag": "mobile", "deps": "3.13"},
    {"is_milestone": False, "id": "3.15", "name": "[1.16] PB02: Test: consent flow end-to-end", "owner": "Viet, Phuc", "start": "2026-09-25", "due": "2026-09-25", "duration": 1, "pct": 0, "phase": "Sprint 1", "tag": "qa", "deps": "3.14"},
    {"is_milestone": False, "id": "3.16", "name": "[1.17] PB06: Research/parse Vietnamese Drug Regulatory Data Source structure", "owner": "All team member", "start": "2026-09-15", "due": "2026-09-22", "duration": 6, "pct": 50, "phase": "Sprint 1", "tag": "data", "deps": ""},
    {"is_milestone": False, "id": "3.17", "name": "[1.18] PB06: Build RQ scheduled sync job & Redis queue", "owner": "All team member", "start": "2026-09-21", "due": "2026-09-25", "duration": 5, "pct": 10, "phase": "Sprint 1", "tag": "backend", "deps": "3.16"},
    {"is_milestone": False, "id": "3.18", "name": "[1.19] PB41: Draft preliminary DPIA (planned sensitive-data flows)", "owner": "Phuc, Nguyen", "start": "2026-09-22", "due": "2026-09-25", "duration": 4, "pct": 25, "phase": "Sprint 1", "tag": "compliance", "deps": "3.01"},

    {"is_milestone": True, "id": "4", "name": "Sprint 2 - Core Reminders & Schedules", "owner": "Team 1", "start": "2026-09-28", "due": "2026-10-11", "duration": 14, "pct": 0, "phase": "Phase 2"},
    {"is_milestone": False, "id": "4.1", "name": "[PB10] Medication Entry API & Mobile Manual Form", "owner": "Nguyen, Viet, Bao, Duc", "start": "2026-09-28", "due": "2026-10-02", "duration": 5, "pct": 0, "phase": "Sprint 2", "tag": "core", "deps": "3.09"},
    {"is_milestone": False, "id": "4.2", "name": "[PB11] Medication Schedule CRUD API & Edit UI", "owner": "Nguyen, Phuc, Bao, Duc", "start": "2026-10-01", "due": "2026-10-06", "duration": 4, "pct": 0, "phase": "Sprint 2", "tag": "core", "deps": "4.1"},
    {"is_milestone": False, "id": "4.3", "name": "[PB12] Local Notification Engine & Offline Reminder Scheduling", "owner": "Duc, Phuc", "start": "2026-10-05", "due": "2026-10-09", "duration": 5, "pct": 0, "phase": "Sprint 2", "tag": "core", "deps": "4.2"},
    {"is_milestone": False, "id": "4.4", "name": "[PB13] Dose Confirmation Intake Button & Logging", "owner": "Bao, Duc", "start": "2026-10-07", "due": "2026-10-09", "duration": 3, "pct": 0, "phase": "Sprint 2", "tag": "core", "deps": "4.3"},
    {"is_milestone": False, "id": "4.5", "name": "[PB04/05] Admin Web Dashboard: Medication & Interaction Catalog CRUD", "owner": "Bao, Viet, Nguyen", "start": "2026-09-28", "due": "2026-10-08", "duration": 9, "pct": 0, "phase": "Sprint 2", "tag": "admin", "deps": "3.02"},
    {"is_milestone": False, "id": "4.6", "name": "[PB09] Patient-Family Linking Data Model & Migration", "owner": "Phuc, Nguyen, Viet", "start": "2026-10-05", "due": "2026-10-09", "duration": 5, "pct": 0, "phase": "Sprint 2", "tag": "database", "deps": "3.02"},

    {"is_milestone": True, "id": "5", "name": "Sprint 3 - Adherence Tracking & Family Connection", "owner": "Team 1", "start": "2026-10-12", "due": "2026-10-25", "duration": 14, "pct": 0, "phase": "Phase 2"},
    {"is_milestone": False, "id": "5.1", "name": "[PB14] Adherence History Calendar & Summary View", "owner": "Phuc, Viet, Bao, Duc", "start": "2026-10-12", "due": "2026-10-16", "duration": 5, "pct": 0, "phase": "Sprint 3", "tag": "mobile", "deps": "4.4"},
    {"is_milestone": False, "id": "5.2", "name": "[PB15/19] QR Code & Referral Code Linking Mechanism", "owner": "Nguyen, Phuc, Bao, Duc", "start": "2026-10-14", "due": "2026-10-19", "duration": 4, "pct": 0, "phase": "Sprint 3", "tag": "feature", "deps": "4.6"},
    {"is_milestone": False, "id": "5.3", "name": "[PB16/18] Data-Sharing Consent Controls & Scoped Revocation", "owner": "Viet, Phuc", "start": "2026-10-16", "due": "2026-10-21", "duration": 4, "pct": 0, "phase": "Sprint 3", "tag": "compliance", "deps": "5.2"},
    {"is_milestone": False, "id": "5.4", "name": "[PB20] Real-time Missed-Dose Alerts for Linked Caregivers", "owner": "Bao, Duc, Viet", "start": "2026-10-19", "due": "2026-10-23", "duration": 5, "pct": 0, "phase": "Sprint 3", "tag": "mobile", "deps": "5.3"},
    {"is_milestone": False, "id": "5.5", "name": "[PB22] Multi-Patient Switcher UI for Family Caregivers", "owner": "Bao, Duc, Viet", "start": "2026-10-21", "due": "2026-10-23", "duration": 3, "pct": 0, "phase": "Sprint 3", "tag": "mobile", "deps": "5.4"},

    {"is_milestone": True, "id": "6", "name": "Sprint 4 - Medical Safety & Drug Lookup", "owner": "Team 1", "start": "2026-10-26", "due": "2026-11-08", "duration": 14, "pct": 0, "phase": "Phase 2"},
    {"is_milestone": False, "id": "6.1", "name": "[PB23] Vietnamese Drug Regulatory Catalog Search & Detail View", "owner": "Nguyen, Viet, Bao, Duc", "start": "2026-10-26", "due": "2026-10-30", "duration": 5, "pct": 0, "phase": "Sprint 4", "tag": "search", "deps": "3.17"},
    {"is_milestone": False, "id": "6.2", "name": "[PB24] Drug-Drug Interaction Checking Engine & Warning UI", "owner": "Nguyen, Viet, Bao, Duc", "start": "2026-10-28", "due": "2026-11-03", "duration": 5, "pct": 0, "phase": "Sprint 4", "tag": "safety", "deps": "6.1"},
    {"is_milestone": False, "id": "6.3", "name": "[PB25] Drug-Food Interaction Checking Engine & Warning UI", "owner": "Nguyen, Viet, Bao, Duc", "start": "2026-11-02", "due": "2026-11-06", "duration": 5, "pct": 0, "phase": "Sprint 4", "tag": "safety", "deps": "6.2"},
    {"is_milestone": False, "id": "6.4", "name": "[PB26-28] Family Member Scoped Access for Drug Safety Lookup", "owner": "Viet, Phuc", "start": "2026-11-04", "due": "2026-11-06", "duration": 3, "pct": 0, "phase": "Sprint 4", "tag": "compliance", "deps": "6.3"},
    {"is_milestone": False, "id": "6.5", "name": "[PB30] Cross-Device Android & iOS Comprehensive Testing Checklist", "owner": "Team 1", "start": "2026-11-05", "due": "2026-11-06", "duration": 2, "pct": 0, "phase": "Sprint 4", "tag": "qa", "deps": "6.4"},

    {"is_milestone": True, "id": "7", "name": "Sprint 5 - High-Risk / Complex Features", "owner": "Team 1", "start": "2026-11-09", "due": "2026-11-22", "duration": 14, "pct": 0, "phase": "Phase 2"},
    {"is_milestone": False, "id": "7.1", "name": "[PB31] On-Device ML Kit OCR for Blister-Pack Scanning", "owner": "Bao, Duc, Viet", "start": "2026-11-09", "due": "2026-11-13", "duration": 5, "pct": 0, "phase": "Sprint 5", "tag": "ai", "deps": "6.1"},
    {"is_milestone": False, "id": "7.2", "name": "[PB32] OCR Text Matching Algorithm & Mandatory Manual Confirmation", "owner": "Nguyen, Viet, Bao", "start": "2026-11-12", "due": "2026-11-17", "duration": 4, "pct": 0, "phase": "Sprint 5", "tag": "mobile", "deps": "7.1"},
    {"is_milestone": False, "id": "7.3", "name": "[PB33] Simple Mode High-Contrast UI for Elderly Users", "owner": "Bao, Duc", "start": "2026-11-16", "due": "2026-11-19", "duration": 4, "pct": 0, "phase": "Sprint 5", "tag": "ui", "deps": "7.2"},
    {"is_milestone": False, "id": "7.4", "name": "[PB34/35] Consent Withdrawal & Right-to-be-Forgotten Data Deletion Flow", "owner": "Viet, Phuc, Nguyen", "start": "2026-11-16", "due": "2026-11-20", "duration": 5, "pct": 0, "phase": "Sprint 5", "tag": "compliance", "deps": "3.13"},
    {"is_milestone": False, "id": "7.5", "name": "[PB36] Sensitive-Data Access Audit Logging & Admin Log Viewer", "owner": "Nguyen, Viet, Phuc, Bao", "start": "2026-11-18", "due": "2026-11-20", "duration": 3, "pct": 0, "phase": "Sprint 5", "tag": "admin", "deps": "7.4"},

    {"is_milestone": True, "id": "8", "name": "Sprint 6 - AI & Final Polish", "owner": "Team 1", "start": "2026-11-23", "due": "2026-12-06", "duration": 14, "pct": 0, "phase": "Phase 2"},
    {"is_milestone": False, "id": "8.1", "name": "[PB37] AI Meal Suggestion Engine with Explanations & Medical Disclaimers", "owner": "Nguyen, Viet, Phuc, Bao", "start": "2026-11-23", "due": "2026-11-27", "duration": 5, "pct": 0, "phase": "Sprint 6", "tag": "ai", "deps": "6.3"},
    {"is_milestone": False, "id": "8.2", "name": "[PB39] Scoped AI Meal Suggestions for Family Caregivers", "owner": "Nguyen, Bao", "start": "2026-11-26", "due": "2026-11-30", "duration": 3, "pct": 0, "phase": "Sprint 6", "tag": "ai", "deps": "8.1"},
    {"is_milestone": False, "id": "8.3", "name": "[PB41/42] Final DPIA Sign-Off & PDPL 2025 Regulatory Compliance Audit", "owner": "Phuc, Nguyen, Viet", "start": "2026-11-26", "due": "2026-12-01", "duration": 4, "pct": 0, "phase": "Sprint 6", "tag": "compliance", "deps": "7.4"},
    {"is_milestone": False, "id": "8.4", "name": "[PB43] Full-System Regression Testing & Defect Fixing (Android + iOS)", "owner": "Team 1", "start": "2026-11-30", "due": "2026-12-04", "duration": 5, "pct": 0, "phase": "Sprint 6", "tag": "qa", "deps": "8.1, 8.3"},

    # --- PHASE 3: INTEGRATION, FINAL RELEASE & DEFENSE ---
    {"is_milestone": True, "id": "9", "name": "Integration and Final Release", "owner": "Team 1", "start": "2026-12-07", "due": "2026-12-16", "duration": 10, "pct": 0, "phase": "Phase 3"},
    {"is_milestone": False, "id": "9.1", "name": "End-to-End Core User Journey Verification (Onboard -> Reminder -> Dose -> Alert -> AI)", "owner": "Team 1", "start": "2026-12-07", "due": "2026-12-09", "duration": 3, "pct": 0, "phase": "Phase 3", "tag": "qa", "deps": "8.4"},
    {"is_milestone": False, "id": "9.2", "name": "Final Submission Package (Source Code, APK/IPA, Docs, Deployment Setup)", "owner": "Phuc, Bao, Duc", "start": "2026-12-10", "due": "2026-12-14", "duration": 3, "pct": 0, "phase": "Phase 3", "tag": "release", "deps": "9.1"},
    {"is_milestone": False, "id": "9.3", "name": "Project Retrospective & Capstone Defense Demo Rehearsal", "owner": "Team 1", "start": "2026-12-14", "due": "2026-12-16", "duration": 3, "pct": 0, "phase": "Phase 3", "tag": "defense", "deps": "9.2"},

    {"is_milestone": True, "id": "10", "name": "Capstone Defense", "owner": "Team 1", "start": "2026-12-17", "due": "2026-12-25", "duration": 7, "pct": 0, "phase": "Phase 3"},
    {"is_milestone": False, "id": "10.1", "name": "Capstone Project 1 Final Defense Presentation & System Demonstration", "owner": "Team 1", "start": "2026-12-17", "due": "2026-12-25", "duration": 7, "pct": 0, "phase": "Phase 3", "tag": "defense", "deps": "9.3"}
]

# ==============================================================================
# 2. GENERATE EXCEL GANTT CHART
# ==============================================================================

def generate_excel():
    excel_path = os.path.join(BASE_DIR, "DrugTime_Gantt_Chart.xlsx")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Gantt Chart"
    ws.views.sheetView[0].showGridLines = True

    # Styling definitions
    FONT_TITLE = Font(name="Arial", size=22, bold=True, color="FF38761D")
    FONT_SUBTITLE = Font(name="Arial", size=10, bold=True, color="FF34A853")
    FONT_HEADER = Font(name="Arial", size=8, bold=True, color="FF000000")
    FONT_PHASE = Font(name="Arial", size=9, bold=True, color="FF073763")
    FONT_WEEK = Font(name="Arial", size=8, bold=True, color="FF073763")
    FONT_MONTH = Font(name="Arial", size=8, bold=True, color="FF073763")
    FONT_DAY = Font(name="Arial", size=7, bold=True, color="FF434343")
    FONT_DATE_NUM = Font(name="Arial", size=8, bold=True, color="FF073763")

    FONT_MILESTONE = Font(name="Arial", size=10, bold=True, color="FF000000")
    FONT_TASK = Font(name="Arial", size=9, bold=False, color="FF333333")

    FILL_TITLE_BG = PatternFill(start_color="FFD9EAD3", end_color="FFD9EAD3", fill_type="solid")
    FILL_HEADER = PatternFill(start_color="FFEFEFEF", end_color="FFEFEFEF", fill_type="solid")
    FILL_PHASE_HEADER = PatternFill(start_color="FFCFE2F3", end_color="FFCFE2F3", fill_type="solid")
    FILL_MILESTONE = PatternFill(start_color="FFE0E0E0", end_color="FFE0E0E0", fill_type="solid")
    FILL_BAR_ACTIVE = PatternFill(start_color="FF6FA8DC", end_color="FF6FA8DC", fill_type="solid") # Light Blue
    FILL_BAR_DONE = PatternFill(start_color="FF93C47D", end_color="FF93C47D", fill_type="solid")   # Green
    FILL_BAR_PLAN = PatternFill(start_color="FFB4C6E7", end_color="FFB4C6E7", fill_type="solid")   # Soft Blue

    BORDER_THIN = Border(
        left=Side(style="thin", color="FFE0E0E0"),
        right=Side(style="thin", color="FFE0E0E0"),
        top=Side(style="thin", color="FFE0E0E0"),
        bottom=Side(style="thin", color="FFE0E0E0")
    )
    BORDER_BAR = Border(
        left=Side(style="thin", color="FF8090A0"),
        right=Side(style="thin", color="FF8090A0"),
        top=Side(style="thin", color="FF8090A0"),
        bottom=Side(style="thin", color="FF8090A0")
    )
    BORDER_HEADER = Border(
        left=Side(style="thin", color="FF999999"),
        right=Side(style="thin", color="FF999999"),
        top=Side(style="thin", color="FF999999"),
        bottom=Side(style="thin", color="FF999999")
    )

    ALIGN_CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ALIGN_LEFT = Alignment(horizontal="left", vertical="center")
    ALIGN_RIGHT = Alignment(horizontal="right", vertical="center")

    # Column widths
    ws.column_dimensions["A"].width = 3.0
    ws.column_dimensions["B"].width = 11.0 # Task ID
    ws.column_dimensions["C"].width = 54.0 # Milestones & Tasks
    ws.column_dimensions["D"].width = 24.0 # Task Owner
    ws.column_dimensions["E"].width = 11.0 # Start Date
    ws.column_dimensions["F"].width = 11.0 # Due Date
    ws.column_dimensions["G"].width = 9.0  # Duration
    ws.column_dimensions["H"].width = 12.0 # % Complete

    for i in range(80):
        col_letter = get_column_letter(9 + i)
        ws.column_dimensions[col_letter].width = 3.2

    # Title banner
    ws.merge_cells("B7:H7")
    cell_b7 = ws["B7"]
    cell_b7.value = "DrugTime - Project Master Gantt Chart"
    cell_b7.font = FONT_TITLE
    cell_b7.fill = FILL_TITLE_BG
    cell_b7.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[7].height = 38

    # Project metadata
    ws["B9"].value = "PROJECT: DrugTime MVP - Mobile Medication Management Platform"
    ws["B9"].font = FONT_SUBTITLE
    ws["B10"].value = "PROJECT LEAD: Phuc Nguyen Ngoc | MENTOR: Giap Trong Nguyen (Kaopiz Da Nang)"
    ws["B10"].font = Font(name="Arial", size=9, bold=True, color="FF434343")

    ws["D9"].value = "SPONSOR: International School, Duy Tan University"
    ws["D9"].font = Font(name="Arial", size=9, bold=False, color="FF434343")
    ws["D10"].value = "TEAM: Nguyen Ngoc Phuc, Nguyen Quang Bao, Nguyen Tan Duc, Nguyen Van Nguyen, Dang Ngo Ngoc Viet"
    ws["D10"].font = Font(name="Arial", size=9, bold=False, color="FF434343")

    ws["F9"].value = "TIMELINE: 10-Sep-2026 to 26-Dec-2026 (16 Weeks)"
    ws["F9"].font = Font(name="Arial", size=9, bold=True, color="FF073763")
    ws["F10"].value = "SPRINT CYCLE: 6 Sprints x 2 Weeks (14 Days)"
    ws["F10"].font = Font(name="Arial", size=9, bold=False, color="FF073763")

    # Table headers
    headers = [
        ("B", "TASK ID NUMBER"),
        ("C", "MILESTONES & TASKS"),
        ("D", "TASK OWNER"),
        ("E", "START DATE"),
        ("F", "DUE DATE"),
        ("G", "DURATION\n(DAYS)"),
        ("H", "% OF TASK\nCOMPLETE")
    ]
    for col_char, title in headers:
        ws.merge_cells(f"{col_char}13:{col_char}16")
        c = ws[f"{col_char}13"]
        c.value = title
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.alignment = ALIGN_CENTER
        for r in range(13, 17):
            ws[f"{col_char}{r}"].border = BORDER_HEADER

    # Row 13: Phase spans
    phases = [
        (9, 18, "PHASE 1: INITIATION & ARCHITECTURE DESIGN"),
        (19, 73, "PHASE 2: IMPLEMENTATION (SPRINT 1 TO SPRINT 6)"),
        (74, 88, "PHASE 3: INTEGRATION, FINAL RELEASE & DEFENSE")
    ]
    for c_start, c_end, p_title in phases:
        ws.merge_cells(start_row=13, start_column=c_start, end_row=13, end_column=c_end)
        c = ws.cell(13, c_start)
        c.value = p_title
        c.font = FONT_PHASE
        c.fill = FILL_PHASE_HEADER
        c.alignment = ALIGN_CENTER
        for col in range(c_start, c_end + 1):
            ws.cell(13, col).border = BORDER_HEADER

    # Row 14: Weeks (16 weeks)
    for w in range(16):
        w_start = 9 + w * 5
        w_end = w_start + 4
        ws.merge_cells(start_row=14, start_column=w_start, end_row=14, end_column=w_end)
        c = ws.cell(14, w_start)
        c.value = f"WEEK {w + 1}"
        c.font = FONT_WEEK
        c.fill = FILL_PHASE_HEADER
        c.alignment = ALIGN_CENTER
        for col in range(w_start, w_end + 1):
            ws.cell(14, col).border = BORDER_HEADER

    # Row 15: Months
    month_spans = [
        (9, 26, "SEPTEMBER 2026"),
        (27, 48, "OCTOBER 2026"),
        (49, 69, "NOVEMBER 2026"),
        (70, 88, "DECEMBER 2026")
    ]
    for m_start, m_end, m_name in month_spans:
        ws.merge_cells(start_row=15, start_column=m_start, end_row=15, end_column=m_end)
        c = ws.cell(15, m_start)
        c.value = m_name
        c.font = FONT_MONTH
        c.fill = FILL_PHASE_HEADER
        c.alignment = ALIGN_CENTER
        for col in range(m_start, m_end + 1):
            ws.cell(15, col).border = BORDER_HEADER

    # Row 16 & 17: Day initials and day numbers
    day_chars = ["M", "T", "W", "R", "F"]
    for i, dt in enumerate(CAL_DATES):
        col = 9 + i
        c16 = ws.cell(16, col)
        c16.value = day_chars[dt.weekday()]
        c16.font = FONT_DAY
        c16.fill = FILL_HEADER
        c16.alignment = ALIGN_CENTER
        c16.border = BORDER_HEADER

        c17 = ws.cell(17, col)
        c17.value = dt.day
        c17.font = FONT_DATE_NUM
        c17.fill = FILL_HEADER
        c17.alignment = ALIGN_CENTER
        c17.border = BORDER_HEADER

    # Fill Tasks rows starting at Row 18
    current_row = 18
    for item in TASKS_DATA:
        ws.row_dimensions[current_row].height = 20
        is_m = item["is_milestone"]

        # Base properties
        c_id = ws.cell(current_row, 2, value=item["id"])
        c_name = ws.cell(current_row, 3, value=item["name"])
        c_owner = ws.cell(current_row, 4, value=item["owner"] if not is_m else "")
        
        # Start & Due
        d_start = date.fromisoformat(item["start"])
        d_due = date.fromisoformat(item["due"])
        c_start = ws.cell(current_row, 5, value=f"{d_start.month}/{d_start.day}")
        c_due = ws.cell(current_row, 6, value=f"{d_due.month}/{d_due.day}")
        c_dur = ws.cell(current_row, 7, value=item["duration"])
        c_pct = ws.cell(current_row, 8, value=f"{item['pct']}%")

        if is_m:
            for c_idx in range(2, 9):
                cell = ws.cell(current_row, c_idx)
                cell.font = FONT_MILESTONE
                cell.fill = FILL_MILESTONE
                cell.border = BORDER_THIN
            c_id.alignment = ALIGN_CENTER
            c_name.alignment = ALIGN_LEFT
            c_start.alignment = ALIGN_CENTER
            c_due.alignment = ALIGN_CENTER
            c_dur.alignment = ALIGN_CENTER
            c_pct.alignment = ALIGN_CENTER
        else:
            for c_idx in range(2, 9):
                cell = ws.cell(current_row, c_idx)
                cell.font = FONT_TASK
                cell.border = BORDER_THIN
            c_id.alignment = ALIGN_CENTER
            c_name.alignment = ALIGN_LEFT
            c_owner.alignment = ALIGN_LEFT
            c_start.alignment = ALIGN_CENTER
            c_due.alignment = ALIGN_CENTER
            c_dur.alignment = ALIGN_RIGHT
            c_pct.alignment = ALIGN_RIGHT

        # Fill calendar bar cells
        # Identify start and end columns based on dates
        # Find active workdays for this task
        active_days = set()
        c_date = d_start
        while c_date <= d_due:
            if c_date.weekday() < 5:
                active_days.add(c_date)
            c_date += timedelta(days=1)

        for col_idx, dt in enumerate(CAL_DATES):
            grid_col = 9 + col_idx
            bar_cell = ws.cell(current_row, grid_col)
            bar_cell.border = BORDER_THIN

            if dt in active_days:
                if is_m:
                    bar_cell.fill = FILL_MILESTONE
                elif item["pct"] == 100:
                    bar_cell.fill = FILL_BAR_DONE
                    bar_cell.border = BORDER_BAR
                elif item["pct"] > 0:
                    bar_cell.fill = FILL_BAR_ACTIVE
                    bar_cell.border = BORDER_BAR
                else:
                    bar_cell.fill = FILL_BAR_PLAN
                    bar_cell.border = BORDER_BAR

        current_row += 1

    wb.save(excel_path)
    print(f"[OK] Generated Excel: {excel_path} ({current_row - 18} tasks)")

# ==============================================================================
# 3. GENERATE FRAPPE GANTT INTERACTIVE HTML DASHBOARD
# ==============================================================================

def generate_frappe_gantt_html():
    html_path = os.path.join(BASE_DIR, "DrugTime_Gantt_Dashboard.html")
    
    # Prepare JSON array for Frappe Gantt
    tasks_js = []
    for item in TASKS_DATA:
        # Frappe Gantt requires YYYY-MM-DD
        # End date for frappe gantt is exclusive or inclusive depending on config; we supply due date
        # If milestone, add a custom class
        css_class = ""
        if item["is_milestone"]:
            css_class = "bar-milestone"
        elif item["pct"] == 100:
            css_class = "bar-done"
        elif item["pct"] > 0:
            css_class = "bar-active"
        else:
            css_class = "bar-pending"

        deps = item.get("deps", "")
        # Format task name cleanly
        name = item["name"]
        if len(name) > 60:
            name = name[:57] + "..."

        # Frappe Gantt object
        tasks_js.append({
            "id": f"T_{item['id'].replace('.', '_')}",
            "name": f"{item['id']} {name}",
            "start": item["start"],
            "end": item["due"],
            "progress": item["pct"],
            "dependencies": ", ".join([f"T_{d.replace('.', '_')}" for d in deps.split(", ") if d]),
            "custom_class": css_class,
            "owner": item["owner"],
            "phase": item["phase"],
            "full_name": item["name"],
            "duration": item["duration"]
        })

    import json
    tasks_json_str = json.dumps(tasks_js, indent=2)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DrugTime - Interactive Gantt Chart & Sprint Roadmap</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/frappe-gantt/dist/frappe-gantt.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --primary: #2b6cb0;
      --primary-dark: #1a4971;
      --accent: #319795;
      --bg-main: #f7fafc;
      --bg-card: #ffffff;
      --border: #e2e8f0;
      --text-main: #2d3748;
      --text-muted: #718096;
      --done-color: #38a169;
      --active-color: #3182ce;
      --pending-color: #a0aec0;
      --milestone-color: #4a5568;
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg-main);
      color: var(--text-main);
      line-height: 1.5;
      padding: 24px;
    }}
    .header-card {{
      background: var(--bg-card);
      border-radius: 12px;
      padding: 24px;
      border: 1px solid var(--border);
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
      margin-bottom: 20px;
    }}
    .header-top {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      flex-wrap: wrap;
      gap: 16px;
    }}
    .project-badge {{
      display: inline-block;
      background: #ebf8ff;
      color: #2b6cb0;
      font-weight: 600;
      font-size: 12px;
      padding: 4px 10px;
      border-radius: 9999px;
      margin-bottom: 8px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    h1 {{
      font-size: 24px;
      font-weight: 700;
      color: #1a202c;
      margin-bottom: 6px;
    }}
    .subtitle {{
      color: var(--text-muted);
      font-size: 14px;
      max-width: 800px;
    }}
    .stats-row {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin-top: 20px;
    }}
    .stat-box {{
      background: #f8fafc;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px 16px;
    }}
    .stat-label {{
      font-size: 12px;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      font-weight: 600;
    }}
    .stat-val {{
      font-size: 20px;
      font-weight: 700;
      color: #2d3748;
      margin-top: 2px;
    }}
    .controls-card {{
      background: var(--bg-card);
      border-radius: 12px;
      padding: 16px 20px;
      border: 1px solid var(--border);
      margin-bottom: 20px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
    }}
    .btn-group {{
      display: inline-flex;
      border-radius: 8px;
      border: 1px solid var(--border);
      overflow: hidden;
    }}
    .btn-group button {{
      background: #fff;
      border: none;
      padding: 8px 16px;
      font-size: 13px;
      font-weight: 500;
      color: var(--text-main);
      cursor: pointer;
      transition: all 0.15s ease;
      border-right: 1px solid var(--border);
    }}
    .btn-group button:last-child {{
      border-right: none;
    }}
    .btn-group button.active, .btn-group button:hover {{
      background: var(--primary);
      color: #fff;
    }}
    .filter-inputs {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .search-input, .select-filter {{
      padding: 8px 12px;
      border-radius: 6px;
      border: 1px solid var(--border);
      font-size: 13px;
      outline: none;
      font-family: inherit;
    }}
    .search-input:focus, .select-filter:focus {{
      border-color: var(--primary);
    }}
    .legend-row {{
      display: flex;
      gap: 16px;
      font-size: 12px;
      align-items: center;
      flex-wrap: wrap;
    }}
    .legend-item {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .legend-dot {{
      width: 12px;
      height: 12px;
      border-radius: 3px;
    }}
    .gantt-wrapper {{
      background: var(--bg-card);
      border-radius: 12px;
      border: 1px solid var(--border);
      padding: 20px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
      overflow-x: auto;
    }}
    #gantt {{
      min-width: 900px;
    }}
    /* Frappe Gantt custom overrides */
    .bar-milestone .bar {{
      fill: #4a5568 !important;
    }}
    .bar-done .bar {{
      fill: #38a169 !important;
    }}
    .bar-active .bar {{
      fill: #3182ce !important;
    }}
    .bar-pending .bar {{
      fill: #a0aec0 !important;
    }}
    .gantt .bar-progress {{
      fill: #276749 !important;
    }}
    .details-container {{
      padding: 12px;
      background: #ffffff;
      border-radius: 8px;
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
      border: 1px solid #e2e8f0;
      max-width: 320px;
      font-family: 'Inter', sans-serif;
    }}
    .details-container h5 {{
      font-size: 14px;
      font-weight: 600;
      color: #1a202c;
      margin-bottom: 6px;
    }}
    .details-container p {{
      font-size: 12px;
      color: #4a5568;
      margin-bottom: 4px;
    }}
    .details-container .badge {{
      display: inline-block;
      font-size: 10px;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 4px;
      background: #edf2f7;
      color: #4a5568;
      margin-top: 4px;
    }}
    .team-banner {{
      margin-top: 16px;
      padding-top: 14px;
      border-top: 1px dashed var(--border);
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
      font-size: 12px;
    }}
    .team-pill {{
      background: #edf2f7;
      padding: 4px 10px;
      border-radius: 6px;
      border: 1px solid var(--border);
      color: var(--text-main);
    }}
  </style>
</head>
<body>

  <div class="header-card">
    <div class="header-top">
      <div>
        <span class="project-badge">DTU C1SE.07 - Capstone Project 1</span>
        <h1>DrugTime: Mobile Medication Management Platform</h1>
        <p class="subtitle">
          Master Gantt Chart & Sprint Backlog Roadmap (10-Sep-2026 to 26-Dec-2026).
          Tracking 6 two-week sprints, architecture milestones, and compliance verification under PDPL 2025.
        </p>
      </div>
      <div style="text-align: right; min-width: 280px;">
        <div style="margin-bottom: 6px;">
          <span style="font-size: 11px; color: var(--text-muted); font-weight: 600; text-transform: uppercase;">Project Sponsor:</span>
          <div style="font-weight: 600; font-size: 13px;">International School, Duy Tan University</div>
        </div>
        <div style="margin-bottom: 6px;">
          <span style="font-size: 11px; color: var(--text-muted); font-weight: 600; text-transform: uppercase;">Project Mentor:</span>
          <div style="font-weight: 600; font-size: 13px;">Giap Trong Nguyen, Kaopiz Da Nang</div>
        </div>
        <div>
          <span style="font-size: 11px; color: var(--text-muted); font-weight: 600; text-transform: uppercase;">Project Lead:</span>
          <div style="font-weight: 700; font-size: 15px; color: var(--primary);">Phuc Nguyen Ngoc</div>
        </div>
      </div>
    </div>

    <div class="team-banner">
      <span style="font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Project Team:</span>
      <span class="team-pill"><strong>Nguyen Ngoc Phuc</strong> - Leader, Dev, QA</span>
      <span class="team-pill"><strong>Nguyen Quang Bao</strong> - Dev, QA, DevOps</span>
      <span class="team-pill"><strong>Nguyen Tan Duc</strong> - Dev, QA, DevOps</span>
      <span class="team-pill"><strong>Nguyen Van Nguyen</strong> - BA, Dev, QA</span>
      <span class="team-pill"><strong>Dang Ngo Ngoc Viet</strong> - Dev, QA, DevOps</span>
    </div>

    <div class="stats-row">
      <div class="stat-box">
        <div class="stat-label">Total Duration</div>
        <div class="stat-val">16 Weeks (80 Days)</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">Sprints Planned</div>
        <div class="stat-val">6 Sprints (14d/sprint)</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">Total Tasks Tracked</div>
        <div class="stat-val">{len(TASKS_DATA)} Tasks</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">Current Active Sprint</div>
        <div class="stat-val" style="color: var(--primary);">Sprint 1 (Onboarding)</div>
      </div>
    </div>
  </div>

  <div class="controls-card">
    <div style="display: flex; align-items: center; gap: 16px; flex-wrap: wrap;">
      <div class="btn-group" id="view-mode-buttons">
        <button type="button" data-mode="Day">Day</button>
        <button type="button" data-mode="Week" class="active">Week</button>
        <button type="button" data-mode="Month">Month</button>
      </div>

      <div class="filter-inputs">
        <input type="text" id="search-box" class="search-input" placeholder="Search task or owner...">
        <select id="phase-filter" class="select-filter">
          <option value="all">All Phases & Sprints</option>
          <option value="Phase 1">Phase 1: Initiation & Architecture</option>
          <option value="Sprint 1">Sprint 1: Platform, Identity & Core Data</option>
          <option value="Sprint 2">Sprint 2: Core Reminders & Schedules</option>
          <option value="Sprint 3">Sprint 3: Adherence & Family Connection</option>
          <option value="Sprint 4">Sprint 4: Medical Safety & Drug Lookup</option>
          <option value="Sprint 5">Sprint 5: High-Risk (OCR & Simple Mode)</option>
          <option value="Sprint 6">Sprint 6: AI Meal & Final Polish</option>
          <option value="Phase 3">Phase 3: Integration & Defense</option>
        </select>
      </div>
    </div>

    <div class="legend-row">
      <div class="legend-item"><span class="legend-dot" style="background:#38a169;"></span> Completed (100%)</div>
      <div class="legend-item"><span class="legend-dot" style="background:#3182ce;"></span> In Progress</div>
      <div class="legend-item"><span class="legend-dot" style="background:#a0aec0;"></span> Planned</div>
      <div class="legend-item"><span class="legend-dot" style="background:#4a5568;"></span> Phase Milestone</div>
    </div>
  </div>

  <div class="gantt-wrapper">
    <svg id="gantt"></svg>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/frappe-gantt/dist/frappe-gantt.umd.js"></script>
  <script>
    const allTasks = {tasks_json_str};

    let currentTasks = [...allTasks];
    let gantt = null;

    function initGantt(tasks, mode = 'Week') {{
      document.getElementById('gantt').innerHTML = '';
      if (tasks.length === 0) {{
        document.getElementById('gantt').innerHTML = '<text x="20" y="50" fill="#718096">No tasks found matching filter.</text>';
        return;
      }}
      gantt = new Gantt("#gantt", tasks, {{
        header_height: 50,
        column_width: mode === 'Day' ? 38 : (mode === 'Week' ? 55 : 90),
        step: 24,
        view_modes: ['Day', 'Week', 'Month'],
        view_mode: mode,
        date_format: 'YYYY-MM-DD',
        custom_popup_html: function(task) {{
          return `
            <div class="details-container">
              <h5>${{task.full_name || task.name}}</h5>
              <p><strong>Owner:</strong> ${{task.owner || 'Team 1'}}</p>
              <p><strong>Dates:</strong> ${{task._start.toLocaleDateString('en-GB')}}  ${{task._end.toLocaleDateString('en-GB')}} (${{task.duration || 1}} days)</p>
              <p><strong>Progress:</strong> ${{task.progress}}%</p>
              <span class="badge">${{task.phase || 'Roadmap'}}</span>
            </div>
          `;
        }}
      }});
    }}

    // Initial render
    initGantt(currentTasks, 'Week');

    // View mode handlers
    document.querySelectorAll('#view-mode-buttons button').forEach(btn => {{
      btn.addEventListener('click', (e) => {{
        document.querySelectorAll('#view-mode-buttons button').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        const mode = e.target.getAttribute('data-mode');
        if (gantt) {{
          gantt.change_view_mode(mode);
        }}
      }});
    }});

    // Filtering logic
    function applyFilters() {{
      const query = document.getElementById('search-box').value.toLowerCase();
      const phase = document.getElementById('phase-filter').value;

      currentTasks = allTasks.filter(t => {{
        const matchQuery = t.name.toLowerCase().includes(query) || (t.owner && t.owner.toLowerCase().includes(query));
        const matchPhase = (phase === 'all') || (t.phase === phase);
        return matchQuery && matchPhase;
      }});

      const activeMode = document.querySelector('#view-mode-buttons button.active').getAttribute('data-mode');
      initGantt(currentTasks, activeMode);
    }}

    document.getElementById('search-box').addEventListener('input', applyFilters);
    document.getElementById('phase-filter').addEventListener('change', applyFilters);
  </script>
</body>
</html>
"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[OK] Generated Frappe Gantt HTML: {html_path}")

# ==============================================================================
# 4. GENERATE MARKWHEN TIMELINE (.mw)
# ==============================================================================

def generate_markwhen():
    mw_path = os.path.join(BASE_DIR, "DrugTime_Timeline.mw")

    lines = [
        "title: DrugTime Master Project & Sprint Backlog Timeline",
        "dateFormat: YYYY-MM-DD",
        "timezone: Asia/Ho_Chi_Minh",
        "author: Phuc Nguyen Ngoc (Project Lead)",
        "mentor: Giap Trong Nguyen (Kaopiz Da Nang)",
        "sponsor: International School, Duy Tan University",
        "team: Nguyen Ngoc Phuc, Nguyen Quang Bao, Nguyen Tan Duc, Nguyen Van Nguyen, Dang Ngo Ngoc Viet",
        "project: DrugTime MVP - Capstone Project 1",
        "",
        "# Phase 1: Initiation & Architecture Design #phase1",
        "section Initiation #initiation",
        "2026-09-10 - 2026-09-11: 1.1 Requirement Gathering & Analysis #req [100%]",
        "2026-09-11 - 2026-09-12: 1.2 Proposal Preparation & Budgeting #proposal [100%]",
        "2026-09-12 - 2026-09-13: 1.3 Proposal Presentation & Mentor Sign-off #proposal [100%]",
        "",
        "section Planning & Architecture #planning",
        "2026-09-12 - 2026-09-14: 2.1 Project Plan & Risk Register #mgmt [100%]",
        "2026-09-14 - 2026-09-18: 2.2 Architecture Design Document (Modular Monolith) #arch [100%]",
        "2026-09-21 - 2026-09-25: 2.3 Database Design Document (Schema v2) #database [100%]",
        "",
        "# Phase 2: Implementation (6 Sprints x 14 Days) #implementation",
        "section Sprint 1 - Platform, Identity & Core Data #sprint1",
        "2026-09-14 - 2026-09-16: [1.01] PB08 Design ERD #database [100%]",
        "2026-09-16 - 2026-09-18: [1.02] PB08 Write Supabase migration scripts #database [75%]",
        "2026-09-18 - 2026-09-21: [1.03] PB08 Review & test migrations on clean DB #database [20%]",
        "2026-09-14 - 2026-09-17: [1.04] PB07 Setup GitHub Actions CI/CD #devops [80%]",
        "2026-09-17 - 2026-09-21: [1.05] PB07 Setup auto-deploy to Oracle Cloud VM #devops [60%]",
        "2026-09-18 - 2026-09-21: [1.07] PB29 Confirm Mac access & configure Apple ID #mobile [50%]",
        "2026-09-21 - 2026-09-23: [1.08] PB29 Configure Xcode project + automatic signing #mobile [20%]",
        "2026-09-23 - 2026-09-25: [1.09] PB29 Test build & run app on real iOS device #mobile [0%]",
        "2026-09-21 - 2026-09-23: [1.10] PB01 Backend Supabase Auth integration #backend [40%]",
        "2026-09-21 - 2026-09-24: [1.11] PB01 Mobile Register/Login UI screens #mobile [30%]",
        "2026-09-24 - 2026-09-25: [1.12] PB01 Mobile-Backend integration & error handling #mobile [0%]",
        "2026-09-25 - 2026-09-25: [1.13] PB01 Test unit & widget test #qa [0%]",
        "2026-09-21 - 2026-09-23: [1.14] PB02 Backend consents table + grant/revoke API (PDPL) #backend [30%]",
        "2026-09-23 - 2026-09-25: [1.15] PB02 Mobile purpose-separated consent UI #mobile [0%]",
        "2026-09-25 - 2026-09-25: [1.16] PB02 Test consent flow end-to-end #qa [0%]",
        "2026-09-15 - 2026-09-22: [1.17] PB06 Research/parse Vietnamese Drug Regulatory source #data [50%]",
        "2026-09-21 - 2026-09-25: [1.18] PB06 Build RQ scheduled sync job & Redis queue #backend [10%]",
        "2026-09-22 - 2026-09-25: [1.19] PB41 Draft preliminary DPIA sensitive-data flows #compliance [25%]",
        "milestone 2026-09-27: Sprint 1 Review & Increment 1 Demo #milestone",
        "",
        "section Sprint 2 - Core Reminders & Schedules #sprint2",
        "2026-09-28 - 2026-10-02: PB10 Medication Entry API & Mobile Form #core [0%]",
        "2026-10-01 - 2026-10-06: PB11 Medication Schedule CRUD API & Edit UI #core [0%]",
        "2026-10-05 - 2026-10-09: PB12 Local Reminder Notifications & Offline Engine #core [0%]",
        "2026-10-07 - 2026-10-09: PB13 Dose Confirmation Intake Button & Logging #core [0%]",
        "2026-09-28 - 2026-10-08: PB04/PB05 Admin Catalog Management Web Dashboard #admin [0%]",
        "2026-10-05 - 2026-10-09: PB09 Patient-Family Linking Data Model #database [0%]",
        "milestone 2026-10-11: Sprint 2 Review & Reminder Engine Demo #milestone",
        "",
        "section Sprint 3 - Adherence & Family Connection #sprint3",
        "2026-10-12 - 2026-10-16: PB14 Adherence History Calendar & Summary View #mobile [0%]",
        "2026-10-14 - 2026-10-19: PB15/PB19 Family Linking via QR / Referral Code #feature [0%]",
        "2026-10-16 - 2026-10-21: PB16/PB18 Data-Sharing Consent & Scoped Permissions #compliance [0%]",
        "2026-10-19 - 2026-10-23: PB20 Missed-Dose Real-time Alerts to Caregivers #mobile [0%]",
        "2026-10-21 - 2026-10-23: PB22 Multi-Patient Switcher UI Component #mobile [0%]",
        "milestone 2026-10-25: Sprint 3 Review & Family Caregiver Demo #milestone",
        "",
        "section Sprint 4 - Medical Safety & Drug Lookup #sprint4",
        "2026-10-26 - 2026-10-30: PB23 Vietnamese Drug Regulatory Search & Details #search [0%]",
        "2026-10-28 - 2026-11-03: PB24 Drug-Drug Interaction Warnings with Disclaimers #safety [0%]",
        "2026-11-02 - 2026-11-06: PB25 Drug-Food Interaction Warnings with Disclaimers #safety [0%]",
        "2026-11-04 - 2026-11-06: PB26-PB28 Family Caregiver Interaction Lookups #compliance [0%]",
        "2026-11-05 - 2026-11-06: PB30 Cross-Device Android & iOS Testing #qa [0%]",
        "milestone 2026-11-08: Sprint 4 Review & Drug Safety Demo #milestone",
        "",
        "section Sprint 5 - High-Risk / Complex Features #sprint5",
        "2026-11-09 - 2026-11-13: PB31 On-Device Blister-Pack OCR Text Recognition #ai [0%]",
        "2026-11-12 - 2026-11-17: PB32 OCR Candidate Matching & Manual Confirmation #mobile [0%]",
        "2026-11-16 - 2026-11-19: PB33 Simple Mode High-Contrast UI #ui [0%]",
        "2026-11-16 - 2026-11-20: PB34/PB35 Consent Withdrawal & Deletion Flow #compliance [0%]",
        "2026-11-18 - 2026-11-20: PB36 Sensitive Data Access Audit Log #admin [0%]",
        "milestone 2026-11-22: Sprint 5 Review & OCR / Compliance Demo #milestone",
        "",
        "section Sprint 6 - AI & Final Polish #sprint6",
        "2026-11-23 - 2026-11-27: PB37 AI Meal Suggestions with Medical Disclaimers #ai [0%]",
        "2026-11-26 - 2026-11-30: PB39 Scoped AI Meal Suggestions for Caregivers #ai [0%]",
        "2026-11-26 - 2026-12-01: PB41/PB42 DPIA Final Sign-off & PDPL 2025 Audit #compliance [0%]",
        "2026-11-30 - 2026-12-04: PB43 Full-System Regression Testing & Bug Fixing #qa [0%]",
        "milestone 2026-12-06: Sprint 6 Review & Feature-Complete MVP Sign-off #milestone",
        "",
        "# Phase 3: Integration, Final Release & Defense #phase3",
        "section Integration & Release #release",
        "2026-12-07 - 2026-12-09: 4.1 System Integration & End-to-End User Journey Tests #qa [0%]",
        "2026-12-10 - 2026-12-14: 4.2 Final Submission Package (Code, APK/IPA, Docs, Deployment) #release [0%]",
        "2026-12-14 - 2026-12-16: 4.3 Retrospective & Capstone Defense Demo Rehearsal #defense [0%]",
        "",
        "section Capstone Defense #defense",
        "2026-12-17 - 2026-12-25: 5.1 Capstone Project 1 Final Defense Presentation & Evaluation #defense [0%]",
        "milestone 2026-12-26: Official Project Completion #milestone"
    ]

    with open(mw_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[OK] Generated Markwhen: {mw_path}")

# ==============================================================================
# 5. GENERATE MERMAID GANTT DIAGRAM (.mmd and .md)
# ==============================================================================

def generate_mermaid():
    mmd_path = os.path.join(BASE_DIR, "DrugTime_Gantt_Chart.mmd")
    md_path = os.path.join(BASE_DIR, "DrugTime_Gantt_Chart.md")

    mermaid_content = """gantt
    title DrugTime MVP: Master Schedule & Sprint Backlog Gantt Chart
    dateFormat  YYYY-MM-DD
    axisFormat  %m/%d
    todayMarker stroke-width:2px,stroke:#e53e3e,opacity:0.8

    section Phase 1: Initiation
    1.1 Requirements & Needs       :done, req, 2026-09-10, 2026-09-11
    1.2 Proposal & Budget ($3 998) :done, prop, 2026-09-11, 2026-09-12
    1.3 Proposal Review Approval   :done, mil1, 2026-09-12, 2026-09-13

    section Phase 1: Planning & Design
    2.1 Project Plan & Risk Reg    :done, plan, 2026-09-12, 2026-09-14
    2.2 Architecture Design (C4)   :done, arch, 2026-09-14, 2026-09-18
    2.3 Database Design Schema v2  :done, db,   2026-09-21, 2026-09-25

    section Sprint 1: Platform & Core Data
    1.01 PB08 Design ERD           :done,    s1_1, 2026-09-14, 2026-09-16
    1.02 PB08 Supabase Migrations  :active,  s1_2, 2026-09-16, 2026-09-18
    1.03 PB08 Review Clean DB      :         s1_3, 2026-09-18, 2026-09-21
    1.04 PB07 GitHub Actions CI/CD :active,  s1_4, 2026-09-14, 2026-09-17
    1.05 PB07 Oracle Cloud VM CD   :active,  s1_5, 2026-09-17, 2026-09-21
    1.07 PB29 Mac & Apple ID Setup :active,  s1_7, 2026-09-18, 2026-09-21
    1.08 PB29 Xcode Auto Signing   :         s1_8, 2026-09-21, 2026-09-23
    1.09 PB29 Real iOS Device Test :         s1_9, 2026-09-23, 2026-09-25
    1.10 PB01 Supabase Auth API    :active,  s1_10, 2026-09-21, 2026-09-23
    1.11 PB01 Mobile Login UI      :active,  s1_11, 2026-09-21, 2026-09-24
    1.12 PB01 Auth Integration     :         s1_12, 2026-09-24, 2026-09-25
    1.13 PB01 Auth Unit/Widget Test:         s1_13, 2026-09-25, 2026-09-25
    1.14 PB02 Consent Table & API  :active,  s1_14, 2026-09-21, 2026-09-23
    1.15 PB02 Consent UI Toggles   :         s1_15, 2026-09-23, 2026-09-25
    1.16 PB02 Consent Flow Test    :         s1_16, 2026-09-25, 2026-09-25
    1.17 PB06 VN Drug Data Parse   :active,  s1_17, 2026-09-15, 2026-09-22
    1.18 PB06 RQ Scheduled Sync    :         s1_18, 2026-09-21, 2026-09-25
    1.19 PB41 Preliminary DPIA     :active,  s1_19, 2026-09-22, 2026-09-25

    section Sprint 2: Core Reminders
    PB10 Medication Entry Form/API :         s2_1, 2026-09-28, 2026-10-02
    PB11 Medication Schedule CRUD  :         s2_2, 2026-10-01, 2026-10-06
    PB12 Local Offline Reminders   :crit,    s2_3, 2026-10-05, 2026-10-09
    PB13 Dose Intake Confirmation  :         s2_4, 2026-10-07, 2026-10-09
    PB04/05 Admin Catalog CRUD     :         s2_5, 2026-09-28, 2026-10-08
    PB09 Family Linking Schema     :         s2_6, 2026-10-05, 2026-10-09

    section Sprint 3: Adherence & Family
    PB14 Adherence History & Log   :         s3_1, 2026-10-12, 2026-10-16
    PB15/19 QR Code Family Linking :         s3_2, 2026-10-14, 2026-10-19
    PB16/18 Data-Sharing Consents  :         s3_3, 2026-10-16, 2026-10-21
    PB20 Missed-Dose Push Alerts   :crit,    s3_4, 2026-10-19, 2026-10-23
    PB22 Multi-Patient Switcher UI :         s3_5, 2026-10-21, 2026-10-23

    section Sprint 4: Medical Safety
    PB23 VN Drug Search & Info     :         s4_1, 2026-10-26, 2026-10-30
    PB24 Drug-Drug Interaction Warn:crit,    s4_2, 2026-10-28, 2026-11-03
    PB25 Drug-Food Interaction Warn:         s4_3, 2026-11-02, 2026-11-06
    PB26-28 Caregiver Scoped Lookup:         s4_4, 2026-11-04, 2026-11-06
    PB30 Cross-Device Mobile Test  :         s4_5, 2026-11-05, 2026-11-06

    section Sprint 5: High-Risk Features
    PB31 ML Kit Blister-Pack OCR   :crit,    s5_1, 2026-11-09, 2026-11-13
    PB32 OCR Match & Verify UI     :         s5_2, 2026-11-12, 2026-11-17
    PB33 Simple Mode UI            :         s5_3, 2026-11-16, 2026-11-19
    PB34/35 Consent Deletion Flow  :         s5_4, 2026-11-16, 2026-11-20
    PB36 Sensitive Data Audit Log  :         s5_5, 2026-11-18, 2026-11-20

    section Sprint 6: AI & Polish
    PB37 AI Meal Suggestion Engine :crit,    s6_1, 2026-11-23, 2026-11-27
    PB39 Caregiver Meal Suggestions:         s6_2, 2026-11-26, 2026-11-30
    PB41/42 DPIA Sign-Off & PDPL   :         s6_3, 2026-11-26, 2026-12-01
    PB43 Full-System Bug Fixing    :         s6_4, 2026-11-30, 2026-12-04

    section Phase 3: Integration & Defense
    4.1 End-to-End Testing         :crit,    rel1, 2026-12-07, 2026-12-09
    4.2 Final Submission Packaging :         rel2, 2026-12-10, 2026-12-14
    4.3 Retrospective & Rehearsal  :         rel3, 2026-12-14, 2026-12-16
    5.1 Capstone Final Defense     :crit,    def1, 2026-12-17, 2026-12-25
"""
    with open(mmd_path, "w", encoding="utf-8") as f:
        f.write(mermaid_content)
    print(f"[OK] Generated Mermaid (.mmd): {mmd_path}")

    # Generate Markdown wrapper
    md_content = f"""# DrugTime: Master Gantt Chart & Sprint Roadmap

Project: **DrugTime MVP (Mobile-First Medication Management Platform)**  
Course: **Capstone Project 1 (C1SE.07) - International School, Duy Tan University**  
Timeline: **10-Sep-2026 to 26-Dec-2026 (16 Weeks / 80 Workdays)**  

### Stakeholders & Team
- **Project Sponsor:** International School, Duy Tan University
- **Project Mentor:** Giap Trong Nguyen, Kaopiz Da Nang
- **Project Lead:** Phuc Nguyen Ngoc
- **Project Team:**
  - **Nguyen Ngoc Phuc** - Leader, Dev, QA
  - **Nguyen Quang Bao** - Dev, QA, DevOps
  - **Nguyen Tan Duc** - Dev, QA, DevOps
  - **Nguyen Van Nguyen** - BA, Dev, QA
  - **Dang Ngo Ngoc Viet** - Dev, QA, DevOps

---

## 1. Interactive Frappe Gantt Dashboard
Open [`DrugTime_Gantt_Dashboard.html`](./DrugTime_Gantt_Dashboard.html) in your browser to inspect interactive task zoom, search filters, and progress percentages.

## 2. Excel Gantt Chart
The spreadsheet [`DrugTime_Gantt_Chart.xlsx`](./DrugTime_Gantt_Chart.xlsx) has been formatted following the standard `Activity Template: Gantt Chart` with calendar day tracking, color-coded task bars, and owners.

## 3. Markwhen Timeline
View or edit [`DrugTime_Timeline.mw`](./DrugTime_Timeline.mw) using Markwhen toolchain.

---

## 4. Mermaid Gantt Diagram

```mermaid
{mermaid_content}
```
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"[OK] Generated Markdown (.md): {md_path}")

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
if __name__ == "__main__":
    generate_excel()
    generate_frappe_gantt_html()
    generate_markwhen()
    generate_mermaid()
    print("\n>>> All Gantt artifacts generated successfully! <<<")
