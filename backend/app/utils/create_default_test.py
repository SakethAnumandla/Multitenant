"""
Script to create default Nutrition & Lifestyle Profile test with questions
"""
from app.database import db
from app.models.test import Test, Question

def create_default_test(tenant_id):
    """Create default Nutrition & Lifestyle Profile test"""
    
    # Create test
    test = Test(
        tenant_id=tenant_id,
        title="Nutrition & Lifestyle Profile",
        description="Comprehensive questionnaire to assess nutritional habits and lifestyle factors",
        is_active=True
    )
    
    db.session.add(test)
    db.session.flush()  # Get test.id
    
    # Define questions based on the provided questionnaire
    # Exact match with user's specification
    questions_data = [
        # Section A: Dietary Overview
        {
            'question_text': 'Typical daily diet (breakfast-lunch-dinner pattern):',
            'question_type': 'textarea',
            'section': 'Section A: Dietary Overview',
            'priority_order': 1
        },
        {
            'question_text': 'Protein intake (meat, eggs, legumes, dairy frequency):',
            'question_type': 'textarea',
            'section': 'Section A: Dietary Overview',
            'priority_order': 2
        },
        {
            'question_text': 'Vegetable & fruit intake:',
            'question_type': 'radio',
            'section': 'Section A: Dietary Overview',
            'options': ['Rare', '1–2 servings', '3–4', '5+'],
            'priority_order': 3
        },
        {
            'question_text': 'Water intake per day:',
            'question_type': 'radio',
            'section': 'Section A: Dietary Overview',
            'options': ['less', '1-3L/day', '2-4 L/day', 'more than 5L/ day'],
            'priority_order': 4
        },
        {
            'question_text': 'Caffeine/ Tea intake:',
            'question_type': 'radio',
            'section': 'Section A: Dietary Overview',
            'options': ['None', '1–2 cups', '3+ cups'],
            'priority_order': 5
        },
        {
            'question_text': 'Sugar consumption:',
            'question_type': 'radio',
            'section': 'Section A: Dietary Overview',
            'options': ['Low', 'Moderate', 'High'],
            'priority_order': 6
        },
        {
            'question_text': 'Alcohol',
            'question_type': 'radio',
            'section': 'Section A: Dietary Overview',
            'options': ['yes', 'occasionally', 'social drinker', 'no'],
            'priority_order': 7
        },
        {
            'question_text': 'smoking:',
            'question_type': 'radio',
            'section': 'Section A: Dietary Overview',
            'options': ['Yes', 'No'],
            'priority_order': 8
        },
        
        # Section B: Nutritional Red Flags
        {
            'question_text': 'Any recent weight loss or dieting?',
            'question_type': 'textarea',
            'section': 'Section B: Nutritional Red Flags',
            'priority_order': 9
        },
        {
            'question_text': 'Skipped meals or fasting practices?',
            'question_type': 'textarea',
            'section': 'Section B: Nutritional Red Flags',
            'priority_order': 10
        },
        {
            'question_text': 'Known deficiencies:',
            'question_type': 'checkbox',
            'section': 'Section B: Nutritional Red Flags',
            'options': ['Iron', 'B12', 'Vitamin D', 'Zinc', 'None'],
            'priority_order': 11
        },
        {
            'question_text': 'Any digestive issues:',
            'question_type': 'checkbox',
            'section': 'Section B: Nutritional Red Flags',
            'options': ['Bloating', 'Constipation', 'Low appetite', 'None'],
            'priority_order': 12
        },
        
        # Section C: Hormonal & Lifestyle Factors
        {
            'question_text': 'For females:',
            'question_type': 'radio',
            'section': 'Section C: Hormonal & Lifestyle Factors',
            'options': ['Regular cycles', 'Irregular', 'PCOS', 'Postpartum', 'Perimenopause', 'not relevant'],
            'priority_order': 13
        },
        {
            'question_text': 'For males: Any recent drop in stamina, libido, or energy?',
            'question_type': 'radio',
            'section': 'Section C: Hormonal & Lifestyle Factors',
            'options': ['yes', 'no', 'not relevant'],
            'priority_order': 14
        },
        {
            'question_text': 'Sleep quality:',
            'question_type': 'radio',
            'section': 'Section C: Hormonal & Lifestyle Factors',
            'options': ['Restful', 'Disturbed', 'Insomnia'],
            'priority_order': 15
        },
        {
            'question_text': 'Exercise frequency:',
            'question_type': 'radio',
            'section': 'Section C: Hormonal & Lifestyle Factors',
            'options': ['Rare', '1–2x/week', '3–5x/week', 'Daily'],
            'priority_order': 16
        },
        
        # Section D: Supplement & Product Use
        {
            'question_text': 'Any supplements? (Biotin, collagen, iron, etc.)',
            'question_type': 'textarea',
            'section': 'Section D: Supplement & Product Use',
            'priority_order': 17
        },
        {
            'question_text': 'Any ongoing medications that could cause shedding (antidepressants, contraceptives, etc.)?',
            'question_type': 'textarea',
            'section': 'Section D: Supplement & Product Use',
            'priority_order': 18
        },
    ]
    
    # Create questions
    for q_data in questions_data:
        question = Question(
            test_id=test.id,
            question_text=q_data['question_text'],
            question_type=q_data['question_type'],
            section=q_data.get('section'),
            options=q_data.get('options'),
            default_order=q_data['priority_order'],
            priority_order=q_data['priority_order'],
            is_required=True
        )
        db.session.add(question)
    
    db.session.commit()
    return test

