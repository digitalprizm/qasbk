// Copyright (c) 2016, qasbk and contributors
// For license information, please see license.txt

frappe.query_reports["Purchase Order Details"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_days(frappe.datetime.get_today(), -30),
			"width": "80"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname":"supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier"
		},
		// 		{
		// 	"fieldname":"item",
		// 	"label": __("Item"),
		// 	"fieldtype": "Check",
		// }
	]
}
