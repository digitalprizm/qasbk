from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
	columns, data = [], []
	columns = get_colums()
	data = get_data(filters)
	validate_filters(filters)

	return columns, data

def validate_filters(filters):
	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date"))

def get_data(filters):
	conditions = ""
	if filters.get("supplier"): 
		conditions += " and supplier= '{0}'".format(filters.get("supplier"))

	query="""select name,transaction_date,supplier,base_grand_total,status,per_received,per_billed
			 FROM `tabPurchase Order` where (transaction_date between '{0}' 
			and '{1}')""".format(filters.get("from_date"),filters.get("to_date"))
	
	query += conditions
	
	dl = frappe.db.sql(query,as_list=1,debug=1)
	return dl
	
def  get_colums():
	columns = ["Purchase Order:Link/Purchase Order:190"]+["Date:Date:90"]+["Supplier:Link/Supplier:190"]\
	+["Grand Total:Currency/currency:140"]+["Status:select:125"]\
	+["% Received:Percent:80"]+["% Billed:Percent:80"]

	
	return columns
