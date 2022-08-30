################################################################################
#
# This script is used to setup gcloud authentication for GitHub Actions.
# It is based on the following guide: https://github.com/google-github-actions/auth#setup
#
################################################################################

# Function to output the variables needed to load into GitHub Actions secrets
function Get-Variables {
    Write-Host "Please load the following variables into your repository secrets at this URL:"
    Write-Host "https://github.com/$GITHUB_REPO/settings/secrets/actions"
    Write-Host  ""
    Write-Host "PROJECT_ID: $PROJECT_ID"
    Write-Host "SERVICE_ACCOUNT_ID: $SERVICE_ACCOUNT_ID"
    Write-Host "WORKLOAD_IDENTITY_PROVIDER: $WORKLOAD_IDENTITY_PROVIDER"
    Write-Host "REGION: us-central1 (or your preferred region)"
    Write-Host "ZONE: us-central1-a (or your preferred zone in the region above)"
    Write-Host ""
    Write-Host "More info on regions and zones can be found at:"
    Write-Host "https://cloud.google.com/compute/docs/regions-zones/"
    Write-Host ""
    Write-Host "You can now continue with the Quick Start instructions in the README.md file."
}

# Function to use GitHub CLI to set repository secrets
function Set-Variables {
    $GH_COMMAND = Get-Command "gh" -ErrorAction SilentlyContinue
    if ($null -eq $GH_COMMAND) {
        Write-Host "Error: The GitHub CLI is not installed. To install, visit this page:"
        Write-Host "https://cli.github.com/manual/installation"
        Write-Host
        Get-Variables
        Exit
    }

    Write-Host "Please enter the name of the region you would like to deploy to (e.g. us-central1)."
    Write-Host "More info: https://cloud.google.com/compute/docs/regions-zones/regions-zones"
    $REGION = Read-Host

    Write-Host "Please enter the name of the zone you would like to deploy to (e.g. us-central1-a)."
    Write-Host "More info: https://cloud.google.com/compute/docs/regions-zones/regions-zones"
    $ZONE = Read-Host

    Write-Host "Logging in to GitHub..."
    gh auth login

    Write-Host "Setting repository secrets..."
    gh secret -R "$GITHUB_REPO" set PROJECT_ID --body "$PROJECT_ID" 
    gh secret -R "$GITHUB_REPO" set SERVICE_ACCOUNT_ID --body "$SERVICE_ACCOUNT_ID"
    gh secret -R "$GITHUB_REPO" set WORKLOAD_IDENTITY_PROVIDER --body "$WORKLOAD_IDENTITY_PROVIDER"
    gh secret -R "$GITHUB_REPO" set REGION --body "$REGION"
    gh secret -R "$GITHUB_REPO" set ZONE --body "$ZONE"

    Write-Host "Repository secrets set!"
    Write-Host "You can now continue with the Quick Start instructions in the README.md file."
}

# Prompt user for project name and repository name
Write-Host "Welcome to the PHDI Google Cloud setup script!"
Write-Host "This script will help you setup gcloud authentication for Github Actions."
Write-Host "We need some info from you to get started."
Write-Host "After entering the info, a browser window will open for you to authenticate with Google Cloud."
Write-Host ""

while ($null -eq $PROJECT_NAME) {
    $yn = Read-Host "Do you already have a Project in Google Cloud Platform? (y/n)"
    Switch ($yn) {
        { @("y", "Y") -eq $_ } {
            $PROJECT_NAME = Read-Host "Please enter the name of the existing Project."
            $NEW_PROJECT = $false
        }
        { @("n", "N") -eq $_ } {
            $PROJECT_NAME = Read-Host "Please enter a name for a new Project."
            $NEW_PROJECT = $true
        }
        default { "Please enter y or n." }
    }
}

Write-Host "Please enter the name of the repository you will be deploying from."
Write-Host "For example, if your repo URL is https://github.com/CDCgov/phdi-google-cloud, enter: CDCgov/phdi-google-cloud."
$GITHUB_REPO = Read-Host

# Login to Google Cloud Platform
gcloud auth login

# Create a project if needed and get the project ID
if ($NEW_PROJECT) {
    gcloud projects create --name="$PROJECT_NAME"
}

$PROJECT_ID = (gcloud projects list --filter="name:'$PROJECT_NAME'" --format="value(projectId)")
if ([string]::IsNullOrEmpty($PROJECT_ID)) {
    Write-Host "Error: Project ID not found. To list projects, run 'gcloud projects list'."
    Exit 1
}

# Set the current project to the PROJECT_ID specified above
gcloud config set project "$PROJECT_ID"

# Enable necessary APIs
gcloud services enable `
    iam.googleapis.com `
    cloudresourcemanager.googleapis.com `
    iamcredentials.googleapis.com `
    sts.googleapis.com `
    serviceusage.googleapis.com

# Create a service account
gcloud iam service-accounts create "github" --project "$PROJECT_ID" --display-name "github"

# Get the service account ID and set some variables
$SERVICE_ACCOUNT_ID = (gcloud iam service-accounts list --filter="displayName:github" --format="value(email)")

# Grant the service account the owner role on the project
gcloud projects add-iam-policy-binding "$PROJECT_ID" `
    --member="serviceAccount:$SERVICE_ACCOUNT_ID" `
    --role="roles/owner"

# It's possible that creating the workload-identity-pools can fail if it's a new project
# due to propagation timings of certain APIs.
if ($NEW_PROJECT) {
    Write-Host "Waiting 60 seconds for Workload Identity Federation to be created."
    Start-Sleep -Seconds 60
}

# Create a Workload Identity Pool
gcloud iam workload-identity-pools create "github-pool" `
    --project="$PROJECT_ID" `
    --location="global" `
    --display-name="github pool"

# Get the full ID of the Workload Identity Pool
$WORKLOAD_IDENTITY_POOL_ID = ( `
        gcloud iam workload-identity-pools describe "github-pool" `
        --project="$PROJECT_ID" `
        --location="global" `
        --format="value(name)" `
)

# Create a Workload Identity Provider in that pool
gcloud iam workload-identity-pools providers create-oidc "github-provider" `
    --project="$PROJECT_ID" `
    --location="global" `
    --workload-identity-pool="github-pool" `
    --display-name="github provider" `
    --attribute-mapping="google.subject=assertion.sub, attribute.actor=assertion.actor, attribute.respository=assertion.repository" `
    --issuer-uri="https://token.actions.githubusercontent.com"

# Allow authentications from Workload Identity Provider origination from your repository to impersonate the Service Account created above
gcloud iam service-accounts add-iam-policy-binding "$SERVICE_ACCOUNT_ID" `
    --project="$PROJECT_ID" `
    --role="roles/iam.workloadIdentityUser" `
    --member="principalSet://iam.googleapis.com/$WORKLOAD_IDENTITY_POOL_ID/attribute.repository/$GITHUB_REPO"

# Extract the Workload Identity Provider name
$WORKLOAD_IDENTITY_PROVIDER = ( `
        gcloud iam workload-identity-pools providers describe "github-provider" `
        --project="$PROJECT_ID" `
        --location="global" `
        --workload-identity-pool="github-pool" `
        --format="value(name)" `
)

Write-Host "Workload Identity Federation setup complete!"
Write-Host ""

while ($null -eq $SCRIPT_DONE) {
    $yn = Read-Host "Would you like to use the GitHub CLI to set repository secrets automatically? (y/n) "
    Switch ($yn) {
        { @("y", "Y") -eq $_ } {
            Set-Variables
            $SCRIPT_DONE = $true
        }
        { @("n", "N") -eq $_ } {
            Get-Variables
            $SCRIPT_DONE = $true
        }
        default { "Please enter y or n." }
    }
}