# dialogflow-mlapi

* Create Service Account
  * https://cloud.google.com/compute/docs/access/service-accounts#newserviceaccounts
  * Grant permission on Google Sheets(You have to create your own) to the service account
  * Change spreadsheetId to your Google Sheets in mlapi-webhook.py

* Create Key and download
  * http://console.cloud.google.com
  * IAM ==> Service Account ==> Choose Account ==> Create Key ==> Downlaod as JSON

* Specify downloaded Service Account Key
  * Place the key file(json) at current directory
  * Modify GOOGLE_APPLICATION_CREDENTIALS location in run_webhook.sh

* Install required Python library by referencing pip-list.txt

* Run run_webhook.sh

* How to guide: https://github.com/javalove93/dialogflow-mlapi/raw/master/How%20to%20install%20agent.pdf
