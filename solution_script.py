import quandl
from datetime import datetime
from datetime import timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


API_KEY ='' # Your API Key
quandl.ApiConfig.api_key = API_KEY
QUANDL_CODE = '' #Quadl code of the equity you want to track
EMAIL = '' # Your email

def get_time_delta_days(today):
    #Monday is 0 and Sunday is 6
    weekday = today.weekday()
    if weekday == 6 or weekday == 0:
        #if weekday is Sunday or Monday
        return (0,0)
    elif weekday == 1:
        #If weekday is Tuesday
        return (4,1)
    else:
        #If weekday is between Wednesday and Friday
        return (2,1)


def get_equity_data_today_yesterday(quandl_code):
    today = datetime.now()
    time_delta_start_date,time_delta_end_date = get_time_delta_days(today)
    if time_delta_start_date == 0:
        print('Percentage change cannot be found on the weekend as there is no data.')
        return None
    start_td = timedelta(days=time_delta_start_date)
    end_td = timedelta(days=time_delta_end_date)
    start_date = today -  start_td
    end_date = today -  end_td
    equity_data = quandl.get(quandl_code,start_date=start_date.date(),end_date=end_date.date())
    return equity_data

def get_percentange_change(equity_data):
    percentage_change = equity_data['Adj_Close'].pct_change(1)
    return percentage_change[-1]


def send_email(email,quandl_code,percentage_change):

	subject= 'Percentage Change Notifier'

	html ="""
		<html>
		  <head></head>
		  <body>
            <b>Quandl Code:</b>  {0} <br/>
			<b>Percentage Change:</b>  {1}
		  </body>
		</html>
	""".format(quandl_code,percentage_change)

	email_body = html
	# Gmail Sign In
    gmail_sender = '' #Your Email
    gmail_passwd = '' #Your Password

	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.ehlo()
	server.starttls()
	server.login(gmail_sender, gmail_passwd)

	msg = MIMEMultipart('alternative')
	msg['Subject'] = subject
	msg['From'] = gmail_sender
	msg['To'] = email
	msg.attach(MIMEText(email_body, 'html'))
	try:
		server.sendmail(gmail_sender, [email], msg.as_string())
		print ('email sent')
	except:
		print ('error sending mail')

	server.quit()

if __name__ == '__main__':
    quandl_equity_code = QUANDL_CODE
    data = quandl.get(quandl_equity_code,start_date='2017-01-01',end_date='2018-01-30')
    threshold = abs(data['Adj_Close'].pct_change(1).mean())

    equity_data = get_equity_data_today_yesterday(quandl_equity_code)
    if equity_data is not None:
        percentage_change = get_percentange_change(equity_data)
    else:
        percentage_change = None
    if percentage_change is not None:
        notify = False
        if abs(percentage_change) >= threshold:
            notify = True
        if notify:
            send_email(EMAIL,quandl_equity_code,percentage_change)
