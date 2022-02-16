#Import necessary libraries
from os import stat_result
from numpy import rec
import pandas as pd
import sklearn
import scipy
import sys
from scipy import stats
from sklearn.metrics import recall_score

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction import text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from sqlalchemy import column
from fuzzywuzzy import process

from tabulate import tabulate


#Load Data
academic_features_df = pd.read_csv("data/test.csv")
academic_features_df = academic_features_df.dropna(subset=['2019.admissions.admission_rate.overall'])
academic_features_df = academic_features_df.reset_index(drop=True)

academic_df = pd.read_csv('data/clean_academic_instituion_data.csv')

org_df = pd.read_csv("data/clean_organization_data.csv")

non_profit_df = pd.read_csv('data/non_profit_data_clean.csv')

#Convert non-profit data to correct format
non_profit_df.NAME= non_profit_df.NAME.str.title()
non_profit_df.URL= non_profit_df.URL.str.lower()

#Set pandas options
pd.set_option('mode.chained_assignment', None)


#Function to identify which demographic categories to search for 
def get_demographic_column(user_input):

    demographic_list = []

    #Set search terms for each ethnicity
    black = ['black', 'african american', 'african-american']
    hispanic = ['hispanic', 'latinx', 'hispanic american', 'hispanic-american','latino', 'latina']
    asian = ['asian', 'asian american', 'asian-american']
    native_american = ['native american']
    hawaii = ['hawaiian', 'pacific islander', 'native hawaiian']

    #Create column for total number of each ethnicity
    for demographic in user_input:
        if demographic in black:
            demographic_list.append('#_ETHNICITY_BLACK')

        if demographic in hispanic:
            demographic_list.append('#_ETHNICITY_HISPANIC')

        if demographic in asian:
            demographic_list.append('#_ETHNICITY_ASIAN')

        if demographic in native_american:
            demographic_list.append('#_ETHNICITY_NATIVE_AMERICAN')

        if demographic in hawaii:
            demographic_list.append('#_ETHNICITY_NATIVE_HAWAIIAN_&_PACIFIC_ISLANDER')

    return demographic_list


#Function to identify which majors to search for
def get_major_list(user_input):

    major_list = []

    #Set search terms for each major
    engineering = ['eng','engineering', 'engineer']
    engineering_tech = ['eng', 'tech', 'computer science', 'data science', 'code']
    resources = ['natural resources', 'natural-resources', 'resources']
    agriculture = ['agg', 'agriculture', 'farming', 'farm', 'livestock', 'husbandry']
    biology = ['biology', 'bio']
    physical_science = ['chemistry', 'chem', 'physics', 'earth science', 'geology', ]
    public_admin = ['political science', 'poli sci', 'public policy', 'public administration']

    #Create column for total number of students in each major
    for major in user_input:
        if major in biology:
            major_list.append('BIOLOGY#')

        if major in resources:
            major_list.append('RESOURCES#')

        if major in physical_science:
            major_list.append('PHYSICAL_SCIENCE#')

        if major in agriculture:
            major_list.append('AGRICULTURE#')

        if major in engineering:
            major_list.append('ENGINEERING#')

        if major in public_admin:
            major_list.append('PUBLIC_ADMIN#')

        if major in engineering_tech:
            major_list.append('ENGINEERING_TECH#')

    return major_list


#Function to obtain index location for school the user input
def get_school_iloc(user_input):

    #Create list of all school names
    school_names = [name.lower() for name in academic_features_df['Unnamed: 0'].to_list()]

    #Create list of matches between user input and school list
    user_input_matches = [school for school in school_names if user_input.lower() in school]
    if len(user_input_matches) > 0:  
        
        #Get iloc of school matches
        rows = academic_features_df[academic_features_df['Unnamed: 0'].str.lower().str.contains(user_input.lower())]
        if len(rows) == 1:
            school_iloc = int(rows.index[0])
            
            return school_iloc


        #If no matches return most similar schools for the user to choose
        else: 
            print(f'We see several schools related to "{user_input}".\nSelect the school you are interested in.')
            selection_list = rows['Unnamed: 0'].to_list()
            enumerated_selection_list = [f"{i + 1} - {selection_list[i]}" for i in range(len(selection_list))]
            input_string = "\n".join(enumerated_selection_list)
            selection = input(input_string  + "\n")
            selection = int(selection)
            school_iloc = int(rows.index[selection - 1])

            return school_iloc
    
    
    closest_match = process.extractOne(user_input.lower(),school_names)
    print(f"We can't find {user_input}. Select the school you meant to search.")
    suggestions = 3
    suggestions = min(len(closest_match), suggestions)
    enumerated_suggestion_list = [f"{i + 1} - {closest_match[i]}" for i in range(suggestions)]
    input_string = "\n".join(enumerated_suggestion_list)
    selection = input(input_string + "\n")
    selection = int(selection)
    row = academic_features_df[academic_features_df['Unnamed: 0'].str.lower().str.contains(closest_match[selection - 1].lower())]
    school_iloc = int(row.index[0])
    
    return school_iloc


#Function to get index locations of schools similar to the user input
def get_similar_schools_index_locations(school_iloc, academic_features_df= academic_features_df):

    academic_features_df = academic_features_df.drop(columns='Unnamed: 0')

    #Normalize student size
    academic_features_df['2019.student.size'] = (academic_features_df['2019.student.size'] - academic_features_df['2019.student.size'].min()) / (academic_features_df['2019.student.size'].max() - academic_features_df['2019.student.size'].min())

    #Get sim scores
    academic_cosine_sim = cosine_similarity(academic_features_df, academic_features_df)

    #Convert to dataframe and label columns and rows
    academic_cosine_sim = pd.DataFrame(academic_cosine_sim)
    academic_cosine_sim.index = academic_features_df.index
    academic_cosine_sim.columns = academic_features_df.index

    #Get list of index locations most similar to user input 
    #Relative to threshold
    threshold = 0.90
    similar_schools_scores = academic_cosine_sim.iloc[int(school_iloc)].sort_values(ascending=False)
    similar_schools_scores = similar_schools_scores[similar_schools_scores > threshold]

    return similar_schools_scores


#Function to get index locations for user input organizations
def get_org_iloc(org_user_input):
    """
    this funciton takes a string and returns an 
    dataframe iloc
    """
    
    #Create list of all org names
    org_names = [name.lower() for name in org_df['NAME'].to_list()]

    #Create list of matches between user input and org list
    org_user_input_matches = [org for org in org_names if org_user_input.lower() in org]

    if len(org_user_input_matches) > 0:  
        
        #Get iloc of org matches
        org_rows = org_df[org_df['NAME'].str.lower().str.contains(org_user_input.lower())]
        
        if len(org_rows) == 1:
            org_iloc = org_rows.index[0]

            return org_iloc
        

        #If no matches return most similar schools for the user to choose
        else: 
            print(f'We see several orgs related to "{org_user_input}".\nSelect the org you are interested in.')
            org_selection_list = org_rows['NAME'].to_list()
            org_enumerated_selection_list = [f"{i + 1} - {org_selection_list[i]}" for i in range(len(org_selection_list))]
            org_input_string = "\n".join(org_enumerated_selection_list)
            org_selection = input(org_input_string + "\n")
            org_selection = int(org_selection)
            org_iloc = org_rows.index[org_selection - 1]

            return org_iloc
    
    
    org_closest_match = process.extractOne(org_user_input.lower(),org_names)
    print(f"We can't find {org_user_input}. Select the org you meant to search.")
    org_suggestions = 3
    org_suggestions = min(len(org_closest_match), org_suggestions)
    org_enumerated_suggestion_list = [f"{i + 1} - {org_closest_match[i]}" for i in range(org_suggestions)]
    org_input_string = "\n".join(org_enumerated_suggestion_list)
    org_selection = input(org_input_string + "\n")
    org_selection = int(org_selection)
    org_row = org_df[org_df['NAME'].str.lower().str.contains(org_closest_match[org_selection - 1].lower())]
    org_iloc = org_row.index[0]
    
    return org_iloc


#Function to get index locations of orgs similar to the user input
def get_similar_orgs_index_locations(org_iloc, org_df = org_df):

    #List of stop words
    my_stop_words = text.ENGLISH_STOP_WORDS.union(["Association", "Guild", "American", "Institute", "association", "guild", 
    "american", "institute", "Board", "Council", "Chamber", "board", "council", "chamber", "Alliance", "Society", 
    "alliance", "society", "Club", "club", "Center", "Bureau", "center", "bureau"])

    #Instantiate vectors
    tfidf = TfidfVectorizer(stop_words= my_stop_words)
    org_df = org_df.fillna('')

    #TF-IDF vectors
    tfidf_name_matrix = tfidf.fit_transform(org_df['NAME'])
    tfidf_bio_matrix = tfidf.fit_transform(org_df['PURPOSE'])
    tfidf_type_matrix = tfidf.fit_transform(org_df['SCOPE'])

    #Set up linear kernel
    name_cosine_sim = linear_kernel(tfidf_name_matrix, tfidf_name_matrix)
    bio_cosine_sim = linear_kernel(tfidf_bio_matrix, tfidf_bio_matrix)
    type_cosine_sim = linear_kernel(tfidf_type_matrix, tfidf_type_matrix)
    
    #Generate a weighted similarity score
    name_weight = 0.80
    bio_weight = 0.15
    type_weight = 0.05
    
    org_sim_scores = (name_weight*name_cosine_sim) + (bio_weight*bio_cosine_sim) + (type_weight*type_cosine_sim)

    #Create a similarity dataframe that's filtered by 
    #A given threshold and sorted
    org_threshold = 0.2
    org_sim_scores = pd.DataFrame(org_sim_scores)
    similar_orgs_scores = org_sim_scores.iloc[org_iloc].sort_values(ascending=False)
    similar_orgs_scores = similar_orgs_scores[similar_orgs_scores > org_threshold]

    return similar_orgs_scores


#Function to generate recommendations to return to the user
def generate_recommendations(user_input, academic_df=academic_df):

    #Unpack user inputs
    demographics = user_input.get('demographics')
    student = user_input.get('candidate_type', {}).get('student')
    professional = user_input.get('candidate_type', {}).get('professional')
    majors = user_input.get('majors')
    states = user_input.get('states')
    keywords = user_input.get('keywords')
    school_examples = user_input.get('school_examples')
    organization_examples = user_input.get('organization_examples')

    recommendations = {}
    
    if demographics: demographic_list = get_demographic_column(demographics)
    
    if majors: major_list = get_major_list(majors)

    #Select the dataframes per the user input
    if student:
        recommendations['Colleges and Universities'] = academic_df

        if majors and not school_examples:
            df = recommendations['Colleges and Universities']
            df.sort_values(by=major_list, inplace=True, ascending=False)
            recommendations['Colleges and Universities'] = df.iloc[:16]
        
        if demographics and not school_examples:
            df = recommendations['Colleges and Universities']
            df.sort_values(by=demographic_list, inplace=True, ascending=False)
            recommendations['Colleges and Universities'] = df
        


    if professional:
        recommendations['Professional Organizations'] = org_df

    #Filter the states per the user input
    if states and not school_examples:
        state_filter_string = "|".join(states)
        for key in recommendations.keys():
            #Return df filterd by states return df filterd by states
            #Recommendation dataframe dictionary
            df = recommendations[key]
            
            #Determine which df and select the state location
            #Column to filter 
            if key == 'Colleges and Universities':
                df = df[df['STATE'].str.contains(state_filter_string)]
            else:
                df = df[df['STATE'].str.contains(state_filter_string)]

            #Update the recommendations df for the filtered df
            recommendations[key] = df

    #Check to see if true        
    if school_examples: 
        
        #Get a list of ilocs that match user input
        school_ilocs = [get_school_iloc(school_name) for school_name in school_examples] 

        #Create empty dict to calculate max value for given similar school
        similar_school_scores = {} 

        #Loop through user inputs
        for school in school_ilocs:

            #For each user input get a pandas Series of similar schools 
            similar_schools = get_similar_schools_index_locations(school) 

            similar_school_ilocs = similar_schools.index.to_list()
            similar_school_weights = similar_schools.to_list()

            #For each similar school
            for i in range(len(similar_school_ilocs)):

                #Check to see if it is already in dict
                if similar_school_ilocs[i] in similar_school_scores: 

                    #If so append the score to the list for the iloc
                    similar_school_scores[similar_school_ilocs[i]].append(similar_school_weights[i]) 

                #Otherwise add first weight entry into the scores dict for the given similar school
                else: 
                    similar_school_scores[similar_school_ilocs[i]] = [similar_school_weights[i]]

        #Convert list to max value
        for key, value in similar_school_scores.items(): 
            similar_school_scores[key] = max(value)

        #Turn dict into a sorted series
        similar_school_scores = pd.Series(similar_school_scores).sort_values(ascending=False)

        #Return results 
        similar_school_ilocs = similar_school_scores.index.to_list() 

        #Update recommendations df
        recommendations['Colleges and Universities'] = recommendations['Colleges and Universities'].iloc[similar_school_ilocs]

        #Filter the states per the user input
        if states:
            state_filter_string = "|".join(states)
            recommendations['Colleges and Universities'] = recommendations['Colleges and Universities'][recommendations['Colleges and Universities']['STATE'].str.contains(state_filter_string)]

        #Filter majors per the user input
        if majors:
            recommendations['Colleges and Universities'].sort_values(by=major_list, inplace=True, ascending=False)
            recommendations['Colleges and Universities'] = recommendations['Colleges and Universities'].iloc[:16]

        #Filter demographics per the user input
        if demographics:
            recommendations['Colleges and Universities'].sort_values(by=demographic_list, inplace=True, ascending=False)

    #Check to see if true
    if organization_examples:

        #Get a list of ilocs that match user input
        org_ilocs = [get_org_iloc(org_name) for org_name in organization_examples]

        #Create empty dict to calculate max value for given similar org
        similar_org_scores = {}

        #Loop through user inputs
        for org in org_ilocs:

            #For each user input get a pandas Series of similar orgs
            similar_orgs = get_similar_orgs_index_locations(org)

            similar_orgs_ilocs = similar_orgs.index.to_list()
            similar_orgs_weights = similar_orgs.to_list()
            
            #For each similar org
            for i in range(len(similar_orgs_ilocs)):

                #Check to see if it is already in dict
                if similar_orgs_ilocs[i] in similar_org_scores:

                    #If so append the score to the list for the iloc
                    similar_org_scores[similar_orgs_ilocs[i]].append(similar_orgs_weights[i])

                #Otherwise add first weight entry into the scores dict for the given similar org
                else:
                    similar_org_scores[similar_orgs_ilocs[i]] = [similar_orgs_weights[i]]

        #Convert list to max value
        for key, value in similar_org_scores.items():
            similar_org_scores[key] = max(value)

        #Turn dict into a sorted series
        similar_org_scores = pd.Series(similar_org_scores).sort_values(ascending=False)

        #Return results 
        similar_org_ilocs = similar_org_scores.index.to_list()

        #Update recommendations df
        recommendations['Professional Organizations'] = recommendations['Professional Organizations'].iloc[similar_org_ilocs]

        #Filter the states per the user input
        if states:
            state_filter_string = "|".join(states)
            recommendations['Professional Organizations'] = recommendations['Professional Organizations'][recommendations['Professional Organizations']['STATE'].str.contains(state_filter_string)]


    #Function to generate scores for non-profits
    def generate_score(series, student=student, states=states, majors=majors, keywords=keywords):
        
        #Set weights 
        weights = dict(
            student = 0.30,
            majors = 0.20,
            states = 0.35,
            keywords = 0.15,
        )

        #Prepare the date
        title_words = series.NAME.split(' ')
        student_keywords = ['STUDENT','YOUTH','CHILDREN','TEEN']

        #Calculate the max possible score given the user query
        max_possible_score = 0
        if student: max_possible_score += 1 * weights['student']
        if states: max_possible_score += 1 * weights['states']
        if majors: max_possible_score += 1 * weights['majors']
        if keywords: max_possible_score += 1 * weights['keywords']
        max_possible_score *= 1.10

        #Calculate the actual raw score    
        score = 0
        if any([word.upper() in student_keywords for word in title_words]): score += 1 * weights['student']
        
        if states:
            if series.STATE in states: score += 1 * weights['states']

        if majors: 
            if any([word.upper() in [mj.upper() for mj in majors] for word in title_words]): score += 1 * weights['majors']
        
        if keywords: 
            if any([word.upper() in [kw.upper() for kw in keywords] for word in title_words]): score += 1 * weights['keywords']

        if any([series.NTEEFINAL == "C03", series.NTEEFINAL == "D03"]): score *= 1.10
        
        #Calculate the ranking score
        ranking_score = round(score / max_possible_score,2)

        return ranking_score
    

    #Apply generate_score function to non-profit df
    non_profit_df['SCORE'] = non_profit_df.apply(lambda x: generate_score(x, student=student, states=states, majors=majors, keywords=keywords), axis=1)
    
    #Sort values by 'SCORE', 'ASSETS', and 'INCOME'
    non_profit_df.sort_values(by=['SCORE', 'ASSETS', 'INCOME'], ascending=False, inplace=True)
    
    #Update recommendations df
    recommendations['Non-Profit Organizations'] = non_profit_df.iloc[:16]

    for key, value in recommendations.items():

        if len(recommendations[key]) > 0:
            recommendations[key] = recommendations[key].filter(['NAME', 'STATE', 'URL'], axis=1)
            print(f'\n{key.upper()}\n')
            print(tabulate(recommendations[key], showindex=False, headers=recommendations[key].columns))
            print('\n')

    return recommendations