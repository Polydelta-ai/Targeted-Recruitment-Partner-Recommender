# recruitment-rec-engine-prototype #
A recommendation engine that identifies academic institutions and organizations to target during recruitment.

## Summary of the Recruitment Recommendation Engine ##
From 3 disparate data sets, we were able to evaluate over 1 million different organizations as potential partners. We gathered data from the [College Scorecard](https://collegescorecard.ed.gov/data/), [National Center for Charitable Statistics Data Archive](https://nccs-data.urban.org/), and the [Directory of Associations](https://directoryofassociations.com/). Each data set has its own transformation pipeline and vectorization process. These vecotrs are then used to train a model or processed through a scoring algorithm. 

### Academic Institutions ###
Our academic institution model calculates the cosine similarity between two schools based on the following characteristics:
- Size
- Admission Rate
- Demographic Makeup
- Program Distribution

### Professional Organizations ###
Our professional organization model utilizes a Term Frequency - Inverse Document Frequency vectorizer implemented with a linear kernel to compare organizations based on the following characteristics:
- Name
- Bio
- Organization Type

### Non-profits ###
Our non-profit scoring algorithm calculates a score for each non-profit organization according to user input for the following areas:
- Candidate Type
- Location
- Relevant Majors
- Keywords

## Demonstration of *demo.py* ##
The *demo.py* file currently takes in dictionary of user inputs. The user can indicate:
- Target Demograpic
- Candidate Type
- Location
- Relevant Majors
- Keywords
- Academic Institution Examples
- Organization Examples

The user may input as many or as few of these categories as desired. Once the dictionary has been input, the demo will return a set of 3 dataframes with the recommended academic institutions, professional organizations, and non-profits.
