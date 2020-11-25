from firebase_utils import get_firebase_remote_config
from advertisement.models import Order, Product, OrderLine, OrderInvoice
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

class AdInvoiceGenerator:
	def __init__(self):
		self.firebase_remote_config = get_firebase_remote_config()
		self.client = boto3.client('s3',aws_access_key_id = settings.BOLOINDYA_AWS_ACCESS_KEY_ID,aws_secret_access_key = settings.BOLOINDYA_AWS_SECRET_ACCESS_KEY)
		self.key = 'ad_invoices/' 

	def start(self):
		try:
			igst = self.firebase_remote_config['parameters']['igst_percentage']['defaultValue']['value']
			orders = Order.objects.filter(is_invoice_sent=False,payment_status="success").prefetch_related('lines')
			invoices_data = []
			print(orders)
			for order in orders:
				print("starting")
				data = {}
				order_line = order.lines.all()[0]
				product_qty = order_line.quantity
				product_unit_mrp = order_line.product.mrp
				product_unit_tax = order_line.product.total_tax
				product_unit_discount = product_unit_mrp - order_line.product.discounted_price
				product_title = order_line.product.name
				net_amount_payble = order.amount_including_tax
				username = order.user.username
				user_email = order.user.email
				shipping_address = order.shipping_address
				data['order_id'] = order.id
				data['product_qty'] = product_qty
				data['unit_price'] = product_unit_mrp
				data['unit_tax'] = product_unit_tax
				data['igst_percentage'] = igst
				data['net_amount_payble'] = net_amount_payble
				data['payment_mode'] = order.payment_method
				data['unit_discount'] = product_unit_discount
				print(data)
				order_invoice = OrderInvoice(**data)
				order_invoice.save()
				invoice_number = order_invoice.invoice_number
				address = ''
				if shipping_address.address1:
					address+= shipping_address.address1+" "
				if shipping_address.address2:
					address+= shipping_address.address2+" "
				if shipping_address.address3:
					address+= shipping_address.address3	
				response = self.create_pdf(invoice_number, product_unit_mrp, product_unit_tax, net_amount_payble, username, product_title, address, product_qty, product_unit_discount)
				print("done")
				response['email'] = user_email
				response['username'] = username
				response['invoice_number'] = invoice_number
				response['product_title'] = product_title
				self.send_email(response)
				invoice_url = self.upload_media(response)
				order_invoice.invoice_pdf_url = invoice_url
				order_invoice.save()
				order.is_invoice_sent = True
				order.save()
		except Exception as e:
			print("error")
			print(e)

	def create_pdf(self, invoice_number, price, tax, netAmount, username, description, shipping_address, product_qty, product_unit_discount):
		context = {}
		context['net_amount_payble'] = netAmount
		context['price'] = price
		context['tax'] = tax
		context['net_amount_rounded_off'] = math.ceil(netAmount)
		context['amount_in_words'] = inflect.engine().number_to_words(math.ceil(netAmount))
		context['discount'] = product_unit_discount*product_qty
		context['gst_registration_no'] = self.firebase_remote_config['parameters']['gst_registration_no']['defaultValue']['value']
		context['company_name'] = self.firebase_remote_config['parameters']['company_name']['defaultValue']['value']
		context['company_pan_no'] = self.firebase_remote_config['parameters']['company_pan_no']['defaultValue']['value']
		context['description'] = description
		context['shipping_address'] = shipping_address
		context['invoice_date'] = datetime.today().strftime('%d-%m-%Y')
		context['invoice_number'] = invoice_number
		context['product_qty'] = product_qty
		context['total_amount'] = price*product_qty
		context['discounted_price'] = price - product_unit_discount
		html = render_to_string('advertisement/invoices/invoice.html',context)
		pdf_file_name = 'invoice_{}_{}.pdf'.format(username, int(time.time()))
		pdf_path = '/tmp/'+pdf_file_name
		write_to_file = open(pdf_path, "w+b")   
		result = pisa.CreatePDF(html,dest=write_to_file)
		write_to_file.close()
		context['media_file'] = pdf_path
		context['file_name'] = pdf_file_name
		return context

	def send_email(self, data):
		if data['email']:
			cc_email = 'support@boloindya.com'
			bcc_email = 'varun@careeranna.com'
			connection = get_connection(host=settings.EMAIL_HOST, 
							port=settings.EMAIL_PORT, 
							username=settings.INVOICE_EMAIL_HOST_USER, 
							password=settings.INVOICE_EMAIL_HOST_PASSWORD, 
							use_tls=True)
			email_from = self.firebase_remote_config['parameters']['invoice_email_from']['defaultValue']['value']
			to_emails = [data['email']]
			subject = "Order Confirmed" + " | "+ data['invoice_number']
			pdf_path = data['media_file']
			html_message = render_to_string('advertisement/invoices/email_body.html', {'username': data['username'], 'invoice_number': data['invoice_number'], 'product_name': data['product_title']})
			plain_message = strip_tags(html_message)
			print("sending email")
			print(to_emails)
			email = EmailMessage(subject, plain_message	, from_email=email_from, to=to_emails, bcc=[bcc_email], cc=[cc_email], connection=connection)
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
	AdInvoiceGenerator().start()
