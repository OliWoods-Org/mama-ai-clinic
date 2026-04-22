// MAMA AI Clinic -- Triage assessment flow

const complaintSelect = document.getElementById('complaint');
const symptomDetails = document.getElementById('symptomDetails');
const symptomFields = document.getElementById('symptomFields');

const SYMPTOM_FIELDS = {
    diarrhea: `
        <div class="form-group">
            <label for="duration">Duration (days)</label>
            <input type="number" id="duration" name="duration_days" min="1" max="90" value="1">
        </div>
        <div class="form-group">
            <label><input type="checkbox" name="blood_in_stool"> Blood in stool</label>
        </div>
        <div class="form-group">
            <label><input type="checkbox" name="sunken_eyes"> Sunken eyes</label>
        </div>
        <div class="form-group">
            <label for="skinPinch">Skin pinch</label>
            <select id="skinPinch" name="skin_pinch">
                <option value="instant">Goes back immediately</option>
                <option value="slow">Goes back slowly</option>
                <option value="very_slow">Goes back very slowly</option>
            </select>
        </div>
        <div class="form-group">
            <label for="drinking">Drinking</label>
            <select id="drinking" name="drinking">
                <option value="normal">Drinks normally</option>
                <option value="eager">Drinks eagerly / thirsty</option>
                <option value="not_able">Not able to drink</option>
            </select>
        </div>
        <div class="form-group">
            <label><input type="checkbox" name="restless_irritable"> Restless or irritable</label>
        </div>
        <div class="form-group">
            <label><input type="checkbox" name="lethargic"> Lethargic</label>
        </div>
    `,
    cough: `
        <div class="form-group">
            <label for="duration">Duration (days)</label>
            <input type="number" id="duration" name="duration_days" min="1" max="90" value="1">
        </div>
        <div class="form-group">
            <label for="breathingRate">Breathing rate (per minute)</label>
            <input type="number" id="breathingRate" name="breathing_rate" min="10" max="100" value="30">
        </div>
        <div class="form-group">
            <label><input type="checkbox" name="chest_indrawing"> Chest indrawing</label>
        </div>
        <div class="form-group">
            <label><input type="checkbox" name="stridor_at_rest"> Stridor when calm</label>
        </div>
    `,
    fever: `
        <div class="form-group">
            <label for="temperature">Temperature (C)</label>
            <input type="number" id="temperature" name="temperature_c" min="35" max="42" step="0.1" value="38.0">
        </div>
        <div class="form-group">
            <label for="duration">Duration (days)</label>
            <input type="number" id="duration" name="duration_days" min="1" max="90" value="1">
        </div>
        <div class="form-group">
            <label><input type="checkbox" name="stiff_neck"> Stiff neck</label>
        </div>
        <div class="form-group">
            <label><input type="checkbox" name="malaria_risk"> Malaria risk area</label>
        </div>
        <div class="form-group" id="rdtGroup" style="display: none;">
            <label for="rdtResult">RDT Result</label>
            <select id="rdtResult" name="rdt_result">
                <option value="">Not done</option>
                <option value="positive">Positive</option>
                <option value="negative">Negative</option>
            </select>
        </div>
    `,
};

complaintSelect.addEventListener('change', () => {
    const complaint = complaintSelect.value;
    if (SYMPTOM_FIELDS[complaint]) {
        symptomFields.innerHTML = SYMPTOM_FIELDS[complaint];
        symptomDetails.style.display = 'block';

        // Show RDT field when malaria risk is checked
        const malariaCheck = document.querySelector('[name="malaria_risk"]');
        if (malariaCheck) {
            malariaCheck.addEventListener('change', () => {
                const rdtGroup = document.getElementById('rdtGroup');
                if (rdtGroup) rdtGroup.style.display = malariaCheck.checked ? 'block' : 'none';
            });
        }
    } else {
        symptomDetails.style.display = 'none';
    }
});

document.getElementById('triageForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const btn = document.getElementById('assessBtn');
    btn.disabled = true;
    btn.textContent = 'Assessing...';

    // Collect danger signs
    const dangerSigns = Array.from(document.querySelectorAll('[name="danger_signs"]:checked'))
        .map(cb => cb.value);

    // Collect symptoms
    const complaint = complaintSelect.value;
    const symptoms = {};

    const numFields = symptomDetails.querySelectorAll('input[type="number"]');
    numFields.forEach(f => { symptoms[f.name] = parseFloat(f.value); });

    const checkboxes = symptomDetails.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(cb => { symptoms[cb.name] = cb.checked; });

    const selects = symptomDetails.querySelectorAll('select');
    selects.forEach(s => { if (s.value) symptoms[s.name] = s.value; });

    const payload = {
        age_group: document.getElementById('ageGroup').value,
        danger_signs: dangerSigns,
        chief_complaint: complaint,
        symptoms: symptoms,
    };

    try {
        const resp = await fetch('/triage/assess', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const data = await resp.json();
        showResults(data);
    } catch (err) {
        alert('Error: Could not reach the assessment server. Check system status.');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Assess Patient';
    }
});

function showResults(data) {
    const resultsDiv = document.getElementById('results');
    const classBox = document.getElementById('classificationBox');
    const explBox = document.getElementById('explanationBox');
    const explText = document.getElementById('explanationText');

    const c = data.classification;
    const color = (c.color || c.classification || '').toLowerCase();
    const colorClass = color === 'red' ? 'classification-red'
        : color === 'yellow' ? 'classification-yellow'
        : 'classification-green';

    classBox.className = colorClass;
    classBox.innerHTML = `
        <div class="classification-label">${c.classification || 'ASSESSMENT'}</div>
        <div style="font-size: 13px; margin-top: 4px;">
            ${(c.actions || []).map(a => `<div style="margin: 4px 0;">- ${a}</div>`).join('')}
        </div>
    `;

    if (data.explanation) {
        explText.textContent = data.explanation;
        explBox.style.display = 'block';
    }

    resultsDiv.style.display = 'block';
    resultsDiv.scrollIntoView({ behavior: 'smooth' });
}
