from firebase_utils import get_firebase_remote_config
from booking.models import EventBooking, EventBookingInvoice
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.core.mail import get_connection
from django.conf import settings
from django.template.loader import get_template
from django.utils.html import strip_tags
from django.template import Context
from drf_spirit.views import remove_extra_char
from multiprocessing.pool import ThreadPool
from io import BytesIO
from xhtml2pdf import pisa
from datetime import datetime, date
import inflect
import boto3
import math
import time

class InvoiceGenerator:
	def __init__(self):
		self.firebase_remote_config = get_firebase_remote_config()
		self.client = boto3.client('s3',aws_access_key_id = settings.BOLOINDYA_AWS_ACCESS_KEY_ID,aws_secret_access_key = settings.BOLOINDYA_AWS_SECRET_ACCESS_KEY)
		self.key = 'invoices/' 

	def start(self):
		try:
			igst = self.firebase_remote_config['parameters']['igst_percentage']['defaultValue']['value']
			event_bookings = EventBooking.objects.filter(invoice_sent=False,payment_status="success",state="booked").select_related('event')
			invoices_data = []
			for event_booking in event_bookings:
				print("starting")
				data = {}
				event_price = event_booking.event.price
				event_title = event_booking.event.title
				user_email = event_booking.user.email
				username = event_booking.user.username
				net_amount_payble, price, tax = self.get_price_breakup(event_price)
				data['price'] = price
				data['net_amount_payble'] = net_amount_payble
				data['tax'] = tax
				data['event_booking_id'] = event_booking.id
				data['payment_mode'] = event_booking.payment_mode
				data['consumer_id'] = event_booking.user_id
				data['event_creator_id'] = event_booking.event.creator.id
				data['igst_percentage'] = igst
				event_booking_invoice = EventBookingInvoice(**data)
				event_booking_invoice.save()

				response = self.create_pdf(event_booking_invoice.invoice_number, event_price, username, event_title, event_booking.payment_mode)
				response['title'] = event_title
				response['email'] = user_email
				response['username'] = username
				response['event_booking_id'] = event_booking_invoice.invoice_number
				self.send_email(response)
				invoice_url = self.upload_media(response)
				event_booking_invoice.invoice_pdf_url = invoice_url
				event_booking_invoice.save()
				event_booking.invoice_sent = True
				event_booking.save()
		except Exception as e:
			print("error")
			print(e)

	def create_pdf(self, invoice_number, price, username, description, payment_mode):
		netAmount, price, tax= self.get_price_breakup(price)
		context = {}
		context['net_amount_payble'] = netAmount
		context['price'] = price
		context['tax'] = tax
		context['net_amount_rounded_off'] = math.ceil(netAmount)
		context['amount_in_words'] = inflect.engine().number_to_words(netAmount)
		context['discount'] = 0
		context['gst_registration_no'] = self.firebase_remote_config['parameters']['gst_registration_no']['defaultValue']['value']
		context['company_name'] = self.firebase_remote_config['parameters']['company_name']['defaultValue']['value']
		context['company_pan_no'] = self.firebase_remote_config['parameters']['company_pan_no']['defaultValue']['value']
		context['description'] = description
		context['payment_mode'] = payment_mode
		context['invoice_date'] = datetime.today().strftime('%d-%m-%Y')
		context['invoice_number'] = invoice_number
		html = render_to_string('payment/invoice.html',context)
		pdf_file_name = 'invoice_{}_{}.pdf'.format(username, int(time.time()))
		pdf_path = '/tmp/'+pdf_file_name
		write_to_file = open(pdf_path, "w+b")   
		result = pisa.CreatePDF(html,dest=write_to_file)
		write_to_file.close()
		context['media_file'] = pdf_path
		context['file_name'] = pdf_file_name
		return context

	def get_price_breakup(self,price):
		igst = self.firebase_remote_config['parameters']['igst_percentage']['defaultValue']['value']
		tax_fraction = 1+float(igst)/100
		netAmount = price
		price = price / tax_fraction
		tax = netAmount - price
		return netAmount, round(price,2), round(tax,2)

	def send_email(self, data):
		if data['email']:
			connection = get_connection(host=settings.EMAIL_HOST, 
							port=settings.EMAIL_PORT, 
							username=settings.INVOICE_EMAIL_HOST_USER, 
							password=settings.INVOICE_EMAIL_HOST_PASSWORD, 
							use_tls=True)
			email_from = self.firebase_remote_config['parameters']['invoice_email_from']['defaultValue']['value']
			to_emails = [data['email']]
			subject = self.firebase_remote_config['parameters']['event_email_subject_prefix']['defaultValue']['value'] + " | "+ data['title']
			pdf_path = data['media_file']
			html_message = render_to_string('payment/email_body.html', {'username': data['username'], 'booking_id': data['event_booking_id']})
			plain_message = strip_tags(html_message)
			email = EmailMessage(subject, plain_message	, from_email=email_from, to=to_emails, connection=connection)
			email.attach_file(pdf_path)
			email.send()

	def upload_media(self,data):
		media_file = data['media_file']
		file_name = data['file_name']
		from jarvis.views import urlify
		ts = time.time()
		created_at = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
		media_file_name = remove_extra_char(str(file_name))
		final_filename = urlify(media_file_name)
		response = self.client.upload_file(media_file, settings.BOLOINDYA_EVENT_INVOICE_BUCKET_NAME,self.key + final_filename)
		filepath = 'https://s3.ap-south-1.amazonaws.com/' + settings.BOLOINDYA_EVENT_INVOICE_BUCKET_NAME + "/"+ self.key + final_filename
		return filepath

def run():
	InvoiceGenerator().start()
