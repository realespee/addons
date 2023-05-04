import frappe


@frappe.whitelist()
def fetch_overtime_rate(project):
    print("/n/n Overstime/n", project, "\n\n")
    proj = frappe.get_doc("Project", project)
    print("/n/n Overstime/n", proj, "\n\n")
    # Return the timesheets
    return proj.overtime_rate
    