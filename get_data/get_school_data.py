import requests
import json
import time
from config import api_key

API_KEY = api_key
BASE_URL = 'https://api.data.gov/ed/collegescorecard/v1/schools?api_key='

filter_on = '&school.degrees_awarded.highest=3,4&' #filtering on tertiary education only
# These fields are 2019-2020 academic year

fields = [
    'school.name',
    'school.city', 
    'school.state',
    'school.school_url', 
    'school.main_campus', 
    'school.ownership']
    
YEAR='2019.'
year_specific_fields = [ 
    # 'school.minority_serving.historically_black', 
# 'school.minority_serving.predominantly_black', 
# 'school.minority_serving.annh',  
# 'school.minority_serving.tribal', 
# 'school.minority_serving.aanipi', 
# 'school.minority_serving.hispanic',
# 'school.minority_serving.nant', 
# 'school.men_only, school.women_only', 
'admissions.admission_rate.overall',
'student.size',
'academics.program_percentage.agriculture',
'academics.program_percentage.resources',
'academics.program_percentage.architecture',
'academics.program_percentage.ethnic_cultural_gender',
'academics.program_percentage.communication',
'academics.program_percentage.communications_technology',
'academics.program_percentage.computer',
'academics.program_percentage.personal_culinary',
'academics.program_percentage.education',
'academics.program_percentage.engineering',
'academics.program_percentage.engineering_technology',
'academics.program_percentage.language',
'academics.program_percentage.family_consumer_science',
'academics.program_percentage.legal',
'academics.program_percentage.english',
'academics.program_percentage.humanities',
'academics.program_percentage.library',
'academics.program_percentage.biological',
'academics.program_percentage.mathematics',
'academics.program_percentage.military',
'academics.program_percentage.multidiscipline',
'academics.program_percentage.parks_recreation_fitness',
'academics.program_percentage.philosophy_religious',
'academics.program_percentage.theology_religious_vocation',
'academics.program_percentage.physical_science',
'academics.program_percentage.science_technology',
'academics.program_percentage.psychology',
'academics.program_percentage.security_law_enforcement',
'academics.program_percentage.public_administration_social_service',
'academics.program_percentage.social_science',
'academics.program_percentage.construction',
'academics.program_percentage.mechanic_repair_technology',
'academics.program_percentage.precision_production',
'academics.program_percentage.transportation',
'academics.program_percentage.visual_performing',
'academics.program_percentage.health',
'academics.program_percentage.business_marketing',
'academics.program_percentage.history',
'2019.student.demographics.race_ethnicity.white',
'student.demographics.race_ethnicity.black',
'student.demographics.race_ethnicity.hispanic',
'student.demographics.race_ethnicity.asian',
'student.demographics.race_ethnicity.aian',
'student.demographics.race_ethnicity.nhpi',
'student.demographics.race_ethnicity.two_or_more',
'student.demographics.race_ethnicity.non_resident_alien',
'student.demographics.race_ethnicity.unknown',
'student.demographics.race_ethnicity.white_non_hispanic',
'student.demographics.race_ethnicity.black_non_hispanic',
'student.demographics.race_ethnicity.asian_pacific_islander',
]
year_specific_fields = [YEAR+i for i in year_specific_fields]

TOTAL_PAGE = 2706 #Get from running query once to see number.
start = time.time()
for page in range(TOTAL_PAGE):
    page_start = time.time()
    query = filter_on+'fields='+ ','.join(fields+year_specific_fields)+'&page='+str(page)

    #print(BASE_URL+API_KEY+query)
    response = requests.get(BASE_URL+API_KEY+query)
    json_result = response.json()

    with open('data/'+str(page)+'_academic_instiutions.json', 'w') as outfile:
        json.dump(json_result, outfile)
    page_end = time.time()
    print(f'Finished page {page}/{TOTAL_PAGE} in {(page_end-page_start)/60} mins.\n')
end = time.time()
print(f'Took {(end-start)/60} minutes to run this script.')