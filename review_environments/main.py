import requests
import csv
import os

def analyze_github_repo_environments(repo_name: str, token: str, csv_writer) -> None:
    """
    Analyze all environments in a GitHub repository, listing all secrets and variables.
    
    Args:
        repo_name: GitHub repository name in format 'owner/repo'
        token: GitHub personal access token with appropriate permissions
        output_file: Path to output CSV file
    
    Output format:
        - For secrets: SECRET, repo_name, environment_name, secret_name
        - For variables: VARIABLE, repo_name, environment_name, variable_name, variable_value
    """
    base_url = f"https://api.github.com/repos/{repo_name}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    print(f"Attempting to dump config for {repo_name}")
    
    # Get all environments
    environments_url = f"{base_url}/environments"
    environments_response = requests.get(environments_url, headers=headers)
    
    if environments_response.status_code != 200:
        print(f"Error retrieving environments: {environments_response.status_code}")
        print(environments_response.text)
        return
    
    environments_data = environments_response.json()
    environments = environments_data.get("environments", [])
    
    results = []
    
    for env in environments:
        env_name = env["name"]
        
        # Get secrets for this environment
        secrets_url = f"{base_url}/environments/{env_name}/secrets"
        secrets_response = requests.get(secrets_url, headers=headers)
        
        if secrets_response.status_code == 200:
            secrets_data = secrets_response.json()
            for secret in secrets_data.get("secrets", []):
                results.append(["SECRET", repo_name, env_name, secret["name"]])
        else:
            print(f"Error retrieving secrets for environment {env_name}: {secrets_response.status_code}")
        
        # Get variables for this environment
        variables_url = f"{base_url}/environments/{env_name}/variables"
        variables_response = requests.get(variables_url, headers=headers)
        
        if variables_response.status_code == 200:
            variables_data = variables_response.json()
            for variable in variables_data.get("variables", []):
                results.append([
                    "VARIABLE", 
                    repo_name, 
                    env_name, 
                    variable["name"], 
                    variable.get("value", "")
                ])
        else:
            print(f"Error retrieving variables for environment {env_name}: {variables_response.status_code}")
    
    # Write results to CSV
    for row in results:
        csv_writer.writerow(row)
    
    print(f"success. results added to output")

def list_github_repos(account_name, token):
    """
    List repositories for either a GitHub user or organization.
    Automatically detects whether the account is a user or organization.
    
    Args:
        account_name: GitHub username or organization name
        token: GitHub personal access token
        
    Returns:
        List of repository names
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    # First check if account is an organization
    org_url = f"https://api.github.com/orgs/{account_name}"
    org_response = requests.get(org_url, headers=headers)
    
    # If not 200, try as a user
    if org_response.status_code != 200:
        base_url = f"https://api.github.com/users/{account_name}/repos"
        account_type = "user"
    else:
        base_url = f"https://api.github.com/orgs/{account_name}/repos"
        account_type = "organization"
    
    print(f"Detected account type: {account_type}")
    
    # Now fetch the repositories
    repos = []
    page = 1
    
    while True:
        response = requests.get(f"{base_url}?per_page=100&page={page}", headers=headers)
        
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            break
            
        page_repos = response.json()
        if not page_repos:
            break
            
        repos.extend([repo["full_name"] for repo in page_repos])
        page += 1
    
    return repos

import argparse

def main():
    parser = argparse.ArgumentParser(description='Process organization and CSV file.')
    
    # Add arguments with both short and long forms
    parser.add_argument('--org', '-o', type=str, required=True, 
                        help='Organization name (string)')
    parser.add_argument('--csv', '-c', type=str, required=True, 
                        help='Path to the CSV file (string)')
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Access the parsed arguments
    org_name = args.org
    csv_file = args.csv
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        print("Please set GITHUB_TOKEN environment variable")
        exit(1)

    repos = list_github_repos(org_name, github_token)
    
    
    # Write results to CSV
    with open(csv_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        for repo_name in repos:
            analyze_github_repo_environments(repo_name, github_token, csv_writer)#, output_file=csv_file)