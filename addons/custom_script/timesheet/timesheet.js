frappe.ui.form.on('Timesheet', {
    total_hours(frm){
        //code here
        if(frm.doc.total_hours){
            if(parseInt(frm.doc.total_hours) > 9){
                var overtime = parseInt(frm.doc.total_hours) - 9
                frm.set_value("overtime_hours", overtime)
                frm.refresh_field("overtime_hours")
            }
        }
    },
   
    parent_project(frm) {
       // your code here
        if(frm.doc.parent_project){
            frappe.call({
                method: "addons.custom_script.timesheet.timesheet.fetch_overtime_rate",
                args: {
                    'project': frm.doc.parent_project, 
                },
                callback: function (r) {
                    console.log(r.message)
                    if (r.message) {
                        frm.set_value("project_overtime_rate", r.message)
                        frm.refresh_field("project_overtime_rate")
                    }
                }
           });    
        }
       
    }

})