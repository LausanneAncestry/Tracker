from db import get_all_census_entries
import json
from job_matcher import match_job_with_dictionary, get_job_metadata

all_census = get_all_census_entries()

metadata_counts_per_census = {
    1835: {},
    1855: {},
    1874: {},
    1890: {},
}

#Track missing data
missing_values = {}

for census in all_census:
    if not census.job:
        continue

    metadata = get_job_metadata(match_job_with_dictionary(census.job)[1])
    census_year = census.census_year

    if metadata:
        for key, value in metadata.items():
            if value is None:
                #Continue if particular field is empty
                continue  

            #Count values for each datatype
            if key not in metadata_counts_per_census[census_year]:
                metadata_counts_per_census[census_year][key] = {}

            if value not in metadata_counts_per_census[census_year][key]:
                metadata_counts_per_census[census_year][key][value] = 0

            metadata_counts_per_census[census_year][key][value] += 1
    else:
        #Add to missing values if job not in metadatafile
        if match_job_with_dictionary(census.job)[1] not in missing_values.keys():
            missing_values[match_job_with_dictionary(census.job)[1]] = 1
        else:
            missing_values[match_job_with_dictionary(census.job)[1]] += 1

print(dict(sorted(missing_values.items(), key=lambda item: item[1], reverse=True)))

#Save to JSON
with open("analysis/results_metadata.json", mode="w", encoding='utf-8') as f:
    json.dump(metadata_counts_per_census, f, ensure_ascii=False, indent=2)
