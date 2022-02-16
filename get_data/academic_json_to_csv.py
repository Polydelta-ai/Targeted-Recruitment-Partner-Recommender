import json
import time
import pandas as pd

# Opening JSON file
TOTAL_PAGE = 135# this what the results stop at apparently
school_data = []
for page in range(TOTAL_PAGE):
    f = open('data/'+str(page)+'_academic_instiutions.json')
    school_data.append(json.load(f))
    # Closing file
    f.close()

# Initliaze the columns
final_dict = dict()
for key in school_data[0]['results'][0].keys():
    final_dict[key] = []

start = time.time()
for data in school_data:
    #print(data)
    for school_result in data['results']:
        for k,v in school_result.items():
            final_dict[k].append(v)
end = time.time()
print(f'Took {(end-start)/60} mins to convert json to one csv.')

pd.DataFrame(final_dict).to_csv('data/academic_institutions.csv',index=False)