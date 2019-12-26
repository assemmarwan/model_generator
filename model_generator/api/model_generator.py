import frappe


@frappe.whitelist(allow_guest=True)
def generate_model(fields, lang_config):
	pass
