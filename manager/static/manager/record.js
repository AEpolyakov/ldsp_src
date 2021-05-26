window.onload = function() {
    const record_type = document.getElementById('id_type')
    const date_from = document.getElementById('id_date_from')
    const date_to = document.getElementById('id_date_to')
    const time_from = document.getElementById('id_time_from')
    const time_to = document.getElementById('id_time_to')
    const button_date_from_today = document.getElementById('button_date_from_today')
    const current_department = document.getElementById('id_cur_dep')
    const department_selected = document.getElementById('id_dep_sel')


    console.log(current_department.value)
    console.log(department_selected.value)
    department_selected.value = current_department.value


    time_from.setAttribute('class', 'disabled')
    time_to.setAttribute('class', 'disabled')
    date_to.setAttribute('class', 'disabled')

    date_from.value = today()
    button_date_from_today.addEventListener('click', (event)=>{
        date_from.value = today()
    })

    date_to.addEventListener('click', (event)=>{
        if (date_to.classList.contains('disabled')){
            date_to.classList.remove('disabled')
            if (date_from.value != null) {
                date_to.value = date_from.value
            } else {
                date_to.value = today()
            }
        }
    })

    time_from.addEventListener('click', (event)=>{
        if (time_from.classList.contains('disabled')){
            time_from.classList.remove("disabled");
            time_to.classList.remove("disabled");
            date_to.classList.remove("disabled")
            time_from.value = '08:00'
            time_to.value = '11:45'
            if (date_from.value != null) {
                date_to.value = date_from.value
            } else {
                date_to.value = today()
            }
        }
    })
    time_to.addEventListener('click', (event)=>{
        if (time_to.classList.contains('disabled')){
            time_from.classList.remove("disabled");
            time_to.classList.remove("disabled");
            time_from.value = '08:00'
            time_to.value = '11:45'
            if (date_from.value != null) {
                date_to.value = date_from.value
            } else {
                date_to.value = today()
            }
        }
    })

    function today(){
        var date = new Date();
        var currentDate = date.toISOString().substring(0,10);
        return currentDate
    }

}