#!/bin/bash

################################################################################
#
# This script is used to setup gcloud authentication for GitHub Actions.
# It is based on the following guide: https://github.com/google-github-actions/auth#setup
#
################################################################################

### Functions ###
colorize() {
  gum style --foreground "$1" "$2"
}

pink() {
  colorize 212 "$1"
}

setup_workload_identity() {
  # Enable necessary APIs
  gcloud services enable \
      iam.googleapis.com \
      cloudresourcemanager.googleapis.com \
      iamcredentials.googleapis.com \
      sts.googleapis.com \
      serviceusage.googleapis.com

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

  if [ $NEW_PROJECT = true ]; then
      sleep 60
  fi

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
}

set_gh_repo_secrets() {
  gh secret -R "${GITHUB_REPO}" set PROJECT_ID --body "${PROJECT_ID}" 
  gh secret -R "${GITHUB_REPO}" set SERVICE_ACCOUNT_ID --body "${SERVICE_ACCOUNT_ID}"
  gh secret -R "${GITHUB_REPO}" set WORKLOAD_IDENTITY_PROVIDER --body "${WORKLOAD_IDENTITY_PROVIDER}"
  gh secret -R "${GITHUB_REPO}" set REGION --body "${REGION}"
  gh secret -R "${GITHUB_REPO}" set ZONE --body "${ZONE}"
  gh secret -R "${GITHUB_REPO}" set SMARTY_AUTH_ID --body "${SMARTY_AUTH_ID}"
  gh secret -R "${GITHUB_REPO}" set SMARTY_AUTH_TOKEN --body "${SMARTY_AUTH_TOKEN}"
}

### Main ###

# Install gum
if ! command -v gum &> /dev/null; then
    echo "Installing gum..."
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://repo.charm.sh/apt/gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/charm.gpg
    echo "deb [signed-by=/etc/apt/keyrings/charm.gpg] https://repo.charm.sh/apt/ * *" | sudo tee /etc/apt/sources.list.d/charm.list
    sudo apt update && sudo apt install gum
fi

# Intro text
gum style --border normal --margin "1" --padding "1 2" --border-foreground 212 "Welcome to the $(pink 'PHDI Google Cloud') setup script!"
echo "This script will help you setup $(pink 'gcloud') authentication for GitHub Actions."
echo "We need some info from you to get started."
echo

# Prompt for region, zone, and Smarty creds
echo "Please select the $(pink 'region') you would like to deploy to."
echo "More info: https://cloud.google.com/compute/docs/regions-zones/regions-zones"
REGION=$(gcloud compute regions list --filter="name~'us-'" | tail +2 | awk '{print $1}' | gum choose)

echo "Please select the $(pink 'zone') you would like to deploy to."
ZONE=$(gcloud compute zones list --filter="name~'${REGION}'" | tail +2 | awk '{print $1}' | gum choose)

echo "Please enter the $(pink 'Authorization ID') of your Smarty Street Account."
echo "More info: https://www.smarty.com/docs/cloud/authentication"
SMARTY_AUTH_ID=$(gum input --placeholder="Authorization ID")

echo "Please enter the $(pink 'Authorization Token') of your Smarty Street Account."
echo "More info: https://www.smarty.com/docs/cloud/authentication"
SMARTY_AUTH_TOKEN=$(gum input --placeholder="Authorization Token")

# Prompt user for project name
if gum confirm "Do you already have a $(pink 'Project') in Google Cloud Platform?"; then
  PROJECT_NAME=$(gum input --prompt="Please enter the name of the existing $(pink 'Project'). " --placeholder="Project name")
  NEW_PROJECT=false
else
  PROJECT_NAME=$(gum input --prompt="Please enter a name for a new $(pink 'Project'). " --placeholder="Project name")
  NEW_PROJECT=true
fi

# Create a project if needed and get the project ID
if [ $NEW_PROJECT = true ]; then
    echo "Thank you! We will now create a new Google Cloud $(pink 'project') for you. A window will open asking you to authorize the gcloud CLI. Please click '$(pink 'Authorize')'."
    echo

    sleep 2
    gum spin -s line --title "Creating $(pink 'project')..." -- gcloud projects create --name="${PROJECT_NAME}"
    CHECK_COUNT=0
    while [ -z "$PROJECT_ID" ]; do
        gum spin -s line --title "Waiting for $(pink 'project') to be ready..." -- sleep 5
        PROJECT_ID=$(gcloud projects list --filter="name:'${PROJECT_NAME}'" --format="value(projectId)")
        CHECK_COUNT=$((CHECK_COUNT+1))
        if [ $CHECK_COUNT -gt 12 ]; then
            echo "Error: Project ID not found. To list projects, run 'gcloud projects list'."
            exit 1
        fi
    done
else
    echo "Thank you! We will now get the ID of your existing Google Cloud $(pink 'project'). A window will open asking you to authorize the gcloud CLI. Please click '$(pink 'Authorize')'."
    echo

    sleep 2
    PROJECT_ID=$(gcloud projects list --filter="name:${PROJECT_NAME}" --format="value(projectId)")
fi

# Set the current project to the PROJECT_ID specified above
gum spin -s line --title "Setting gcloud default $(pink 'project')..." -- gcloud config set project "${PROJECT_ID}"

# Login to gh CLI
echo "Project ID $(pink 'set')! We will now login to the $(pink 'GitHub CLI'). Copy the provided code and then click the link that will be printed. Paste the code into the browser tab that opens. Then return to this terminal!"
echo

gh auth login --hostname github.com -p https -w
GITHUB_USER=$(gh api user -q '.login')

# Get repository name
if gum confirm "Have you already forked the $(pink 'phdi-google-cloud') repository on GitHub?"; then
  REPO_NAME=$(gh repo list --fork --json name --jq ".[].name" | gum choose)
  GITHUB_REPO="${GITHUB_USER}/${REPO_NAME}"
else
  gum spin -s line --title "Forking repository..." -- gh repo fork CDCgov/phdi-google-cloud
  GITHUB_REPO="${GITHUB_USER}/phdi-google-cloud"
fi
echo "GitHub repository $(pink 'set')!"
echo

gum spin -s line --title "Setting up Workload Identity Federation..." -- setup_workload_identity

echo "Workload Identity Federation setup $(pink 'complete')!"
echo

gum spin -s line --title "Setting repository secrets..." -- set_gh_repo_secrets

echo "Repository secrets set!"
echo
sleep 1

# Sendoff
clear
gum style --border normal --margin "1" --padding "1 2" --border-foreground 212 "Quick start $(pink 'complete')! You can now continue with the Quick Start instructions in the README.md file."