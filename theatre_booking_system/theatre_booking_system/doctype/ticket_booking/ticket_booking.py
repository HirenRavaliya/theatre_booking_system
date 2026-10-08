import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, today


class ticketbooking(Document):
	def before_naming(self):
		self.booking_reference = (self.booking_reference or "").strip()

	def validate(self):
		schedule = frappe.db.get_value(
			"show schedule", self.show_schedule, ["theatre", "show_date", "ticket_price"], as_dict=True
		)
		if not schedule:
			frappe.throw(_("Select a valid Show Schedule."))
		if getdate(schedule.show_date) < getdate(today()):
			frappe.throw(_("Seats cannot be booked for a past show."))

		self.ticket_price = flt(schedule.ticket_price)
		self._validate_seats(schedule.theatre)
		self.amount_due = self.ticket_price * len(self.seats)

	def _validate_seats(self, theatre):
		if not self.seats:
			frappe.throw(_("Add at least one seat to the booking."))

		seat_keys = set()
		for seat in self.seats:
			seat.row_alphabet = (seat.row_alphabet or "").strip().upper()
			if not seat.row_alphabet or not seat.seat_number or seat.seat_number < 1:
				frappe.throw(_("Every booked seat requires a row and a positive seat number."))
			key = (seat.row_alphabet, seat.seat_number)
			if key in seat_keys:
				frappe.throw(_("A seat can only appear once in a booking."))
			seat_keys.add(key)
			if not frappe.db.exists(
				"theatre seat",
				{"theatre": theatre, "row_alphabet": seat.row_alphabet, "seat_number": seat.seat_number, "active": 1},
			):
				frappe.throw(_("Seat {0}{1} is not an active seat in this theatre.").format(seat.row_alphabet, seat.seat_number))

		if self.status == "Cancelled":
			return

		for row, number in seat_keys:
			reserved = frappe.db.sql(
				"""
					select bs.parent
					from `tabbook seat` bs
					inner join `tabticket booking` b on b.name = bs.parent
					where bs.parenttype = 'ticket booking' and bs.parent != %s
						and b.show_schedule = %s and b.status != 'Cancelled'
						and bs.row_alphabet = %s and bs.seat_number = %s
					limit 1
				""",
				(self.name, self.show_schedule, row, number),
			)
			if reserved:
				frappe.throw(_("Seat {0}{1} is already booked for this show.").format(row, number))
