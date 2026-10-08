import frappe
from frappe import _
from frappe.model.document import Document


class theatreseat(Document):
	def before_naming(self):
		self.seat_name = (self.seat_name or "").strip()

	def validate(self):
		self.row_alphabet = (self.row_alphabet or "").strip().upper()
		if not self.row_alphabet:
			frappe.throw(_("Row is required."))
		if not self.seat_number or self.seat_number < 1:
			frappe.throw(_("Seat Number must be greater than zero."))
		if frappe.db.exists(
			"theatre seat",
			{"theatre": self.theatre, "row_alphabet": self.row_alphabet, "seat_number": self.seat_number, "name": ["!=", self.name]},
		):
			frappe.throw(_("This seat already exists for the selected theatre."))
