## Course Project
This repo is the final project for the [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) 2023 by [DataTalks.Club](datatalks.club). The goal of this project is to apply everything I learned in this course among 7 weeks and build an end-to-end data pipeline. The project will covers the scope of data engineering (build the ETL data pipeline) & data science (build the data dashboard). Much appreciated to the DataTalks team, prepare the course in [Youtube Video](https://www.youtube.com/watch?v=-zpVha7bw5A&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb) & Github code, also provide [Slack Channel](https://datatalks.club/slack.html) to reply the inquiry. 

### Problem statement

For the project, the dataset to be use is the [ChatGPT - Youtube Data](https://www.kaggle.com/datasets/dekomorisanae09/chatgpt-youtube-analysis-data) from kaggle.

* Create a pipeline for processing this dataset and putting it to a datalake
* Create a pipeline for moving the data from the lake to a data warehouse
* Transform the data in the data warehouse: prepare it for the dashboard
* Create a dashboard

### Technologies 

* Cloud: Google Cloud Platform (GCP).
* Infrastructure as code (IaC): Terraform.
* Containerization: Docker.
* Workflow orchestration: Prefect.
* Data Wareshouse: BigQuery.
* Data Transformation: dbt cloud
* Batch processing: Spark.

## Pre-requistes Setup
The project use Google Cloud Platform, including Cloud Storage and BigQuery. 
1. Create a [Google Cloud Platform](https://cloud.google.com/) service account.
2. Create a new project from the dropdown menu, and note down the project ID.
   * Make the project ID unique
   * Go to project, under *IAM & Admin*, click on *Service Accounts*.
3. Setup Service account & authentification, and download Service Account Credential file (.json) for auth. 
   * Go the actions -> *Manage Keys* -> *ADD KEY*
   * Keep ```.json```
   * Download the ```generated.json```
   * Rename it to ```google_credentials.json``` and store it in your local folder. 
4. Download the Google Cloud [SDK](https://cloud.google.com/sdk/docs/quickstart) for local setup.
   ``` shell 
   export GOOGLE_APPLICATION_CREDENTIALS="<path/to/your/service-account-authkeys>.json" 
   # Refresh token/session, and verify authentication
   gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS
   # Login
   gcloud auth application-default login
   # Then Google knows this is your key, and done the local computer can interact with the cloud.
   gcloud init
   ```
5. Setup for Access, enable API to interact between local environment and the cloud environment.
   * Go to the IAM section of [IAM & Admin](https://console.cloud.google.com/iam-admin/iam)
   * Click the *Edit* principal icon for service account.
   * Add these roles in addition to *Viewer*: 
      * Storage Admin
      * Storage Object Admin
      * BigQuery Admin
   * Also activate the following APIs:
      * https://console.cloud.google.com/apis/library/iam.googleapis.com
      * https://console.cloud.google.com/apis/library/iamcredentials.googleapis.com
   * If you need further instructions, Please check out the links below:
      * [GCP Setup](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/week_1_basics_n_setup/1_terraform_gcp/2_gcp_overview.md)
      * [Video Introduction of GCP](https://www.youtube.com/watch?v=18jIzE41fJ4&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=3)

## Local Setup for Terraform & GCP
1. Download the latest version for [Terraform](https://www.terraform.io/downloads)
2. Unzip the file and put in under local C drive.
3. Check Terraform version: ```terraform -version```
4. For more instructions, please check [Terraform Overview](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/week_1_basics_n_setup/1_terraform_gcp/1_terraform_overview.md).

![image](https://user-images.githubusercontent.com/88218047/227323239-e0b17c8c-8680-4a36-8a7e-394a3ddc512d.png)


### Execution steps
1. ``` terraform init ```: 
   * Initializes & configures the backend, installs plugins/provider. Make sure you have two main configuration files ```main.tf``` and ```variable.tf``` under ```ls```.
2. ``` terraform plan ```:
   * Matches changes against a remote state, e.g. if you add another resource.
3. ``` terraform apply ```:
   * Apply changes to the cloud

## Workflow Orchestration using Prefect
Start the Prefect Orion server locally
1. Clone the repo locally.
2. Create a conda environment. ```conda create -n zoom python=3.9```
3. Install the requirements found in *requirements.txt* ```pip install -r requirements.txt```
3. Run the script: ```$ python flows/02_gcp/etl_web_to_gcs_final.py```
4. Then open the source UI to visual. ```python orion start``` 
5. Paste the url to the browser. ```prefect config set PREFECT_API_URL="http://127.0.0.1:4200/api"```
6. You should able to see that Prefect has successfully completed the flow by download the GZ file from Data Source, Unzip the GZ file to get the dataset, and convert the dataset to .csv format.

![image](https://user-images.githubusercontent.com/88218047/227322470-64ccf98c-afe0-42c3-9f75-622db1aa5980.png)

### Create Prefect GCP blocks & Perform the data ingestion
1. Adding blocks ***GCS Bucket*** from the interface Blocks of Orion.
2. Create a Block Name, Name of the bucket.
3. Under GCP Credentials, click on *Add+* button to create a Credentials with these informations.
3. Go the Google Cloud Console, select IAM & Admin, and Service Accounts. Then click on + CREATE SERVICE ACCOUNT with these informations: 
   * Click on CREATE AND CONTINUE button.
   * Give the roles BigQuery Admin and Storage Admin.
   * Click on DONE button.
   * Then create a key, select ```.json``` and click on CREATE button.
   * Back to Prefect, paste the info in Service Account Info.
   * Return the buckets and run ``` python flows/02_gcp/etl_gcs_to_bq_final.py```
4. It's now succussfully create a ETL to upload the GCP, and load data in BigQuery.

### Create a schedule to implement Batch Processing
1. Scheduling the flows and running the flows in containers in Dockers.
2. ```prefect deployment build flows/03_deployments/parameterized_flow.py:etl_parent_flow -n etl2 --cron "0 0 * * *"-a```
3. Make sure to have Dockerfile and docker-requirements.txt
4. ```docker image build -t finalproject/prefect:zoom .```
5. ``` docker image push finalproject/prefect:zoom .```
6. Go to the Orion UI, select Blocks in the right menu, click the + button to add a Docker Container with these information:
	* Block Name: zoom
	* Type (Optional) > The type of infrastructure: docker-container
	* Image (Optional) > Tag of a Docker image to use: finalproject/prefect:zoom
	* ImagePullPolicy (Optional): ALWAYS
	* Auto Remove (Optional): ON
   * Then click on Create button.
7. Run the deployment file from command line. ```python flows/03_deployments/docker_deploy.py```
8. Then we should see *docker-flow* under ***Deployment***.
9. Running Tasks in Docker: ```$ prefect deployment run etl-parent-flow/docker-flow -p "months=[1,2]"```

Further instructions: https://github.com/discdiver/prefect-zoomcamp

## Setting dbt Cloud
1. Go to GCP [create service account](https://console.cloud.google.com/apis/credentials/wizard) for dbt.
2. Grand specific roles and create the .JSON file.
3. Create a [dbt cloud account](https://www.getdbt.com/signup/)
4. Under ***Settings*** click on *Upload a Service Account JSON file*
5. Scroll down to the end of the page and set up your development credentials, then test connection.
6. Git clone from the repo, under Github repo Settings, you will get your deploy keys. 
7. Go the dbt cloud, and then *Initialize dbt project*
8. Create a new job in Deploy ***Environment***
9. The execution steps for dbt:
   * ```dbt run ```


Further instuctions: [setup dbt cloud with bigquery](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/week_4_analytics_engineering/dbt_cloud_setup.md)


## Dashboard
Visualising data with Google Data Studio
1. Go to [Google data studio](https://lookerstudio.google.com/u/0/)
2. Create a data source. 
3. Select BigQuery.
4. Authorize Looker Studio to connect to your BigQuery projects.
5. Select project id & connect

![image](https://user-images.githubusercontent.com/88218047/227397441-9e0b8304-822f-4591-8133-3befe33e36a4.png)
![image](https://user-images.githubusercontent.com/88218047/227824115-004d10a4-d221-455e-9ea8-59a649ec6ab0.png)
