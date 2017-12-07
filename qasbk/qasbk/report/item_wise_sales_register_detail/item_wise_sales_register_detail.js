// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Item-wise Sales Register Detail"] = frappe.query_reports["Sales Register"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"width": "80"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname":"from_time",
			"label": __("From Time"),
			"fieldtype": "Time",
			"default": "00:00",
			"width": "80"
		},
		{
			"fieldname":"to_time",
			"label": __("To Time"),
			"fieldtype": "Time",
			"default": "23:59:59",
			"width": "80"
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		}
	],
	"formatter":function (row, cell, value, columnDef, dataContext, default_formatter) {
	    value = default_formatter(row, cell, value, columnDef, dataContext);
	   if (columnDef.id != "Invoice" && columnDef.id != "Item Code" && dataContext["Item Code"] == "") {
	   		value = "<span style='color:black!important;font-weight:bold'>" + value + "</span>";
	   }
	   // else{
	   // 		value = "<span style='color:black!important;font-weight:bold'>" + value + "</span>";
	   // }
	   return value;
	}
}
