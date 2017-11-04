# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe import _
from frappe.utils import flt
from frappe.model.meta import get_field_precision
from erpnext.accounts.report.sales_register.sales_register import get_mode_of_payments
from operator import itemgetter
from itertools import groupby
import operator
import time

def execute(filters=None):
	return _execute(filters)

def _execute(filters=None, additional_table_columns=None, additional_query_columns=None):
	if not filters: filters = {}
	columns = get_columns(additional_table_columns)

	
	item_list = get_items(filters, additional_query_columns)

	
	print item_list
	#convert time to HH:MM and update it in existing item list
	for i in item_list:
		item_list[item_list.index(i)]["posting_time"]=frappe.utils.get_time(i.posting_time).strftime("%H:%M")
		


	if item_list:
		itemised_tax, tax_columns = get_tax_accounts(item_list, columns)
	

	data = []
	for d in item_list:
		delivery_note = None
		if d.delivery_note:
			delivery_note = d.delivery_note
		elif d.so_detail:
			delivery_note = ", ".join(so_dn_map.get(d.so_detail, []))

		if not delivery_note and d.update_stock:
			delivery_note = d.parent

		row = [d.posting_date, d.posting_time,d.parent,d.customer_name,d.item_code, d.qty]

		if additional_query_columns:
			for col in additional_query_columns:
				row.append(d.get(col))

		row += [d.base_net_rate, d.base_net_amount]

		total_tax = 0
		for tax in tax_columns:
			item_tax = itemised_tax.get(d.name, {}).get(tax, {})
			row += [item_tax.get("tax_rate", 0), item_tax.get("tax_amount", 0)]
			total_tax += flt(item_tax.get("tax_amount"))

		row += [total_tax, d.base_net_amount + total_tax]


		data.append(row)
	total_tax=0.00
	total_grand=0.00
	# total_outstanding=0.00
	for i in data:
			total_tax =total_tax +i[7]
			total_grand =total_grand +i[8]
			# total_outstanding2 =total_outstanding2 +i[6]

	a = list(sorted(data,key=itemgetter(4)))
	my_new_list = []
	
	for k, items in groupby(a, itemgetter(4)):
		print "k=",k
		grand = 0.00
		paid = 0.00
		

		for i in items:
			grand += i[7]
			paid += i[8]
			# os += i[6]
			# my_new_list.append(i)

			my_new_list.append([i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8]])
		my_new_list.append(["","","","","","","<b>Total</b>",grand,paid])
		# my_new_list.append(["","","","",k,"",""])
	
	my_new_list.append(["","","","","","",""])

	my_new_list.append(["","","","","","","<b> Net Total</b>",total_tax,total_grand])
	my_new_list.append(["","","","","","",""])
	my_new_list.append(["","","","","","",""])
	# my_new_list.append(["","","","","<b> ITEM</b>","<b> QTY</b>","<b> AMOUNT</b>"])


 	
	for k, items in groupby(a, itemgetter(0)):
		print "k=",k
		qty = 0.00
		# paid = 0.00
		
		for i in items:
			# qty += i[1]
			print("qty",qty)
			# paid += i[8]
			# my_new_list.append(["","","","","",qty,"","",""])
		# my_new_list.append(["","","","","",grand2,""])
		# my_new_list.append(["","","","",k,"","","",""])
	return columns, my_new_list

def get_columns(additional_table_columns):
	columns = [
		_("Posting Date") + ":Date:81",_("Posting Time") + ":Time:81",
		_("Invoice") + ":Link/Sales Invoice:100",_("Customer Name") + ":Link/Customer:100",
		_("Item Code") + ":Link/Item Code:100",
		_("Quantity") + ":Float:70", 
		
		# _("Vehicle No") + "::80",
		# _(" Rate")+"Currency:80",
		# _(" Net Total")+"Currency/currency:100"

		]
		# _("Posting Time") + ":Time:120",]

	# columns += ["Posting Time:Time/Time:100"]

	if additional_table_columns:
		columns += additional_table_columns


	return columns

def get_conditions(filters):
	conditions = ""

	for opts in (("company", " and company=%(company)s"),
		("customer", " and `tabSales Invoice`.customer = %(customer)s"),
		("item_code", " and `tabSales Invoice Item`.item_code = %(item_code)s"),
		("from_date", " and `tabSales Invoice`.posting_date>=%(from_date)s"),
		("to_date", " and `tabSales Invoice`.posting_date<=%(to_date)s")):
			if filters.get(opts[0]):
				conditions += opts[1]

	# if filters.get("mode_of_payment"):
	# 	conditions += """ and exists(select name from `tabSales Invoice Payment`
	# 		where parent=si.name
	# 			and ifnull(`tabSales Invoice Payment`.mode_of_payment, '') = %(mode_of_payment)s)"""

	return conditions

def get_items(filters, additional_query_columns):
	conditions = get_conditions(filters)
	match_conditions = frappe.build_match_conditions("Sales Invoice")
	
	if match_conditions:
		match_conditions = " and {0} ".format(match_conditions)
	
	if additional_query_columns:
		additional_query_columns = ', ' + ', '.join(additional_query_columns)

	return frappe.db.sql("""
		select

			`tabSales Invoice`.posting_date,
			`tabSales Invoice`.posting_time,
			`tabSales Invoice Item`.parent,
			`tabSales Invoice`.customer_name,
			`tabSales Invoice Item`.item_code,
			`tabSales Invoice Item`.qty,
			`tabSales Invoice Item`.base_net_rate,
			`tabSales Invoice Item`.base_net_amount, 
			`tabSales Invoice`.grand_total,
		    `tabSales Invoice`.base_net_total,
		    `tabSales Invoice Item`.item_name
			
			
			
		from `tabSales Invoice`, `tabSales Invoice Item`
		where `tabSales Invoice`.name = `tabSales Invoice Item`.parent
			and `tabSales Invoice`.docstatus = 1 %s %s
		order by `tabSales Invoice`.posting_date desc, `tabSales Invoice Item`.item_code
		""".format(additional_query_columns or '') % (conditions, match_conditions), filters, as_dict=1)

# def get_delivery_notes_against_sales_order(item_list):
# 	so_dn_map = frappe._dict()
# 	so_item_rows = list(set([d.so_detail for d in item_list]))

# 	if so_item_rows:
# 		delivery_notes = frappe.db.sql("""
# 			select parent, so_detail
# 			from `tabDelivery Note Item`
# 			where docstatus=1 and so_detail in (%s)
# 			group by so_detail, parent
# 		""" % (', '.join(['%s']*len(so_item_rows))), tuple(so_item_rows), as_dict=1)

# 		for dn in delivery_notes:
# 			so_dn_map.setdefault(dn.so_detail, []).append(dn.parent)

# 	return so_dn_map

def get_tax_accounts(item_list, columns,
		doctype="Sales Invoice", tax_doctype="Sales Taxes and Charges"):
	import json
	item_row_map = {}
	tax_columns = []
	invoice_item_row = {}
	itemised_tax = {}

	tax_amount_precision = get_field_precision(frappe.get_meta(tax_doctype).get_field("tax_amount")) or 2

	for d in item_list:
		invoice_item_row.setdefault(d.parent, []).append(d)
		item_row_map.setdefault(d.parent, {}).setdefault(d.item_code, []).append(d)


	conditions = ""
	if doctype == "Purchase Invoice":
		conditions = " and category in ('Total', 'Valuation and Total')"

	tax_details = frappe.db.sql("""
		select
			parent, description, item_wise_tax_detail,
			charge_type, base_tax_amount_after_discount_amount
		from `tab%s`
		where
			parenttype = %s and docstatus = 1
			and (description is not null and description != '')
			and parent in (%s)
			%s
		order by description
	""" % (tax_doctype, '%s', ', '.join(['%s']*len(invoice_item_row)), conditions),
		tuple([doctype] + invoice_item_row.keys()))

	for parent, description, item_wise_tax_detail, charge_type, tax_amount in tax_details:
		if description not in tax_columns and tax_amount:
			tax_columns.append(description)

		if item_wise_tax_detail:
			try:
				item_wise_tax_detail = json.loads(item_wise_tax_detail)

				for item_code, tax_data in item_wise_tax_detail.items():
					itemised_tax.setdefault(item_code, frappe._dict())

					if isinstance(tax_data, list):
						tax_rate, tax_amount = tax_data
					else:
						tax_rate = tax_data
						tax_amount = 0

					if charge_type == "Actual" and not tax_rate:
						tax_rate = "NA"

					item_net_amount = sum([flt(d.base_net_amount)
						for d in item_row_map.get(parent, {}).get(item_code, [])])

					for d in item_row_map.get(parent, {}).get(item_code, []):
						item_tax_amount = flt((tax_amount * d.base_net_amount) / item_net_amount) \
							if item_net_amount else 0
						if item_tax_amount:
							itemised_tax.setdefault(d.name, {})[description] = frappe._dict({
								"tax_rate": "NA",
								"tax_amount": flt(item_tax_amount, tax_amount_precision)
							})

			except ValueError:
				continue
		elif charge_type == "Actual" and tax_amount:
			for d in invoice_item_row.get(parent, []):
				itemised_tax.setdefault(d.name, {})[description] = frappe._dict({
					"tax_rate": "NA",
					"tax_amount": flt((tax_amount * d.base_net_amount) / d.base_net_total,
						tax_amount_precision)
				})

	tax_columns.sort()
	for desc in tax_columns:
		columns.append( " Rate:Currency:80")
		columns.append(" Net Total:Currency/currency:100")

	 

	columns += ["Tax:Currency/currency:80", "Grand Total:Currency/currency:100"]

	return itemised_tax, tax_columns
