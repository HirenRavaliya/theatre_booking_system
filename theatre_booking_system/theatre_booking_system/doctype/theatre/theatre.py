# Copyright (c) 2026, Hiren Ravaliya and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class theatre(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		active: DF.Check
		address: DF.Data | None
		theatre_name: DF.Data | None
	# end: auto-generated types

	_DOCTYPE_NAME = "theatre"
