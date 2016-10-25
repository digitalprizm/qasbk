
from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Sales"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Service",
					"description": _("Service For Customers or Suppliers"),
				},
				{
					"type": "doctype",
					"name": "Delivery Note",
					"description": _("Delivery Note for Customers."),
				},
			]
		},
	]

