import frappe
from frappe import _
from frappe.model.document import Document


class show(Document):
	def before_naming(self):
		self.show_name = (self.show_name or "").strip()

	def validate(self):
		self.show_name = (self.show_name or "").strip()
		if not self.show_name:
			frappe.throw(_("Title is required."))
		if not self.duration_minutes or self.duration_minutes < 1:
			frappe.throw(_("Duration must be at least one minute."))
