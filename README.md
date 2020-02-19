# TransferWise account statements to email

As a business owner you'll have to provide your accountant with account statements every month.
This script automates this process by authenticating into your TransferWise account and deliver
the account statements directly to your inbox. Saving you at least 5 minutes every month..

The solution consist of a small Python script that's utilizing:
* SendGrid (API Key required - FREE)
* Google Cloud Platform
	* Cloud Functions (that will execute our Python code)
	* Cloud Scheduler (that will trigger the Cloud Function every month)

# Setup
Configure gcloud CLI
```
export PROJECT_ID=brilliantr-1
gcloud config set project ${PROJECT_ID}
```

Deploy Cloud Function
```
gcloud functions deploy transferwise-statements-to-email \
	--runtime python37 \
	--trigger-http \
	--allow-unauthenticated \
	--memory 128MB \
	--entry-point trigger \
	--env-vars-file config.yaml
```
Note down the URL. For example: https://us-central1-brilliantr-1.cloudfunctions.net/transferwise-statements-to-email

Deploy Cloud Scheduler
```
gcloud beta scheduler jobs create http transferwise-statements-to-email \
	--schedule "0 0 1 * *" \
	--uri https://us-central1-brilliantr-1.cloudfunctions.net/transferwise-statements-to-email \
	--http-method get \
	--time-zone "UTC"
```


# Setup (local)
```
git clone https://github.com/RuneStone0/transferwise-statements-to-email.git 
cd transferwise-statements-to-email
pip install -r requirements.txt

# Configure Environment
export TW_API_URL=https://api.transferwise.com
export TW_API_KEY=00000000-0000-0000-0000-000000000000
export TW_PROFILE_ID=0000000
export TW_BORDERLESS_ACCOUNT_ID=0000000
export TW_CURRENCIES=USD,EUR,DKK
export SendGrid_KEY=SG.ABCEFHHIJABCEFHHIJABCEFHHIJABCEFHHIJABCEFHHIJ
export TO_EMAIL=random@gmail.com
export FROM_EMAIL=random@gmail.com
```