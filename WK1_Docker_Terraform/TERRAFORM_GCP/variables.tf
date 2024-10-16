/*
    Variables allow you to customize modules without altering source code. The variable name must be unique among all 
    variables within a project. The default keyword gives the default variable value when the code is ran. The description
    keyword provides a description of the variable purpose. Other keywords such as type (specify value types allowed)
    can be added in the definition. Default values can be overwritten when running terraform apply by adding the -var 
    option on the command line. In this file, all variables provided are input variables, but there are also output
    variables and local values. Details on these can be found via the documentation link for variable in the README.md
    file.

    Variables must be defined in the variables.tf file to be accessible to the terraform project. Default values will
    be used during execution, or variable values must be provided at execution for the project to run. For cases in
    development or production where you want to run with specific variable values, a .tfvars file can be created that
    is a list of variables and values in the following syntax

    [variable_name] = [variable value]

    When executing terraform apply, you can add the -var-file argument to run the instance with the variables
    specified in the file

    terraform apply -var-file="<your_var_file>.tfvars"
*/
variable "credentials" { # Path to service account credentials file
  description = "My Credentials"
  default     = ""
}

variable "project" { # Define project ID; this is a unique value from Gcloud across all projects
  description = "Project"
  default     = ""
}

variable "region" { # Define region for projects, should be closest to deployment location to reduce latency
  description = "Region"
  # Update the below to your desired region
  default     = ""
}

variable "location" { # Country location for project
  description = "Project Location"
  # Update the below to your desired location
  default     = ""
}

variable "bq_dataset_name" { # Name for Big Query Dataset
  description = "My BigQuery Dataset Name"
  # Update the below to what you want your dataset to be called
  default     = "test_bq_dataset" # NOTE: "-" is not allowed, use underscores instead
}

/*
  NOTE: Bucket names must be globally unique across all of gcloud. Prefixing with the globally unique project
  name will allow your bucket name to be globally unique 
*/
variable "gcs_bucket_name" {
  description = "My Storage Bucket Name"
  # Update the below to a unique bucket name
  default     = "<your-project-name>-test-terraform-bucket"
}

variable "gcs_storage_class" { # Storage class type for bucket storage
  description = "Bucket Storage Class"
  default     = "STANDARD" # Types defined here: https://cloud.google.com/storage/docs/storage-classes
}