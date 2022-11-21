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

spin() {
  local -r title="${1}"
  shift 1
  gum spin -s line --title "${title}" -- $@
}

enable_billing() {
  BILLING_ACCOUNT_COUNT=$(gcloud beta billing accounts list --format json | jq '. | length')
  while [ BILLING_ACCOUNT_COUNT -eq 0 ]; do
    echo "You don't have any $(pink 'billing accounts') yet."
    echo "If you are responsible for billing, please create one in the Google Cloud Console at https://console.cloud.google.com/billing."
    echo "If you are not responsible for billing, please ask your billing admin to create one for you."
    echo "Press $(pink 'Enter') to continue once the billing account is created. Type $(pink 'exit') to exit the script."
    read SHOULD_CONTINUE
    if [ $SHOULD_CONTINUE = "exit" ]; then
      exit 1
    else
      BILLING_ACCOUNT_COUNT=$(gcloud beta billing accounts list --format json | jq '. | length')
    fi
  done
  echo "You have $(pink $BILLING_ACCOUNT_COUNT) billing account(s)."
  echo "Please select the billing account you want to use for this project."
  BILLING_ACCOUNT_ID=$(gcloud beta billing accounts list --format="csv(displayName,name)" | gum table -w 25,25 | cut -d ',' -f 2)
}

link_billing_account() {
  spin "Linking $(pink 'project') to billing account..." gcloud beta billing projects link "${PROJECT_ID}" --billing-account="${BILLING_ACCOUNT_ID}"

}

### Main ###

# Install gum
if ! command -v gum &> /dev/null; then
    echo "Installing gum..."
    go install github.com/charmbracelet/gum@latest
fi

clear

# Intro text
gum style --border normal --margin "1" --padding "1 2" --border-foreground 212 "Welcome to the $(pink 'PHDI Google Cloud') setup script!"
echo "This script will help you setup $(pink 'gcloud') authentication for GitHub Actions."
echo "We need some info from you to get started."
echo

# Check if new project, create a project if needed and get the project ID
if gum confirm "Do you already have a $(pink 'Project') in Google Cloud Platform?"; then
  echo "We will now get the ID of your existing Google Cloud $(pink 'project'). A window will open asking you to authorize the gcloud CLI. Please click '$(pink 'Authorize')'."
  echo

  echo "Please select the $(pink 'project') you want to use:"
  PROJECT_NAME=$(gcloud projects list --format="value(name)" | gum choose)
  PROJECT_ID=$(gcloud projects list --filter="name:${PROJECT_NAME}" --format="value(projectId)")
  echo "You selected $(pink "${PROJECT_NAME}") with ID $(pink "${PROJECT_ID}")."
  echo

  # Check if billing is enabled, enable billing if needed and link billing account to project
  BILLING_ENABLED=$(gcloud beta billing projects describe "${PROJECT_ID}" --format="value(billingEnabled)")
  if [[ "${BILLING_ENABLED}" == "False" ]]; then
    enable_billing
    link_billing_account
  fi
else
  echo "Thank you! We will now attempt to create a new Google Cloud $(pink 'project') for you. A window will open asking you to authorize the gcloud CLI. Please click '$(pink 'Authorize')'."
  echo

  # Check if billing is enabled, enable billing if needed
  enable_billing

  PROJECT_NAME=$(gum input --prompt="Please enter a name for a new $(pink 'Project'). " --placeholder="Project name")
  PROJECT_ID=$(echo $PROJECT_NAME | awk '{print tolower($0)}')-$(date +"%s")
  spin "Creating $(pink 'project')..." gcloud projects create $PROJECT_ID --name="${PROJECT_NAME}"

  # Link billing account to project
  link_billing_account
fi

# Set the current project to the PROJECT_ID specified above
spin "Setting gcloud default $(pink 'project')..." gcloud config set project "${PROJECT_ID}"

# Enable necessary APIs
spin "Enabling $(pink 'gcloud APIs')..." gcloud services enable \
      compute.googleapis.com \
      iam.googleapis.com \
      cloudresourcemanager.googleapis.com \
      iamcredentials.googleapis.com \
      sts.googleapis.com \
      serviceusage.googleapis.com

# Prompt for region, zone, and Smarty creds
echo "Please select the $(pink 'region') you would like to deploy to."
echo "More info: https://cloud.google.com/compute/docs/regions-zones/regions-zones"
REGION=$(gcloud compute regions list --filter="name~'us-'" --format="value(name)" | gum choose)

echo "Please select the $(pink 'zone') you would like to deploy to."
ZONE=$(gcloud compute zones list --filter="name~'${REGION}'" --format="value(name)" | gum choose)

echo "Please enter the $(pink 'Authorization ID') of your Smarty Street Account."
echo "More info: https://www.smarty.com/docs/cloud/authentication"
SMARTY_AUTH_ID=$(gum input --placeholder="Authorization ID")

echo "Please enter the $(pink 'Authorization Token') of your Smarty Street Account."
echo "More info: https://www.smarty.com/docs/cloud/authentication"
SMARTY_AUTH_TOKEN=$(gum input --placeholder="Authorization Token")

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
  spin "Forking repository..." gh repo fork CDCgov/phdi-google-cloud
  GITHUB_REPO="${GITHUB_USER}/phdi-google-cloud"
fi
echo "GitHub repository $(pink 'set')!"
echo

### Set up Workload Identity ###

# Create a service account
spin "Creating service account..." gcloud iam service-accounts create "github" \
  --project "${PROJECT_ID}" \
  --display-name "github"

# Get the service account ID and set some variables
SERVICE_ACCOUNT_ID=$(gcloud iam service-accounts list --filter="displayName:github" --format="value(email)")

# Grant the service account the owner role on the project
spin "Granting service account owner role..." gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SERVICE_ACCOUNT_ID}" \
  --role="roles/owner"

if [ $NEW_PROJECT = true ]; then
    spin "Waiting for service account to be ready..." sleep 60
fi

# Create a Workload Identity Pool
spin "Creating workload identity pool..." gcloud iam workload-identity-pools create "github-pool" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --display-name="github pool"

# Get the full ID of the Workload Identity Pool
WORKLOAD_IDENTITY_POOL_ID=$(gcloud iam workload-identity-pools describe "github-pool" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --format="value(name)")

# Create a Workload Identity Provider in that pool
spin "Creating workload identity provider..." gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="github provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# Allow authentications from the Workload Identity Provider originating from your repository to impersonate the Service Account created above
spin "Adding IAM policy binding for GitHub repo..." gcloud iam service-accounts add-iam-policy-binding "${SERVICE_ACCOUNT_ID}" \
  --project="${PROJECT_ID}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/${WORKLOAD_IDENTITY_POOL_ID}/attribute.repository/${GITHUB_REPO}"

# Extract the Workload Identity Provider resource name
WORKLOAD_IDENTITY_PROVIDER=$(gcloud iam workload-identity-pools providers describe "github-provider" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --format="value(name)")

echo "Workload Identity Federation setup $(pink 'complete')!"
echo

### GitHub Actions ###

# Set up GitHub Secrets
spin "Setting PROJECT_ID..." gh secret -R "${GITHUB_REPO}" set PROJECT_ID --body "${PROJECT_ID}" 
spin "Setting SERVICE_ACCOUNT_ID..." gh secret -R "${GITHUB_REPO}" set SERVICE_ACCOUNT_ID --body "${SERVICE_ACCOUNT_ID}"
spin "Setting WORKLOAD_IDENTITY_PROVIDER..." gh secret -R "${GITHUB_REPO}" set WORKLOAD_IDENTITY_PROVIDER --body "${WORKLOAD_IDENTITY_PROVIDER}"
spin "Setting REGION..." gh secret -R "${GITHUB_REPO}" set REGION --body "${REGION}"
spin "Setting ZONE..." gh secret -R "${GITHUB_REPO}" set ZONE --body "${ZONE}"
spin "Setting SMARTY_AUTH_ID..." gh secret -R "${GITHUB_REPO}" set SMARTY_AUTH_ID --body "${SMARTY_AUTH_ID}"
spin "Setting SMARTY_AUTH_TOKEN..." gh secret -R "${GITHUB_REPO}" set SMARTY_AUTH_TOKEN --body "${SMARTY_AUTH_TOKEN}"

echo "Repository secrets $(pink 'set')!"
echo

# Create dev environment in GitHub
spin "Creating $(pink 'dev') environment..." gh api -X PUT "repos/${GITHUB_REPO}/environments/dev" --silent

# Run Terraform Setup workflow
echo "We will now run the $(pink 'Terraform Setup') workflow to create the necessary storage account for Terraform in Google Cloud."
spin "Running Terraform Setup workflow..." gh workflow run terraformSetup.yml

# Run optional deployment workflow
if gum confirm "Would you like to deploy the $(pink 'PHDI Google Cloud') infrastructure to your Google Cloud project?"; then
  echo "We will now run the $(pink 'Terraform Deploy') workflow to deploy the infrastructure to your Google Cloud project."
  spin "Running Terraform Deploy workflow..." gh workflow run deployment.yml -f environment=dev
  DEPLOYED=true
fi

# Sendoff
clear
gum style --border normal --margin "1" --padding "1 2" --border-foreground 212 "Quick start $(pink 'complete')! You can view your forked repository at https://github.com/${GITHUB_REPO}."
echo
echo "To view the status of your workflows, go to https://github.com/${GITHUB_REPO}/actions."
echo
if [ "$DEPLOYED" = true ]; then
  echo "Your infrastructure is deployed! To trigger your new pipeline, upload a file to the $(pink 'phdi-dev-phi') bucket at https://console.cloud.google.com/storage/browser."
  echo
fi
else
  echo "To deploy the infrastructure to your Google Cloud project, run the $(pink 'deployment') workflow at https://github.com/${GITHUB_REPO}/actions/workflows/deployment.yaml."
fi

echo
echo "Thanks for using the $(pink 'PHDI Google Cloud') quick start script!"