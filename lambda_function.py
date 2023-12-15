import smtplib
import os
import requests
import json
from datetime import datetime

from email.mime.text import MIMEText

gmail_account = os.environ.get('GMAIL_ACCOUNT')
gmail_password = os.environ.get('GMAIL_APP_PASSWORD')

def sendEmail(recipients, subject):
    try:
        body = f'''
        Hello,

        I hope this message finds you well. This email is a test to verify the functionality of our automated mailing system, implemented using Python and AWS Lambda.

        If you have received this email, it indicates that our system is functioning correctly. No further action is required on your part.

        Should you have any questions or if you encounter any issues with receiving this email, please do not hesitate to contact me at {gmail_account}.

        Thank you for your assistance in ensuring the reliability of our system.

        Best regards,
        '''

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = gmail_account
        msg['To'] = recipients

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(gmail_account, gmail_password)
            smtp_server.sendmail(gmail_account, recipients, msg.as_string())
        print('Email sent successfully!')

        return {
            'statusCode': 200,
            'message': 'Send email successfully!'
        }
    except:
        return {
            'statusCode': 400,
            'message': 'Send email failed!' 
        }

def sendSlackNotification(webhook_url, message):
    slack_data = {'text': message}

    response = requests.post(
        webhook_url, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code != 200:
        raise ValueError(f'Error sending to Slack: {response.status_code}, response: {response.text}')

def checkIsMondayOrFriday():
    today = datetime.now().weekday()
    if (today == 0 or today == 4):
        return True
    
    return False

def lambdaHandler():
    isMondayOrFriday = checkIsMondayOrFriday()

    if (isMondayOrFriday == False):
        return {
            'statusCode': 200,
            'body': 'Today is not Monday or Friday'
        }

    subject = os.environ.get('MAIL_SUBJECT')
    recipients = os.environ.get("MAIL_RECIPIENTS")
    slack_webhook_url = os.environ.get('SLACK_HOOK_CHANNEL')

    result = sendEmail(recipients, subject)
    message = ''

    if result['statusCode'] == 200:
        message = f'Was sent email successfully to {recipients}'
       
    elif result['statusCode'] == 400:
        message = f'Can\'t send email to {recipients}'
    
    try:
        if slack_webhook_url is not None:
            sendSlackNotification(slack_webhook_url, message)

        return {
            'statusCode': result['statusCode'],
            'body': message
        }
    except:
        return {
            'statusCode': 400,
            'body': 'Send email and notification to Slack failed!'
        }