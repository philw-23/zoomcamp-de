# Week 0 - Setting Everything Up

This course was done on an Ubuntu 24.04 linux vm, so all tutorials, commands, and scripts in this repo are are based on this. 

## Installing Python

Many linux distributions come with python3 already installed, however the tutorial [here](https://docs.vultr.com/how-to-install-python-and-pip-on-ubuntu-24-04) can be followed if you want to install either the most current (or a previous) python version. It is highly reccomended to create a virtual environment for your python project to avoid package conflicts with other projects, and a tutorial for setting that up can be found [here](https://docs.python.org/3/library/venv.html). For this project, we created a virtual environment named `zoomcamp-env` was created in the top directory. The packages used in this course are included in the `requirements.txt` file in this folder, and can be installed by activating the virtual environment and running the following command in a terminal

```bash
$ pip install -r ./WK0_Setup/requirements.txt
```

## Additional Tools

The key tools for this course (Docker, Google Cloud SDK, and Terraform) can be isntalled by following the below links

* [Docker](https://docs.docker.com/engine/install/ubuntu/)
* [Google Cloud SDK](https://cloud.google.com/sdk/docs/install#deb)
* [Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)

You can then use the following commands to verify a successful install

* Docker: `docker run hello-world`
* Google Cloud SDK: `gcloud --version`
* Terraform: `terraform -v`

## Setting up a GCloud Project

Instructions can be found [here](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/01-docker-terraform/1_terraform_gcp/2_gcp_overview.md) on how to set up a project on google cloud for this course. The project used for this repo was named `de-zoomcamp-project`

Note that part of the instructions involve setting the envrionment variable `GOOGLE_APPLICATION_CREDENTIALS`. When this is set using the `export` command, it is only set for the current session and does not persist for future sessions. You can add it to startup by adding the `export` command to the `.bashrc` file in linux, however this may not be practical if you are working with multiple different service accounts. In many cases the service account keys can be stored in a file location and the path can be provided to the necessary credential manager. These use cases will be documented in later sections. Keys used in this couse were stored in a local `.keys/` directory of the virtual machine