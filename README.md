# Theatre Booking System

A Frappe application for managing theatre shows, scheduling, and seat bookings — built on top of a site with ERPNext installed.

---

## Overview

This app lets an admin:

- Create and manage **Theatres** and their **Seats**
- Create **Shows** (movies / plays) with a title, description, and duration
- Schedule shows at specific theatres with a date, time window, and ticket price (**Show Schedule**)
- **Book seats** for a scheduled show, with the amount due automatically calculated
- Filter and view today's (and upcoming) shows via the Show Schedule list

All business rules are enforced **server-side** in Python — nothing is enforced only in JavaScript.

---

## Data Model

| DocType | Purpose |
|---|---|
| **Theatre** | A physical venue. Stores name, address, and an `active` flag. |
| **Theatre Seat** | Individual seats within a theatre, identified by row (A, B, …) and seat number. Has an `active` flag to disable seats (e.g., for maintenance). |
| **Show** | A title / production (movie or play). Stores the title, description, duration in minutes, and an `is_active` flag. A Show is not tied to any date — it is a reusable template. |
| **Show Schedule** | Puts a Show into a Theatre on a specific date with a start time, end time, and ticket price. This is the schedulable event. |
| **Ticket Booking** | A booking by a customer for a Show Schedule. Contains a child table of `Book Seat` rows (row + seat number), a booking status (`Confirmed` / `Cancelled`), and a calculated `amount_due = ticket_price × number_of_seats`. |
| **Book Seat** | Child doctype of Ticket Booking. Represents one seat being reserved (row alphabet + seat number). |

### Design decisions

- **Show vs Show Schedule** — the Show carries permanent information (title, duration); the Schedule carries time/venue/price. This avoids duplicating show metadata per event and lets the same production run at multiple theatres or on multiple dates without copying data.
- **Theatre Seat is a first-class DocType** — seats are pre-defined per theatre. This lets the system validate that a booked seat actually exists and is active, rather than accepting any arbitrary row/number.
- **Amount due on the booking, not the seat row** — price is set at the Schedule level (same price for all seats in a show), so `amount_due` is derived at booking-save time (`ticket_price × seat_count`) and stored on the Ticket Booking document. No payment gateway is wired up; the field exists for downstream use.
- **No Customer / Item / Sales Order** — see the ERPNext section below for the rationale.

---

## Server-Side Validations

### Show
- Title is required and non-blank.
- Duration must be at least 1 minute.

### Theatre Seat
- Row alphabet is required and is normalised to uppercase.
- Seat number must be a positive integer.
- Duplicate seat (same theatre + row + number) is rejected.

### Show Schedule
- Show date cannot be in the past.
- End time must be after start time.
- Ticket price must be greater than zero.
- Only active Shows can be scheduled.
- Only active Theatres can be scheduled.
- Overlapping schedules in the same theatre on the same date are rejected (SQL overlap check).

### Ticket Booking
- Show Schedule must be valid and must not be in the past.
- At least one seat must be added.
- Every seat row must be non-blank and seat number must be positive.
- Duplicate seat within the same booking is rejected.
- Each booked seat must exist and be active in the theatre for that schedule.
- A seat already booked for the same Show Schedule (in a non-Cancelled booking) cannot be booked again.
- `ticket_price` and `amount_due` are set programmatically from the Schedule — they cannot be forged by the client.

---

## ERPNext Usage

### What I used from ERPNext

| ERPNext feature | How it is used here |
|---|---|
| **Frappe's DocType / ORM layer** | All data storage, list views, form views, permissions, field validation, and naming strategies come from the Frappe framework that ships with ERPNext. |
| **`frappe.db.sql` / `frappe.db.exists` / `frappe.db.get_value`** | Used for overlap detection, duplicate-seat checks, and reading related document fields inside server-side validation hooks. |
| **`frappe.utils.getdate` / `today`** | Used to prevent scheduling shows in the past and to block bookings for past shows. |
| **Frappe Roles & Permissions** | System Manager role is granted create/read/write/delete on all custom doctypes — no custom permission logic required. |
| **Frappe's `autoname`** | Show uses `field:show_name`; Show Schedule and Ticket Booking use `naming_series` — standard Frappe naming strategies. |

### What I looked at and decided against

| ERPNext concept | Reason not used |
|---|---|
| **Sales Order / Sales Invoice** | ERPNext's SO/SI cycle is designed around items, warehouses, taxes, and multi-step workflows. Mapping a one-time theatre booking into that pipeline would require creating a fake Item per show, dealing with warehouses, and fighting ERPNext's stock and accounting assumptions. The complexity outweighs the benefit for this scope; without payment integration there is no accounting entry to make. |
| **Customer doctype** | Useful if the app needed a full CRM history per buyer. At this scope, the booking just captures a customer name as a text field. Linking to ERPNext Customer is a natural next step once payment integration is added. |
| **ERPNext Event / Calendar** | Covers generic calendar scheduling but lacks theatre-specific fields (ticket price, seat count, capacity). Building on top of it would mean working around its schema rather than using it. |
| **Website / Portal** | ERPNext's web portal (ecommerce) is designed for B2C item sales. Adapting it for seat selection would require heavy customisation with no meaningful reuse. |

### What I would have had to build myself without ERPNext / Frappe

Without the Frappe framework (which comes bundled with ERPNext) I would have needed to build: database schema migrations, a REST API layer, an admin UI (list + form views), user authentication and role-based access, file attachments, audit logging, and a front-end framework. Frappe provides all of that out of the box, which is the primary reason for choosing it.

---

## Installation

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/HirenRavaliya/theatre_booking_system.git --branch develop
bench --site <your-site> install-app theatre_booking_system
bench --site <your-site> migrate
```

> **Requires**: Frappe v15+ with ERPNext installed on the site.

---

## Quick Start (after installation)

1. **Create a Theatre** — go to *Theatre Booking System → Theatre*, add a name and mark it active.
2. **Add Seats** — go to *Theatre Seat*, create seats for the theatre (e.g., Row A, seats 1–10).
3. **Create a Show** — go to *Show*, enter the title and duration, mark it active.
4. **Schedule it** — go to *Show Schedule*, link the Show and Theatre, set date/time/price.
5. **Book seats** — go to *Ticket Booking*, choose the Schedule, add seat rows, save. Amount due is calculated automatically.

To see today's shows, open *Show Schedule* and filter by `Show Date = Today`.

---

## License

MIT
