import frappe
from erpnext.utilities.transaction_base import TransactionBase
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip

from frappe.utils import (
	add_days,
	cint,
	cstr,
	date_diff,
	flt,
	formatdate,
	get_first_day,
	get_link_to_form,
	getdate,
	money_in_words,
	rounded,
)


class CustomSalarySlip(SalarySlip):
    def set_time_sheet(self):
        if self.salary_slip_based_on_timesheet:
            self.set("timesheets", [])

            Timesheet = frappe.qb.DocType("Timesheet")
            timesheets = (
                frappe.qb.from_(Timesheet)
                .select(Timesheet.star)
                .where(
                    (Timesheet.employee == self.employee)
                    & (Timesheet.start_date.between(self.start_date, self.end_date))
                    & ((Timesheet.status == "Submitted") | (Timesheet.status == "Billed"))
                )
            ).run(as_dict=1)

            print('/n/n Timesheet /n', timesheets, '/n/n')

            for data in timesheets:
                # Edited line below to add overtime hours to timesheet childtable
                self.append("timesheets", {"time_sheet": data.name, "working_hours": data.total_hours, "overtime_hours": data.overtime_hours})
    
    
    def pull_sal_struct(self):
        from hrms.payroll.doctype.salary_structure.salary_structure import make_salary_slip

        if self.salary_slip_based_on_timesheet:
            self.salary_structure = self._salary_structure_doc.name
            self.hour_rate = self._salary_structure_doc.hour_rate
            self.base_hour_rate = flt(self.hour_rate) * flt(self.exchange_rate)
            self.total_working_hours = sum([d.working_hours or 0.0 for d in self.timesheets]) or 0.0
            # Added line below to add total overtime hours
            self.total_overtime_hours = sum([d.overtime_hours or 0.0 for d in self.timesheets])
            wages_amount = self.hour_rate * self.total_working_hours

            self.add_earning_for_hourly_wages(
                self, self._salary_structure_doc.salary_component, wages_amount
            )

        make_salary_slip(self._salary_structure_doc.name, self)