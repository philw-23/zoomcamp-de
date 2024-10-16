/*
    Define basic terraform settings for infrastructure
*/
terraform {
  required_providers { # Determines the providers that need to be installed/used in the infrastructure
    /*
        Providers are plugins terraform uses to interface with APIs and cloud services. Providers add
        the set of resource types and datasets that terraform can manage. The README.md file has a link
        to the terraform provider documentation which has more information on available providers, declaration
        instructions, configuration settings, and links to individual provider documentation
    */
    google = { # Google provider
      source  = "hashicorp/google" # Source address of the provider; location where terraform downloads from 
      version = "5.6.0" # Version of the provider to use (for compatibility purposes in project)
    }
  }
}

provider "google" { # Note that provider name in initialization here must match name in required_providers
  credentials = file(var.credentials) # Path to credentials to use for GCP authentication. file() loads the json key
  project     = var.project # Project to use in GCP
  region      = var.region # Region to use in GCP
}

/*
    Resource blocks in terraform define infrastructure objects to create within the provier. Available options
    are listed on the documentation for a specific provier. The README.md file has a link to resources specific
    to Google Cloud. The second argument is a local name for the resource, which must be unique within the project.
    This is to delineate if you are defining multiple instances of a resource in the terraform project.
*/
# google_storage_bucket: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket
resource "google_storage_bucket" "demo-bucket" { # Creates a google_storage_bucket resource instance
  name          = var.gcs_bucket_name # Name to create GCS bucket under
  location      = var.location # Location for resource creation
  force_destroy = true # If true, delete all contained objects on terraform destroy; if false, will error if objects exist

  lifecycle_rule { # Rules that apply over the lifecycle of a resource. Can involve deleting, stopping operations, etc.
    condition { # Condition that triggers rule. In this case, it is an operation time of 1 day
      age = 1 # Age of an object in days to trigger the ruls
    }
    action { # Action that is performed if the condition is met
      type = "AbortIncompleteMultipartUpload" # Stop MultipartUpload instance if loading large dataset in parallel
    }
  }
}

# google_bigquery_dataset: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_dataset
resource "google_bigquery_dataset" "demo_dataset" {
  dataset_id = var.bq_dataset_name # Name for big query dataset
  location   = var.location # Location for big query dataset
}