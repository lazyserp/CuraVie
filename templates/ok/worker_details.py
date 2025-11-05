{% extends "base.html.j2" %}
{% block title %}Complete Your Profile - CuraVie{% endblock %}

{% block content %}
<div class="container form-container">
    <div class="card form-card">
        <div class="form-header">
            <h2 data-translate-key="worker_details_title">{{ page_title | default('Complete Your Profile') }}</h2>
            <p data-translate-key="worker_details_subtitle">This information helps us provide accurate health recommendations.</p>
        </div>
        
        <form method="POST" action="" novalidate>
            {{ form.hidden_tag() }}

            <h3 class="form-subheading" data-translate-key="subheading_basic_info">Basic Information</h3>
            <div class="form-group">
                {{ form.first_name.label(class="form-label") }}
                {{ form.first_name(class="form-input", placeholder="Enter your first name", **{'data-translate-key': 'placeholder_first_name'}) }}
                {% for e in form.first_name.errors %}<div class="error">{{ e }}</div>{% endfor %}
            </div>
            <div class="form-group">
                {{ form.last_name.label(class="form-label") }}
                {{ form.last_name(class="form-input", placeholder="Enter your last name", **{'data-translate-key': 'placeholder_last_name'}) }} 
                {% for e in form.last_name.errors %}<div class="error">{{ e }}</div>{% endfor %}
            </div>
            <div class="form-group">
                {{ form.age.label(class="form-label") }}
                {{ form.age(class="form-input", placeholder="Enter your age", **{'data-translate-key': 'placeholder_age'}) }}
                {% for e in form.age.errors %}<div class="error">{{ e }}</div>{% endfor %}
            </div>
            <div class="form-group">
                {{ form.phone.label(class="form-label") }}
                {{ form.phone(class="form-input", placeholder="e.g., +919876543210", **{'data-translate-key': 'placeholder_phone'}) }}
                {% for e in form.phone.errors %}<div class="error">{{ e }}</div>{% endfor %}
            </div>
            <div class="form-group">
                {{ form.home_state.label(class="form-label") }}
                {{ form.home_state(class="form-input", placeholder="e.g., West Bengal, Bihar", **{'data-translate-key': 'placeholder_home_state'}) }}
                {% for e in form.home_state.errors %}<div class="error">{{ e }}</div>{% endfor %}
            </div>
            <div class="form-group">
                {{ form.gender.label(class="form-label") }}
                {{ form.gender(class="form-input") }}
                {% for e in form.gender.errors %}<div class="error">{{ e }}</div>{% endfor %}
            </div>

            <h3 class="form-subheading" data-translate-key="subheading_occupation">Occupational Details</h3>
            <div class="form-group">
                {{ form.occupation.label(class="form-label") }}
                {{ form.occupation(class="form-input") }}
                {% for e in form.occupation.errors %}<div class="error">{{ e }}</div>{% endfor %}
            </div>
            <div class="form-group">
                {{ form.work_hours_per_day.label(class="form-label") }}
                {{ form.work_hours_per_day(class="form-input", placeholder="Enter average hours per day", **{'data-translate-key': 'placeholder_work_hours'}) }}
                {% for e in form.work_hours_per_day.errors %}<div class="error">{{ e }}</div>{% endfor %}
            </div>
            <div class="form-group">
                {{ form.physical_strain.label(class="form-label") }}
                {{ form.physical_strain(class="form-input") }}
                {% for e in form.physical_strain.errors %}<div class="error">{{ e }}</div>{% endfor %}
            </div>
            <div class="form-group">
                {{ form.ppe_usage.label(class="form-label") }}
                {{ form.ppe_usage(class="form-input") }}
                {% for e in form.ppe_usage.errors %}<div class="error">{{ e }}</div>{% endfor %}
            </div>

            <h3 class="form-subheading" data-translate-key="subheading_lifestyle">Lifestyle & Habits</h3>
            <div class="form-group">
                {{ form.smoking_habit.label(class="form-label") }}
                {{ form.smoking_habit(class="form-input") }}
                {% for e in form.smoking_habit.errors %}<div class="error">{{ e }}</div>{% endfor %}
            </div>
            <div class="form-group">
                {{ form.alcohol_consumption.label(class="form-label") }}
                {{ form.alcohol_consumption(class="form-input") }}
                {% for e in form.alcohol_consumption.errors %}<div class="error">{{ e }}</div>{% endfor %}
            </div>
            <div class="form-group">
                {{ form.diet_type.label(class="form-label") }}
                {{ form.diet_type(class="form-input") }}
                {% for e in form.diet_type.errors %}<div class="error">{{ e }}</div>{% endfor %}
            </div>
             <div class="form-group">
                {{ form.meals_per_day.label(class="form-label") }}
                {{ form.meals_per_day(class="form-input", placeholder="e.g., 3", **{'data-translate-key': 'placeholder_meals_per_day'}) }}
                {% for e in form.meals_per_day.errors %}<div class="error">{{ e }}</div>{% endfor %}
            </div>
            <div class="form-group">
                {{ form.junk_food_frequency.label(class="form-label") }}
                {{ form.junk_food_frequency(class="form-input") }}
                {% for e in form.junk_food_frequency.errors %}<div class="error">{{ e }}</div>{% endfor %}
            </div>
            <div class="form-group">
                {{ form.sleep_hours_per_night.label(class="form-label") }}
                {{ form.sleep_hours_per_night(class="form-input", placeholder="e.g., 7", **{'data-translate-key': 'placeholder_sleep_hours'}) }}
                {% for e in form.sleep_hours_per_night.errors %}<div class="error">{{ e }}</div>{% endfor %}
            </div>

            <h3 class="form-subheading" data-translate-key="subheading_living">Living Conditions</h3>
            <div class="form-group">
                {{ form.accommodation_type.label(class="form-label") }}
                {{ form.accommodation_type(class="form-input") }}
                {% for e in form.accommodation_type.errors %}<div class="error">{{ e }}</div>{% endfor %}
            </div>
            <div class="form-group">
                {{ form.sanitation_quality.label(class="form-label") }}
                {{ form.sanitation_quality(class="form-input") }}
                {% for e in form.sanitation_quality.errors %}<div class="error">{{ e }}</div>{% endfor %}
            </div>
            <div class="form-group">
                <div class="checkbox-group">
                    {{ form.access_to_clean_water(class="form-checkbox") }}
                    {{ form.access_to_clean_water.label(class="form-label") }}
                </div>
                {% for e in form.access_to_clean_water.errors %}<div class="error">{{ e }}</div>{% endfor %}
            </div>
            
            <h3 class="form-subheading" data-translate-key="subheading_mental">Mental Well-being</h3>
            <div class="form-group">
                {{ form.stress_level.label(class="form-label") }}
                {{ form.stress_level(class="form-input", placeholder="Enter a number from 1 to 10", **{'data-translate-key': 'placeholder_stress_level'}) }}
                {% for e in form.stress_level.errors %}<div class="error">{{ e }}</div>{% endfor %}
            </div>
            <div class="form-group">
                <div class="checkbox-group">
                    {{ form.has_social_support(class="form-checkbox") }}
                    {{ form.has_social_support.label(class="form-label") }}
                </div>
                {% for e in form.has_social_support.errors %}<div class="error">{{ e }}</div>{% endfor %}
            </div>

            <div class="form-group">
                <button type="submit" class="btn btn-primary btn-full-width" data-translate-key="worker_details_submit_btn">Save Profile</button>
            </div>
        </form>
    </div>
</div>
{% endblock %}