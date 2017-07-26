
from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Other Reports"),
			"icon": "icon-star",
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Purchase Order Details",
					"doctype": "Purchase Order"
				},
			]
		},
	]

