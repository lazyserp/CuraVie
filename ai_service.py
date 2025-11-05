import ollama
from models import Worker, MedicalCheckup, LabResults, DoctorEvaluation, Vaccination, MedicalVisit
import logging
import os
from datetime import datetime

# Configure basic logging
logging.basicConfig(level=logging.INFO)

def _safe(v, default='N/A'):
    return v if v not in (None, "", []) else default


def _enum(v):
    return v.value if v else None


def _format_date(d):
    if not d:
        return None
    if isinstance(d, datetime):
        return d.strftime('%Y-%m-%d')
    try:
        return d.isoformat()
    except Exception:
        return str(d)


def generate_health_report(worker: Worker):
    if not worker:
        return "Error: Worker not found."

    # Latest medical checkup with labs and evaluation
    latest_checkup: MedicalCheckup | None = None
    if hasattr(worker, 'medical_checkups') and worker.medical_checkups:
        latest_checkup = sorted(worker.medical_checkups, key=lambda c: (c.date_of_checkup or datetime.min), reverse=True)[0]

    lab: LabResults | None = latest_checkup.lab_results if latest_checkup else None
    ev: DoctorEvaluation | None = latest_checkup.doctor_evaluation if latest_checkup else None

    # Recent vaccinations (last 3)
    vaccinations = []
    if hasattr(worker, 'vaccinations') and worker.vaccinations:
        vaccinations = sorted(worker.vaccinations, key=lambda v: (v.date_administered or datetime.min), reverse=True)[:3]

    # Recent medical visits (last 3)
    visits = []
    if hasattr(worker, 'medical_visits') and worker.medical_visits:
        visits = sorted(worker.medical_visits, key=lambda v: (v.visit_date or datetime.min), reverse=True)[:3]

    profile_data = f"""
    - Full Name: {_safe(f"{_safe(worker.first_name, '')} {_safe(worker.last_name, '')}".strip())}
    - Age: {_safe(worker.age)}
    - Date of Birth: {_safe(_format_date(getattr(worker, 'date_of_birth', None)))}
    - Gender: {_safe(_enum(worker.gender))}
    - Nationality: {_safe(getattr(worker, 'nationality', None))}
    - Home State: {_safe(worker.home_state)}
    - Occupation: {_safe(_enum(worker.occupation))}
    - Employer: {_safe(getattr(worker, 'employer_name', None))}
    - Work Location: {_safe(getattr(worker, 'work_location', None))}
    - Average Daily Work Hours: {_safe(worker.work_hours_per_day)}
    - Physical Strain of Job: {_safe(_enum(worker.physical_strain))}
    - PPE Usage: {_safe(_enum(worker.ppe_usage))}
    - Smoking Habit: {_safe(_enum(worker.smoking_habit))}
    - Alcohol Consumption: {_safe(_enum(worker.alcohol_consumption))}
    - Diet Type: {_safe(_enum(worker.diet_type))}
    - Meals Per Day: {_safe(worker.meals_per_day)}
    - Junk Food Frequency: {_safe(_enum(worker.junk_food_frequency))}
    - Sleep Hours/Night: {_safe(worker.sleep_hours_per_night)}
    - Accommodation Type: {_safe(_enum(worker.accommodation_type))}
    - Sanitation Quality: {_safe(_enum(worker.sanitation_quality))}
    - Chronic Diseases: {_safe(_enum(getattr(worker, 'chronic_diseases', None)) or getattr(worker, 'chronic_diseases', None))}
    - Stress Level (1-10): {_safe(worker.stress_level)}
    """

    checkup_data = "No medical checkup on record."
    if latest_checkup:
        checkup_data = f"""
        - Date of Checkup: {_safe(_format_date(latest_checkup.date_of_checkup))}
        - Height (cm): {_safe(latest_checkup.height_cm)}
        - Weight (kg): {_safe(latest_checkup.weight_kg)}
        - BMI: {_safe(latest_checkup.bmi)}
        - BP: {_safe(latest_checkup.blood_pressure_systolic)}/{_safe(latest_checkup.blood_pressure_diastolic)} mmHg
        - Pulse (bpm): {_safe(latest_checkup.pulse_rate)}
        - Temperature (°C): {_safe(latest_checkup.temperature_celsius)}
        - Vision (L/R): {_safe(latest_checkup.vision_left)}/{_safe(latest_checkup.vision_right)}
        - Hearing: {_safe(_enum(latest_checkup.hearing_test_result))}
        - Respiratory Rate: {_safe(latest_checkup.respiratory_rate)}
        - SpO2 (%): {_safe(latest_checkup.oxygen_saturation)}
        - Checkup Type: {_safe(_enum(latest_checkup.checkup_type))}
        - Geo Location: {_safe(latest_checkup.geo_location)}
        - Risk Category: {_safe(getattr(latest_checkup, 'risk_category', None))}
        - Disease Prediction Score: {_safe(getattr(latest_checkup, 'disease_prediction_score', None))}
        """

    lab_data = "No lab results available."
    if lab:
        lab_data = f"""
        - Hemoglobin (g/dL): {_safe(lab.hemoglobin_g_dl)}
        - Sugar (F/PP mg/dL): {_safe(lab.blood_sugar_fasting)} / {_safe(lab.blood_sugar_postprandial)}
        - Lipids (Total/Trig/HDL/LDL): {_safe(lab.cholesterol_total)} / {_safe(lab.triglycerides)} / {_safe(lab.hdl_cholesterol)} / {_safe(lab.ldl_cholesterol)}
        - HIV: {_safe(_enum(lab.hiv_test_result))}
        - Hepatitis B: {_safe(_enum(lab.hepatitis_b_result))}
        - Hepatitis C: {_safe(_enum(lab.hepatitis_c_result))}
        - TB Screening: {_safe(_enum(lab.tuberculosis_screening_result))}
        - Malaria: {_safe(_enum(lab.malaria_test_result))}
        - Urine Test: {_safe(_enum(lab.urine_test_result))}
        - Chest X-ray: {_safe(_enum(lab.xray_chest_result))}
        - ECG: {_safe(_enum(lab.ecg_result))}
        """

    eval_data = "No doctor evaluation available."
    if ev:
        eval_data = f"""
        - Doctor: {_safe(ev.doctor_name)} (Reg: {_safe(ev.doctor_registration_number)})
        - Findings: {_safe(ev.general_physical_findings)}
        - Diagnosis: {_safe(ev.diagnosis)}
        - Recommendations: {_safe(ev.recommendations)}
        - Fitness Status: {_safe(_enum(ev.fitness_status))}
        - Follow-up Required: {_safe('Yes' if ev.follow_up_required else ('No' if ev.follow_up_required is not None else None))}
        - Follow-up Date: {_safe(_format_date(ev.follow_up_date))}
        - Report Generated By: {_safe(ev.report_generated_by)} on {_safe(_format_date(getattr(ev, 'report_generated_on', None)))}
        - Verified By: {_safe(ev.report_verified_by)}
        - Remarks: {_safe(ev.remarks)}
        """

    vacc_lines = [f"- {v.vaccine_name} (Dose {v.dose_number}) on {_safe(_format_date(v.date_administered))}" for v in vaccinations] or ["- None"]
    visit_lines = [f"- {v.visit_date}: {_safe(v.doctor_name)} @ facility {_safe(v.facility_id)} — {_safe(v.diagnosis)}" for v in visits] or ["- None"]

    prompt = f"""
    Role: You are a public health expert analyzing a migrant worker's health in Kerala, India. Provide a clear, empathetic, and actionable assessment in simple language.

    Worker Profile:
    {profile_data}

    Latest Medical Checkup:
    {checkup_data}

    Laboratory Results:
    {lab_data}

    Doctor Evaluation:
    {eval_data}

    Recent Vaccinations (up to 3):
    {chr(10).join(vacc_lines)}

    Recent Medical Visits (up to 3):
    {chr(10).join(visit_lines)}

    Task: Using all the above, produce the following strictly structured output:
    1. Overall Health Summary (2-4 sentences)
    2. Key Health Risks (3-6 bullets). For each, explain WHY based on the data.
    3. Personalized Recommendations
       - Diet & Nutrition (4-6 bullets)
       - Lifestyle Changes (4-6 bullets)
       - Preventive Actions (4-6 bullets)
    4. Follow-up Plan (if any), including timelines and what to monitor
    5. Flags for Immediate Medical Attention (if any)

    Rules:
    - Be concise and practical. Use bullet points.
    - Do not invent data; if a field is N/A, skip it.
    - Avoid markdown bold markers (**) in the response.
    """

    try:
        model_name = os.getenv("OLLAMA_MODEL", "llama3")
        logging.info("Sending prompt to Ollama...")
        response = ollama.chat(
            model=model_name,
            messages=[{'role': 'user', 'content': prompt}]
        )
        logging.info("Received response from Ollama.")
        return response['message']['content']
    except Exception as e:
        logging.error(f"Error communicating with Ollama: {e}")
        return "Error: Could not generate the health report. Please ensure the AI service is running and accessible."