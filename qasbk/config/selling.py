
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
				{
                                        "type": "doctype",
                                        "name": "Job Master",
                                        "description": _("Job Master Details"),
                },

			]
		},
		{
			"label": _("Other Reports"),
			"icon": "icon-star",
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Sales Register Detail",
					"doctype": "Sales Invoice"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Item-wise Sales Register Detail",
					"doctype": "Sales Invoice"
				},
			]
		},
	]

