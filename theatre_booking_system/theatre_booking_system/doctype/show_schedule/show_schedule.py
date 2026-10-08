import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class showschedule(Document):
	def validate(self):
		if getdate(self.show_date) < getdate(today()):
			frappe.throw(_("A show cannot be scheduled in the past."))
		if self.show_start_time >= self.show_end_time:
			frappe.throw(_("End Time must be after Start Time."))
		if not self.ticket_price or self.ticket_price <= 0:
			frappe.throw(_("Ticket Price must be greater than zero."))
		if not frappe.db.get_value("show", self.show, "is_active"):
			frappe.throw(_("Only active shows can be scheduled."))
		if not frappe.db.get_value("theatre", self.theatre, "active"):
			frappe.throw(_("Only active theatres can be scheduled."))

		overlap = frappe.db.sql(
			"""
				select name from `tabshow schedule`
				where theatre = %s and show_date = %s and name != %s
					and show_start_time < %s and show_end_time > %s
				limit 1
			""",
			(self.theatre, self.show_date, self.name, self.show_end_time, self.show_start_time),
		)
		if overlap:
			frappe.throw(_("This theatre already has an overlapping show.")) 
