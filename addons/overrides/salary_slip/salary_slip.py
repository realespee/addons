import frappe
from erpnext.utilities.transaction_base import TransactionBase
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip

from frappe.utils import flt


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
            # Added line below to calculate cumulative overtime_bonus_rate
            self.overtime_bonus_rate = self.overtime_rate(self.total_overtime_hours)
            wages_amount = self.hour_rate * self.total_working_hours

            self.add_earning_for_hourly_wages(
                self, self._salary_structure_doc.salary_component, wages_amount
            )

        make_salary_slip(self._salary_structure_doc.name, self)

    def overtime_rate(self, overtime_hours):
        '''
        Compute Overtime Bonus Rate, it increases by 0.25 for every 2 more hours of overtime
        '''
        if overtime_hours < 2:
            return 1
        elif overtime_hours == 4:
            return 1.25
        else:
            return 1.25 + (overtime_hours - 4) // 2 * 0.25