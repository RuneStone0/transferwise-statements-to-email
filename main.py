import yaml
import requests
import base64
from datetime import date, timedelta
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)
from os import environ

def trigger(request, config=None):
	# Config
	if config is None:
		print(" Loading config from environment variables")
		config = {
			"TW_API_URL": environ.get('TW_API_URL'),
			"TW_API_KEY": environ.get('TW_API_KEY'),
			"TW_PROFILE_ID": environ.get('TW_PROFILE_ID'),
			"TW_BORDERLESS_ACCOUNT_ID": environ.get('TW_BORDERLESS_ACCOUNT_ID'),
			"TW_CURRENCIES": environ.get('TW_CURRENCIES'),
			"TO_EMAIL": environ.get('TO_EMAIL'),
			"FROM_EMAIL": environ.get('FROM_EMAIL'),
			"SendGrid_KEY": environ.get('SendGrid_KEY')
		}
	else:
		print(" * Loading config from config.yaml")

	def get_statement(profile_id, borderless_account_id, currency, interval_start, interval_stop, format="pdf"):
		s = requests.session()
		s.headers.update({})  # Clear headers
		s.headers.update({"Authorization": "Bearer {}".format(config["TW_API_KEY"])})  # Add API key
		url = "{0}/v3/profiles/{1}/borderless-accounts/{2}/statement.{3}?currency={4}&intervalStart={5}&intervalEnd={6}".format(config["TW_API_URL"],
			profile_id,
			borderless_account_id,
			format,
			currency,
			interval_start,
			interval_stop)
		print(" * Fetching {} account statement ".format(currency))
		data = s.get(url, stream=True)
		return data.raw

	# Fetch all files from TW
	files = {}
	last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)
	start_day_of_prev_month = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)
	for currency in config["TW_CURRENCIES"].split(','):
		_file = get_statement(
			profile_id=config["TW_PROFILE_ID"],
			borderless_account_id=config["TW_BORDERLESS_ACCOUNT_ID"],
			currency=currency,
			interval_start="{}T00:00:00.000-07:00".format(start_day_of_prev_month),
			interval_stop="{}T00:00:00.000-08:00".format(last_day_of_prev_month))
		files[currency] = _file.data

	# Prepare email
	message = Mail(from_email=config["FROM_EMAIL"], to_emails=config["TO_EMAIL"], subject="TransferWise Account Statements", html_content="body")

	# Append all attachments to email
	for f in files:
		encoded_file = base64.b64encode(files[f]).decode()
		attachedFile = Attachment(
			FileContent(encoded_file),
			FileName('statement-{}.pdf'.format(f)),
			FileType('application/pdf'),
			Disposition('attachment')
		)
		message.attachment = attachedFile

	try:
		print(" * Sending email")
		sg = SendGridAPIClient(config["SendGrid_KEY"])
		sg.send(message)
		return "", 200
	except Exception as e:
		print(e)
		return "", 500


if __name__ == '__main__':
	""" Only used when running locally """
	with open("config.yaml", 'r') as ymlfile:
		config = yaml.load(ymlfile, Loader=yaml.BaseLoader)
	#trigger(None, config=config)
	trigger(None)
