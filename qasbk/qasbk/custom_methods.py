from __future__ import unicode_literals
import frappe
import logging
import string
import datetime
import re
import json

from frappe.utils import getdate, flt,validate_email_add, cint
from frappe.model.naming import make_autoname
from frappe import throw, _, msgprint
import frappe.permissions
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

_logger = logging.getLogger(frappe.__name__)

def share_doc_with_owner(doc, method):
	customer_owner = frappe.db.get_value("Customer",doc.customer,"owner")
	if doc.owner != customer_owner:
		frappe.share.add(doc.doctype, doc.name, customer_owner,write=1,flags={"ignore_share_permission": True})
		# frappe.msgprint(frappe.share.get_shared("Quotation", 't@t.com'))

def validate_share(doc,method):
	if not doc.get("__islocal") :	
		customer_owner = frappe.db.get_value("Customer",doc.customer,"owner")	
		if doc.owner != customer_owner:
			frappe.share.add(doc.doctype, doc.name, customer_owner,write=1,flags={"ignore_share_permission": True})