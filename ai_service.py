import ollama
from models import Worker
import logging
import os

# Configure basic logging
logging.basicConfig(level=logging.INFO)

def generate_health_report(worker):
    if not worker:
        return None

    profile_data = f"""
    - Age: {worker.age}
    - Gender: {worker.gender.value if worker.gender else 'N/A'}
    - Home State: {worker.home_state}
    - Occupation: {worker.occupation.value if worker.occupation else 'N/A'}
    - Average Daily Work Hours: {worker.work_hours_per_day}
    - Physical Strain of Job: {worker.physical_strain.value if worker.physical_strain else 'N/A'}
    - Use of Safety Gear (PPE): {worker.ppe_usage.value if worker.ppe_usage else 'N/A'}
    - Smoking Habit: {worker.smoking_habit.value if worker.smoking_habit else 'N/A'}
    - Alcohol Consumption: {worker.alcohol_consumption.value if worker.alcohol_consumption else 'N/A'}
    - Diet Type: {worker.diet_type.value if worker.diet_type else 'N/A'}
    - Meals Per Day: {worker.meals_per_day}
    - Junk Food Frequency: {worker.junk_food_frequency.value if worker.junk_food_frequency else 'N/A'}
    - Average Nightly Sleep: {worker.sleep_hours_per_night} hours
    - Living Accommodation: {worker.accommodation_type.value if worker.accommodation_type else 'N/A'}
    - Sanitation Quality: {worker.sanitation_quality.value if worker.sanitation_quality else 'N/A'}
    - Chronic Diseases: {worker.chronic_diseases if worker.chronic_diseases else 'None reported'}
    - Stress Level (1-10): {worker.stress_level}
    """


    prompt = f"""
    **Role and Goal:** You are a public health expert analyzing the health profile of a migrant worker in Kerala, India. Your goal is to provide a clear, empathetic, and actionable health risk assessment. The language should be simple and easy to understand.

    **Worker's Profile Data:**
    {profile_data}

    **Task:** Based on the worker's profile, generate a health report with the following structure:

    1.  **Overall Health Summary:** A brief, 2-3 sentence paragraph summarizing the worker's current health status based on the provided data.
    
    2.  **Key Health Risks:** Identify the top 3-5 potential health risks. For each risk, briefly explain *why* it's a risk based on their specific lifestyle, occupation, and living conditions. For example, connect 'Construction' work and 'Heavy Lifting' to musculoskeletal issues.

    3.  **Personalized Recommendations:** Provide a bulleted list of simple, low-cost, and actionable recommendations. Categorize them into:
        - **Diet & Nutrition:** (e.g., "Try to include one local fruit each day...")
        - **Lifestyle Changes:** (e.g., "Simple stretching for 10 minutes before work can help...")
        - **Preventive Actions:** (e.g., "Ensure you are drinking clean water...")

    **Format:** Please use clear headings for each section. Use bullet points for lists. Do not add any introductory or concluding text outside of this structure.
    """

    try:
        logging.info("Sending prompt to Ollama...")
        response = ollama.chat(
            model= os.getenv("OLLAMA_MODEL"),
            messages=[{'role': 'user', 'content': prompt}]
        )
        logging.info("Received response from Ollama.")
        return response['message']['content']
    except Exception as e:
        logging.error(f"Error communicating with Ollama: {e}")
        return "Error: Could not generate the health report. Please ensure the AI service is running and accessible."