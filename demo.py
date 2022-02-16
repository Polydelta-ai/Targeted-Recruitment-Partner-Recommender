import engine

user_input = {
    'demographics': ['black'],
    
    'candidate_type': {
        'student': True,
        'professional': True,
        },
    
    'states': ['GA','CA','TX'],
    
    'majors': ['biology', 'chemistry'],
    
    'keywords': ['wildlife'],
    
    'school_examples': [
        'Bennett College', 
        'California State University-Bakersfield'
        ],

    'organization_examples': ['the wildlife society'],
}

engine.generate_recommendations(user_input)
