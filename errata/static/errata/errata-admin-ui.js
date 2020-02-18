django.jQuery(function ($) {
    $(document).ready(function(){
        let status = document.getElementById("id_status")
        let resolution = document.getElementById("id_resolution")
        let archived = document.getElementById("id_junk")
        let junk = document.getElementById("id_junk")

        let savebtn = $('input[name="_save"]')
        let savenewbtn = $('input[name="_saveasnew"]')
        let savecontbtn = $('input[name="_continue"]')

        //changing the button text based on status and resolution selection
        $('#id_status, #id_resolution').change(function(){
            if (status.options[status.selectedIndex].value == 'Reviewed' && (resolution.options[resolution.selectedIndex].value == 'Will Not Fix' || resolution.options[resolution.selectedIndex].value == 'Duplicate' || resolution.options[resolution.selectedIndex].value == 'Not An Error' || resolution.options[resolution.selectedIndex].value == 'Major Book Revision' || resolution.options[resolution.selectedIndex].value == 'Approved')) {
                savebtn.val('Save AND EMAIL USER')
                savenewbtn.val('Save as new and email user')
                savecontbtn.val('Save, email user, and continue editing')
            } else if ((status.options[status.selectedIndex].value == 'Completed') && (resolution.options[resolution.selectedIndex].value == 'Sent to Customer Support' || resolution.options[resolution.selectedIndex].value == 'More Information Requested' || resolution.options[resolution.selectedIndex].value == 'Partner Product')) {
                savebtn.val('SAVE AND EMAIL USER')
                savenewbtn.val('Save as new and email user')
                savecontbtn.val('Save, email user, and continue editing')
            } else {
                savebtn.val('SAVE')
                savenewbtn.val('Save as new')
                savecontbtn.val('Save and continue editing')
            }
        })

        //auto-check archived if junk box is checked
        $('#id_junk, #id_archived').change(function(){
            if (document.getElementById("id_junk").checked == true){
              document.getElementById("id_archived").checked = true;
            }
        })
    })
})
