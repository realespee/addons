import frappe


@frappe.whitelist()
def fetch_overtime_hours(employee):
    timesheets = frappe.get_all("Timesheet", filters={"employee":employee}, 
        fields=["name", "employee", "overtime_hours", "start_date", "end_date"])
    # Check dates
    overtime_hours = 0
    for t in timesheets:
        overtime_hours = overtime_hours + t.overtime_hours

    # Return the timesheets
    return overtime_hours
    