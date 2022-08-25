################################################################################
#
# This script is used to setup gcloud authentication for GitHub Actions.
# It is based on the following guide: https://github.com/google-github-actions/auth#setup
#
################################################################################

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

if ($NEW_PROJECT) {
    gcloud projects create $PROJECT_NAME
}

$PROJECT_ID = (gcloud projects list --filter="name:$PROJECT_NAME" --format="value(projectId)")
if ([string]::IsNullOrEmpty($PROJECT_ID)) {
    Write-Host "Error: Project ID not found. To list projects, run 'gcloud projects list'."
    Exit 1
}

# Set the current project to the PROJECT_ID specified above
gcloud config set project "$PROJECT_ID"

# Create a service account
gcloud iam service-accounts create "github" --project "$PROJECT_ID" --display-name "github"

# Get the service account ID and set some variables
$SERVICE_ACCOUNT_ID = (gcloud iam service-accounts list --filter="displayName:github" --format="value(email)")

# Grant the service account the owner role on the project
gcloud projects add-iam-policy-binding "$PROJECT_ID" `
    --member="serviceAccount:$SERVICE_ACCOUNT_ID" `
    --role="roles/owner"

# Enable the IAM Credentials API
gcloud services enable iamcredentials.googleapis.com --project "$PROJECT_ID"

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
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.respository=assertion.repository" `
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

# Output the variables needed to load into Github Actions Secrets
Write-Host "Workload Identity Federation setup complete!"
Write-Host ""
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