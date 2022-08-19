#!/bin/bash

################################################################################
#
# This script is used to setup gcloud authentication for GitHub Actions.
# It is based on the following guide: https://github.com/google-github-actions/auth#setup
#
################################################################################

# Prompt user for project name and repository name
echo "Welcome to the PHDI Google Cloud setup script!"
echo "This script will help you setup gcloud authentication for GitHub Actions."
echo "We need some info from you to get started."
echo "After entering the info, a browser window will open for you to authenticate with Google Cloud."
echo
while true; do
    read -p "Do you already have a Project in Google Cloud Platform? (y/n) " yn
    case $yn in
        [Yy]* ) read -p "Please enter the name of the existing Project. " PROJECT_NAME; NEW_PROJECT=false; break;;
        [Nn]* ) read -p "Please enter a name for a new Project. " PROJECT_NAME; NEW_PROJECT=true; break;;
        * ) echo "Please answer y or n.";;
    esac
done
echo "Please enter the name of the repository you will be deploying from."
echo "For example, if your repo URL is https://github.com/CDCgov/phdi-google-cloud, enter: CDCgov/phdi-google-cloud"
read GITHUB_REPO

# Login to Google Cloud Platform
gcloud auth login

# Create a project if needed and get the project ID
if [ $NEW_PROJECT = true ]; then
    gcloud projects create $PROJECT_NAME
fi
PROJECT_ID=$(gcloud projects list --filter="name:${PROJECT_NAME}" --format="value(projectId)")
if [ -z "$PROJECT_ID" ]; then
    echo "Error: Project ID not found. To list projects, run 'gcloud projects list'."
    exit 1
fi

# Create a service account
gcloud iam service-accounts create "github" \
  --project "${PROJECT_ID}" \
  --display-name "github"

# Get the service account ID and set some variables
SERVICE_ACCOUNT_ID=$(gcloud iam service-accounts list --filter="displayName:github" --format="value(email)")

# Grant the service account the owner role on the project
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SERVICE_ACCOUNT_ID}" \
  --role="roles/owner"

# Enable the IAM Credentials API
gcloud services enable iamcredentials.googleapis.com --project "${PROJECT_ID}"

# Create a Workload Identity Pool
gcloud iam workload-identity-pools create "github-pool" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --display-name="github pool"

# Get the full ID of the Workload Identity Pool
WORKLOAD_IDENTITY_POOL_ID=$(gcloud iam workload-identity-pools describe "github-pool" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --format="value(name)")

# Create a Workload Identity Provider in that pool
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="github provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# Allow authentications from the Workload Identity Provider originating from your repository to impersonate the Service Account created above
gcloud iam service-accounts add-iam-policy-binding "${SERVICE_ACCOUNT_ID}" \
  --project="${PROJECT_ID}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/${WORKLOAD_IDENTITY_POOL_ID}/attribute.repository/${GITHUB_REPO}"

# Extract the Workload Identity Provider resource name
WORKLOAD_IDENTITY_PROVIDER=$(gcloud iam workload-identity-pools providers describe "github-provider" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --format="value(name)")

# Output the variables needed to load into GitHub Actions secrets
echo "Workload Identity Federation setup complete!"
echo
echo "Please load the following variables into your repository secrets at this URL:"
echo "https://github.com/$GITHUB_REPO/settings/secrets/actions"
echo
echo "PROJECT_ID: ${PROJECT_ID}"
echo "SERVICE_ACCOUNT_ID: ${SERVICE_ACCOUNT_ID}"
echo "WORKLOAD_IDENTITY_PROVIDER: ${WORKLOAD_IDENTITY_PROVIDER}"
echo "REGION: us-west1 (or your preferred region)"
echo "ZONE: us-west1b (or your preferred zone in the region above)"
echo
echo "More info on regions and zones can be found at:"
echo "https://cloud.google.com/compute/docs/regions-zones/"
echo
echo "You can now continue with the Quick Start instructions in the README.md file."