1. Get a fine grain token with environment/metadata/secrets/variables read only access
2. set GITHUB_TOKEN env variable to that token
3. run poetry install
4. run poetry run review-environments --org your_org_or_user -c output.csv
5. Get a list of all secrets (names, not values) and variables (names and values) in your organization or user repos.
