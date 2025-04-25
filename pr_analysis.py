import json
import requests
from datetime import datetime

github_token = ''
repositories = ['BritishAirways-Ent/ops-odie-core-infra','BritishAirways-Ent/ops-odie-services','BritishAirways-Ent/ops-odie-datadog', 'BritishAirways-Ent/ops-odie-terraform-modules', 'BritishAirways-Ent/ops-odie-developer-tools']
deployers_group = {'yuvrajunde-ba','gayathris-ba','lakshmipriyanka-ba','krishnanttd','shahrukhsayyadba','BA-OscarPocock','MuhammadTahirBA','geetha1priya','BA-Harikrishna','emmanuelanya-ba'}
start_date = '2025-01-01T00:00:00Z'
end_date = '2025-04-24T00:00:00Z'
headers = {
    'Authorization': f'token {github_token}',
    'Accept': 'application/vnd.github+json'
}

s = []
def get_pull_requests(repo):
    prs = []
    page = 1
    while True:
        query = f'repo:{repo} is:pr created:{start_date}..{end_date}'
        url = f"https://api.github.com/search/issues"
        params = {
            'q':query,
            'per_page': 100,
            'page': page,
            'sort': 'created',
            'order': 'asc'
        }
        response = requests.get(url,headers=headers,params=params, verify=False)
        
        data = response.json()
        items = data.get('items',[])
        if not items:
            break
        for pr in items:
                if (pr['title'].startswith("feat(") or pr['title'].startswith("fix(") and pr['state'] == 'closed') and pr['pull_request']['merged_at'] != None:
                    prs.append(pr)
 
        if len(items) == 0:
            break 
        page += 1
    return prs

def get_reviews(repo, pr_number):
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"
    response = requests.get(url,headers=headers,verify=False)
    return response.json()

def analyze_repositories():
    total_prs = 0
    approved_by_group = 0
    reviewed_by_group = 0
    for repo in repositories:
        prs = get_pull_requests(repo)
        total_prs += len(prs)
        for pr in prs:
            pr_number = pr['number']
            reviews = get_reviews(repo, pr_number)

            approved_by_deployer_group = False
            number_of_times_reviewed_by_deployer_group = False

            for review in reviews:
                user = review['user']['login']

                state = review['state']
                if user in deployers_group and state == 'COMMENTED' or state == 'CHANGES_REQUESTED' or state == 'APPROVED' :
                    number_of_times_reviewed_by_deployer_group = True

                    if number_of_times_reviewed_by_deployer_group:
                        reviewed_by_group += 1

                if user in deployers_group and state == 'APPROVED':
                    approved_by_deployer_group = True

                    if approved_by_deployer_group:
                        approved_by_group += 1
    
    print(f"Total PR's: {total_prs}")
    print(f"Number of times PR's reviewed by Platform Engineer: {reviewed_by_group}")
    print(f"Approved by Platform Engineer: {approved_by_group}")


analyze_repositories()
