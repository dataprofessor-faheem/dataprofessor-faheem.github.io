import requests, json
u="https://www.cbioportal.org/api/v3/api-docs"
j=requests.get(u,timeout=90).json()
for key in ["MutationFilter","MutationMultipleStudyFilter","StudyViewFilter"]:
    print("\nSCHEMA",key)
    print(json.dumps(j.get("components",{}).get("schemas",{}).get(key,{}),indent=2))
