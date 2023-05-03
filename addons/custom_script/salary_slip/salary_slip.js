frappe.ui.form.on('Salary Slip', {
    employee(frm) {
       // your code here
        if(frm.doc.employee){
            frappe.call({
                method: "addons.custom_script.salary_slip.salary_slip.fetch_overtime_hours",
                args: {
                    'employee': frm.doc.employee, 
                },
                callback: function (r) {
                    if (r.message) {
                        const overtime_hours = r.message
                        frm.set_value("overtime_hours", overtime_hours)
                        frm.refresh_field("overtime_hours")
                    }
                }
           });    
        }
       
    }

})