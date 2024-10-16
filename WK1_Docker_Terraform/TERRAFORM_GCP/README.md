# Terraform

The `main.tf` and `variables.tf` files are documented with information on the various terraform objects as well as what is being performed. Note that the `variables.tf` file will need to be replaced with your variable values in order to run.

There was an additional section in the course that did not use a `variables.tf` file, however this was skipped in these notes as it covered the same content with the variables passed directly as values in `main.tf`.

Remember if you do not pass credentials as a variable in terraform, you will need to run the following command in your shell session to enable authentication. 
```bash
$ export GOOGLE_AUTHENTICATION_CREDENTIALS="<path/to/your/service-account-authkeys>.json"
```

One advantage of using a credentials variable is that it can easily be swapped to a different service account key in the case of multiple accounts or projects

## Terraform Components

The following are links to Terraform documentation on the object types used in the `main.tf` and `variables.tf` files. Information on Google Cloud specific resources from terraform is also linked
* [providers](https://developer.hashicorp.com/terraform/language/providers)
* `required_providers` [block](https://developer.hashicorp.com/terraform/language/providers/requirements)
* [resource](https://developer.hashicorp.com/terraform/language/resources/syntax)
* [variable](https://developer.hashicorp.com/terraform/language/values/variables)
* [Google Cloud Provider/Resources](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
* [`lifecycle_rule` for Gcloud](https://cloud.google.com/storage/docs/lifecycle#configuration)

## Executing a Terraform Project

The following command will initialize terraform, configure the backend, install necessary plugins, and obtain the configuration specified for providers
```bash
$ terraform init
```

Running the following command creates a proposed execution plan for object creation and configuration as defined in the `main.tf` file. This will output the proposed exectuion plan to console for review, and summarizes additions, changes, and destructions to be performed in Gcloud
```bash
$ terraform plan
```

The following command will implement the plan and deploy the additions, changes, or destructions in Gcloud
```bash
$ terraform apply
```

To remove the project from the cloud, the following command is used to remove what was applied to Gcloud. It is good practice to run this when done executing to prevent charges from use
```bash
$ terraform destroy
```