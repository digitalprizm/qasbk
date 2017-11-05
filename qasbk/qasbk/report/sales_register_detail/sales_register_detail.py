# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, getdate, cstr
from frappe import msgprint, _
from operator import itemgetter
from itertools import groupby
import operator

def execute(filters=None):
	if not filters: filters = frappe._dict({})

	invoice_list = get_invoices(filters)
	columns, income_accounts, tax_accounts = get_columns(invoice_list)

	
	print invoice_list
	#convert time to HH:MM and update it in existing item list
	for i in invoice_list:
		invoice_list[invoice_list.index(i)]["posting_time"]=frappe.utils.get_time(i.posting_time).strftime("%H:%M")
		

	if not invoice_list:
		msgprint(_("No record found"))
		return columns, invoice_list

	invoice_income_map = get_invoice_income_map(invoice_list)
	invoice_income_map, invoice_tax_map = get_invoice_tax_map(invoice_list,
		invoice_income_map, income_accounts)

	invoice_so_dn_map = get_invoice_so_dn_map(invoice_list)
	customer_map = get_customer_details(invoice_list)
	company_currency = frappe.db.get_value("Company", filters.company, "default_currency")
	#mode_of_payments = get_mode_of_payments([inv.name for inv in invoice_list])

	data = []
	for inv in invoice_list:
		# invoice details
		# sales_order = list(set(invoice_so_dn_map.get(inv.name, {}).get("sales_order", [])))
		# delivery_note = list(set(invoice_so_dn_map.get(inv.name, {}).get("delivery_note", [])))

		row = [inv.name, inv.posting_date, inv.posting_time, inv.customer]

		# map income values
		base_net_total = 0
		# for income_acc in income_accounts:
		# 	income_amount = flt(invoice_income_map.get(inv.name, {}).get(income_acc))
		# 	base_net_total += income_amount
		# 	# row.append(income_amount)

		# # net total
		
		# # tax account
		# total_tax = 0
		# for tax_acc in tax_accounts:
		# 	if tax_acc not in income_accounts:
		# 		tax_amount = flt(invoice_tax_map.get(inv.name, {}).get(tax_acc))
		# 		total_tax += tax_amount
				# row.append(tax_amount)

		# total tax, grand total, outstanding amount & rounded total
		# row += [total_tax, inv.base_grand_total, inv.outstanding_amount]
		# row.append(inv.debit_to)
		row.append(inv.base_grand_total)
		row.append(inv.paid_amount)
		row.append(inv.outstanding_amount)
		row.append(inv.siitems)
		row.append(inv.served_by)
		row.append(inv.vehicle_no)
		# row.append(base_net_total or inv.base_net_total)

		# row.append(inv.gentlemen_ring_size)
		# row.append(inv.ladies_ring_size)
		# row.append(inv.engraving_text)
		# row.append(inv.engraving_font)
		data.append(row)
		total_paid=0
		total_grand=0
		total_outstanding=0

		for i in data:
			total_paid =total_paid +i[5]
			total_grand =total_grand +i[4]
			total_outstanding =total_outstanding +i[6]


	a = list(sorted(data,key=itemgetter(1)))
	my_new_list = []
	
	for k, items in groupby(a, itemgetter(1)):
		print "k=",k	
		# print items,"itemsas"
		
		grand = 0.00
		paid = 0.00
		os = 0.00

		for i in items:
			grand += i[4]
			paid += i[5]
			os += i[6]
			# my_new_list.append(i)

			my_new_list.append([i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8],i[9]])
		my_new_list.append(["","","","<b>Total</b>",grand,paid,os,"",""])
	
		# my_new_list.append(["","","","","","",""])
	my_new_list.append(["","","","","","",""])
	
	my_new_list.append(["","","","<b>Net Total:</b>",total_grand,total_paid,total_outstanding,"","",""])
	return columns, my_new_list


def get_columns(invoice_list):
	"""return columns based on filters"""
	columns = [
		_("Invoice") + ":Link/Sales Invoice:80", _("Posting Date") + ":Date:81",  _("Posting Time") + ":Time:81",
		_("Customer") + ":Link/Customer:80", 
		# _("Mode of Payment") + "::150",
		 
		# {
		# 	"fieldname": "currency",
		# 	"label": _("Currency"),
		# 	"fieldtype": "Data",
		# 	"width": 80
		# }
	]

	income_accounts = tax_accounts = income_columns = tax_columns = []

	if invoice_list:
		income_accounts = frappe.db.sql_list("""select distinct income_account
			from `tabSales Invoice Item` where docstatus = 1 and parent in (%s)
			order by income_account""" %
			', '.join(['%s']*len(invoice_list)), tuple([inv.name for inv in invoice_list]))

		tax_accounts = 	frappe.db.sql_list("""select distinct account_head
			from `tabSales Taxes and Charges` where parenttype = 'Sales Invoice'
			and docstatus = 1 and base_tax_amount_after_discount_amount != 0
			and parent in (%s) order by account_head""" %
			', '.join(['%s']*len(invoice_list)), tuple([inv.name for inv in invoice_list]))

	income_columns = [(account + ":Currency/currency:80") for account in income_accounts]
	for account in tax_accounts:
		if account not in income_accounts:
			tax_columns.append(account + ":Currency/currency:70")

	columns = columns  + \
		[ _("Grand Total") + ":Currency/currency:80",_("Paid Amount") + ":Currency/currency:90",
		_("Outstanding Amount") + ":Currency/currency:100",_("Items") + ":Data:120",
		_("Served By") + ":Data:85"]
	return columns, income_accounts, tax_accounts

def get_conditions(filters):
	conditions = ""

	if filters.get("company"): conditions += " and company=%(company)s"
	if filters.get("customer"): conditions += " and customer = %(customer)s"

	if filters.get("from_date"): conditions += " and posting_date >= %(from_date)s"
	if filters.get("to_date"): conditions += " and posting_date <= %(to_date)s"
	
	#if filters.get("mode_of_payment"):
	#	conditions += """ and exists(select name from `tabSales Invoice Payment`
	#		 where parent=`tabSales Invoice`.name 
	#		 	and ifnull(`tabSales Invoice Payment`.mode_of_payment, '') = %(mode_of_payment)s)"""
				
	return conditions

# def get_invoices(filters):
# 	conditions = get_conditions(filters)
# 	return frappe.db.sql("""select name, posting_date, debit_to, 
# 		project, customer, customer_name, paid_amount, base_grand_total,
# 		base_rounded_total, 
# 		CASE WHEN 1 = 1 
# 		THEN 
# 		(select GROUP_CONCAT(item_name SEPARATOR ', ') as siitems from `tabSales Invoice Item` i where i.parent=`tabSales Invoice`.name group by i.parent)
# 		ELSE "" END AS siitems,
# 		case when 1 = 1 then (select full_name from `tabUser` u where u.name=`tabSales Invoice`.served_by) end as "served_by",
# 		outstanding_amount,vehicle_no
# 		from `tabSales Invoice`
# 		where docstatus = 1 %s order by posting_date desc, name desc""" %
# 		conditions, filters, as_dict=1)

def get_invoices(filters):
	conditions = get_conditions(filters)
	return frappe.db.sql("""select name, posting_date,posting_time,
		project, customer, customer_name, paid_amount, base_grand_total, 
		base_rounded_total, 
		CASE WHEN 1 = 1 
		THEN 
		(select GROUP_CONCAT(item_name SEPARATOR ', ') as siitems from `tabSales Invoice Item` i where i.parent=`tabSales Invoice`.name group by i.parent)
		ELSE "" END AS siitems,
		case when 1 = 1 then (select full_name from tabUser u where u.name=`tabSales Invoice`.owner) end as "served_by",
		outstanding_amount
		from `tabSales Invoice`
		where docstatus = 1 %s order by  name desc """ %
		# where docstatus = 1 %s order by posting_date desc, name desc """ %
		conditions, filters, as_dict=1)


def get_invoice_income_map(invoice_list):
	income_details = frappe.db.sql("""select parent, income_account, sum(base_net_amount) as amount
		from `tabSales Invoice Item` where parent in (%s) group by parent, income_account""" %
		', '.join(['%s']*len(invoice_list)), tuple([inv.name for inv in invoice_list]), as_dict=1)

	invoice_income_map = {}
	# for d in income_details:
	# 	invoice_income_map.setdefault(d.parent, frappe._dict()).setdefault(d.income_account, [])
	# 	invoice_income_map[d.parent][d.income_account] = flt(d.amount)

	return invoice_income_map

def get_invoice_tax_map(invoice_list, invoice_income_map, income_accounts):
	tax_details = frappe.db.sql("""select parent, account_head,
		sum(base_tax_amount_after_discount_amount) as tax_amount
		from `tabSales Taxes and Charges` where parent in (%s) group by parent, account_head""" %
		', '.join(['%s']*len(invoice_list)), tuple([inv.name for inv in invoice_list]), as_dict=1)

	invoice_tax_map = {}
	for d in tax_details:
		if d.account_head in income_accounts:
			if invoice_income_map[d.parent].has_key(d.account_head):
				invoice_income_map[d.parent][d.account_head] += flt(d.tax_amount)
			else:
				invoice_income_map[d.parent][d.account_head] = flt(d.tax_amount)
		else:
			invoice_tax_map.setdefault(d.parent, frappe._dict()).setdefault(d.account_head, [])
			invoice_tax_map[d.parent][d.account_head] = flt(d.tax_amount)

	return invoice_income_map, invoice_tax_map

def get_invoice_so_dn_map(invoice_list):
	si_items = frappe.db.sql("""select parent, sales_order, delivery_note, so_detail
		from `tabSales Invoice Item` where parent in (%s)
		and (ifnull(sales_order, '') != '' or ifnull(delivery_note, '') != '')""" %
		', '.join(['%s']*len(invoice_list)), tuple([inv.name for inv in invoice_list]), as_dict=1)

	invoice_so_dn_map = {}
	for d in si_items:
		if d.sales_order:
			invoice_so_dn_map.setdefault(d.parent, frappe._dict()).setdefault(
				"sales_order", []).append(d.sales_order)

		delivery_note_list = None
		if d.delivery_note:
			delivery_note_list = [d.delivery_note]
		elif d.sales_order:
			delivery_note_list = frappe.db.sql_list("""select distinct parent from `tabDelivery Note Item`
				where docstatus=1 and so_detail=%s""", d.so_detail)

		if delivery_note_list:
			invoice_so_dn_map.setdefault(d.parent, frappe._dict()).setdefault("delivery_note", delivery_note_list)

	return invoice_so_dn_map

def get_customer_details(invoice_list):
	customer_map = {}
	customers = list(set([inv.customer for inv in invoice_list]))
	for cust in frappe.db.sql("""select name, territory, customer_group from `tabCustomer`
		where name in (%s)""" % ", ".join(["%s"]*len(customers)), tuple(customers), as_dict=1):
			customer_map.setdefault(cust.name, cust)

	return customer_map


# def get_mode_of_payments(invoice_list):
# 	mode_of_payments = {}
# 	if invoice_list:
# 		inv_mop = frappe.db.sql("""select parent, mode_of_payment
# 			from `tabSales Invoice Payment` where parent in (%s) group by parent, mode_of_payment""" %
# 			', '.join(['%s']*len(invoice_list)), tuple(invoice_list), as_dict=1)

# 		for d in inv_mop:
# 			mode_of_payments.setdefault(d.parent, []).append(d.mode_of_payment)

# 	return mode_of_payments