# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "qasbk"
app_title = "qasbk"
app_publisher = "qasbk"
app_description = "qasbk"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "k.s@gmail.com"
app_license = "MIT"
hide_in_installer = True

fixtures = ['Custom Field', 'Property Setter', "Custom Script","Print Format"]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/qasbk/css/qasbk.css"
# app_include_js = "/assets/qasbk/js/qasbk.js"

# include js, css files in header of web template
# web_include_css = "/assets/qasbk/css/qasbk.css"
# web_include_js = "/assets/qasbk/js/qasbk.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "qasbk.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "qasbk.install.before_install"
# after_install = "qasbk.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "qasbk.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# after_insert
doc_events = {
	"Quotation": {
		"after_insert": "qasbk.qasbk.custom_methods.share_doc_with_owner",
		"validate": "qasbk.qasbk.custom_methods.validate_share"
	},
	"Sales Order": {
		"after_insert": "qasbk.qasbk.custom_methods.share_doc_with_owner",
		"validate": "qasbk.qasbk.custom_methods.validate_share"
	},
	"Delivery Note": {
		"after_insert": "qasbk.qasbk.custom_methods.share_doc_with_owner",
		"validate": "qasbk.qasbk.custom_methods.validate_share"
	},
	"Sales Invoice": {
		"after_insert": "qasbk.qasbk.custom_methods.share_doc_with_owner",
		"validate": "qasbk.qasbk.custom_methods.validate_share"
	},
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"qasbk.tasks.all"
# 	],
# 	"daily": [
# 		"qasbk.tasks.daily"
# 	],
# 	"hourly": [
# 		"qasbk.tasks.hourly"
# 	],
# 	"weekly": [
# 		"qasbk.tasks.weekly"
# 	]
# 	"monthly": [
# 		"qasbk.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "qasbk.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "qasbk.event.get_events"
# }

