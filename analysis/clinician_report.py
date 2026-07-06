import sqlite3
import json
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import inch
from io import BytesIO
from .trend_analysis import get_session_history, compute_trends, generate_progression_report

DB_PATH = 'sessions.db'

def get_all_patients():
    with sqlite3.connect(DB_PATH) as con:
        rows = con.execute('''
            SELECT job_id, created_at, mode, result_json
            FROM sessions ORDER BY created_at DESC
        ''').fetchall()

    patients = {}
    for r in rows:
        try:
            result = json.loads(r[3])
            mode = r[2]
            patient_key = 'default_patient'
            if patient_key not in patients:
                patients[patient_key] = []
            patients[patient_key].append({
                'job_id': r[0],
                'created_at': r[1],
                'mode': mode,
                'result': result
            })
        except (json.JSONDecodeError, TypeError):
            continue
    return patients

def get_patient_summary(patient_id='default_patient'):
    sessions = get_session_history(db_path=DB_PATH)
    if not sessions:
        return None

    standing_no_brace = [s for s in sessions if 'standing' in s['mode'] and 'no_brace' in s['mode']]
    standing_with_brace = [s for s in sessions if 'standing' in s['mode'] and 'with_brace' in s['mode']]

    latest_no_brace = standing_no_brace[0] if standing_no_brace else None
    latest_with_brace = standing_with_brace[0] if standing_with_brace else None

    brace_effectiveness = None
    if latest_no_brace and latest_with_brace:
        no_brace_angle = latest_no_brace['metrics'].get('trunk_lean_angle', 0)
        with_brace_angle = latest_with_brace['metrics'].get('trunk_lean_angle', 0)
        if no_brace_angle > 0:
            correction_pct = ((no_brace_angle - with_brace_angle) / no_brace_angle) * 100
            brace_effectiveness = {
                'correction_percentage': round(correction_pct, 1),
                'without_brace_angle': no_brace_angle,
                'with_brace_angle': with_brace_angle,
                'absolute_correction': round(no_brace_angle - with_brace_angle, 2)
            }

    trends = compute_trends(sessions)

    return {
        'patient_id': patient_id,
        'total_sessions': len(sessions),
        'last_session_date': sessions[0]['created_at'] if sessions else None,
        'brace_effectiveness': brace_effectiveness,
        'trends': trends,
        'session_summary': {
            'standing_no_brace': len(standing_no_brace),
            'standing_with_brace': len(standing_with_brace),
            'walking': len([s for s in sessions if 'walking' in s['mode']]),
            'exercise': len([s for s in sessions if 'exercise' in s['mode']])
        }
    }

def generate_pdf_report(patient_id='default_patient'):
    report_data = generate_progression_report(patient_id, db_path=DB_PATH)
    summary = get_patient_summary(patient_id)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=6)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, spaceAfter=4, textColor=colors.HexColor('#1e40af'))
    body_style = ParagraphStyle('CustomBody', parent=styles['Normal'], fontSize=10, spaceAfter=4)
    small_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=8, textColor=colors.grey)

    elements.append(Paragraph('Scoliosis Brace Monitoring Report', title_style))
    elements.append(Paragraph(f'Generated: {datetime.now().strftime("%B %d, %Y at %H:%M")}', small_style))
    elements.append(Paragraph(f'Patient: {patient_id}', small_style))
    elements.append(Paragraph('Created by Srinath Sankara', small_style))
    elements.append(Spacer(1, 8))

    disclaimer_style = ParagraphStyle('Disclaimer', parent=styles['Normal'], fontSize=7, textColor=colors.HexColor('#991b1b'), spaceAfter=4)
    elements.append(Paragraph(
        '<b>Medical Disclaimer:</b> This report is for educational and monitoring purposes only. '
        'It is not a medical device and does not provide medical diagnosis or treatment recommendations. '
        'The metrics are estimates based on computer vision analysis and should not be used as a substitute '
        'for professional medical assessment. Always consult a qualified healthcare provider for clinical decisions. '
        'The author assumes no responsibility for any decisions made based on this report.',
        disclaimer_style
    ))
    elements.append(Spacer(1, 4))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3b82f6')))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph('Session Summary', heading_style))
    if summary:
        summary_data = [
            ['Total Sessions', str(summary['total_sessions'])],
            ['Last Session', summary.get('last_session_date', 'N/A')],
            ['Standing (No Brace)', str(summary['session_summary']['standing_no_brace'])],
            ['Standing (With Brace)', str(summary['session_summary']['standing_with_brace'])],
            ['Walking Sessions', str(summary['session_summary']['walking'])],
            ['Exercise Sessions', str(summary['session_summary']['exercise'])]
        ]
        t = Table(summary_data, colWidths=[2.5*inch, 3.5*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 6)
        ]))
        elements.append(t)
    elements.append(Spacer(1, 12))

    if summary and summary.get('brace_effectiveness'):
        elements.append(Paragraph('Brace Effectiveness', heading_style))
        be = summary['brace_effectiveness']
        be_data = [
            ['Metric', 'Value'],
            ['Without Brace Angle', f"{be['without_brace_angle']}°"],
            ['With Brace Angle', f"{be['with_brace_angle']}°"],
            ['Absolute Correction', f"{be['absolute_correction']}°"],
            ['Correction Percentage', f"{be['correction_percentage']}%"]
        ]
        t = Table(be_data, colWidths=[3*inch, 3*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 6)
        ]))
        elements.append(t)
    elements.append(Spacer(1, 12))

    if report_data.get('status') == 'analyzed' and report_data.get('trends', {}).get('trends'):
        elements.append(Paragraph('Longitudinal Trends', heading_style))
        trend_data = [['Metric', 'Direction', 'Total Change', 'Sessions', 'Risk']]
        for metric, trend in report_data['trends']['trends'].items():
            risk = 'High' if abs(trend['total_change']) > 5 else 'Moderate' if abs(trend['total_change']) > 2 else 'Low'
            trend_data.append([
                metric.replace('_', ' ').title(),
                trend['direction'].title(),
                f"{trend['total_change']:+.1f}",
                str(trend['session_count']),
                risk
            ])
        t = Table(trend_data, colWidths=[1.8*inch, 1.2*inch, 1.2*inch, 1*inch, 1*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('PADDING', (0, 0), (-1, -1), 5)
        ]))
        elements.append(t)
    elements.append(Spacer(1, 12))

    if report_data.get('alerts'):
        elements.append(Paragraph('Alerts', heading_style))
        for alert in report_data['alerts']:
            color = colors.red if alert['level'] == 'critical' else colors.orange
            alert_style = ParagraphStyle('Alert', parent=styles['Normal'], fontSize=10, textColor=color, spaceAfter=4)
            elements.append(Paragraph(f"[{alert['level'].upper()}] {alert['message']}", alert_style))
        elements.append(Spacer(1, 8))

    if report_data.get('recommendations'):
        elements.append(Paragraph('Recommendations', heading_style))
        for rec in report_data['recommendations']:
            elements.append(Paragraph(f"\u2022 {rec}", body_style))
        elements.append(Spacer(1, 12))

    elements.append(Paragraph('Treatment Rationale: Bracing & Physical Therapy to Prevent Surgery', heading_style))
    elements.append(Paragraph(
        'Adolescent Idiopathic Scoliosis (AIS) affects 2-3% of adolescents. When detected early, '
        'the combination of bracing and scoliosis-specific physical therapy (Schroth method) can '
        'prevent curve progression and avoid spinal fusion surgery in up to 72% of cases (BrAIST study, NEJM 2013).',
        body_style
    ))
    elements.append(Spacer(1, 6))

    rationale_data = [
        ['Treatment Component', 'Evidence-Based Outcome'],
        ['Bracing (13+ hrs/day)', '72% reduction in surgery risk (BrAIST). Higher compliance = better outcomes.'],
        ['Schroth PSSE', 'Recommended over traditional PT (SOSORT 2025). Retrains postural habits, strengthens concave-side muscles.'],
        ['Brace + Schroth Combined', 'Brace holds correction; Schroth strengthens muscles to maintain it. Synergistic effect exceeds individual treatments.'],
        ['Smart Brace Monitoring', 'Pressure data verifies corrective force at curve apex. Objective compliance tracking.'],
        ['Cost Comparison', 'Bracing + PT: $5K-$15K vs. Spinal Fusion Surgery: $100K-$300K. Fraction of the cost with full mobility preserved.']
    ]
    t = Table(rationale_data, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#ecfdf5')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    elements.append(t)
    elements.append(Spacer(1, 8))

    if summary and summary.get('brace_effectiveness'):
        be = summary['brace_effectiveness']
        if be['correction_percentage'] > 0:
            elements.append(Paragraph(
                f"This patient's brace is achieving {be['correction_percentage']}% correction "
                f"({be['absolute_correction']} degree improvement). "
                + ("This indicates the brace is effectively applying corrective force, supporting the non-surgical treatment plan."
                   if be['correction_percentage'] > 20
                   else "Consider brace adjustment to improve corrective force delivery."),
                body_style
            ))
    elements.append(Spacer(1, 12))

    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        'This report is generated by Scoliosis Brace Coach AI (created by Srinath Sankara). '
        'It is for educational and monitoring purposes only and is not a medical device. '
        'For clinical decisions, always consult a qualified healthcare provider. '
        'The author assumes no responsibility for medical decisions made based on this report.',
        small_style
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
