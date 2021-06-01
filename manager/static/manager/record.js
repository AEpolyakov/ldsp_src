window.onload = function() {
    const record_type = document.getElementById('id_type')
    const date_from = document.getElementById('id_date_from')
    const date_to = document.getElementById('id_date_to')
    const time_from = document.getElementById('id_time_from')
    const time_to = document.getElementById('id_time_to')    
    const current_department = document.getElementById('id_cur_dep')
    const dep_select = document.querySelector('#department-selector')
    const persons = document.querySelector('#id_person')
    // const csrf_token = document.getElementsByName('csrfmiddlewaretoken')

    dep_select.addEventListener('change', (event)=>{
        var xhr = new XMLHttpRequest()
        const params = dep_select.value
        xhr.open('GET', '/dep_change/' + params, true)

        xhr.onload = function(){
            const fetched_persons = xhr.response.split('---')

            console.log(persons)
            console.log(fetched_persons)

            for (i=persons.length-1; i >= 0; i--){
                persons.remove(i)
            }

            for (i=0; i < fetched_persons.length-1; i++){
                const option = document.createElement("option")
                option.text = fetched_persons[i]
                console.log(option)
                persons.add(option)
            }


            

        }
        xhr.send()
    })

    date_from.value = today()
    time_from.setAttribute('class', 'disabled')
    time_to.setAttribute('class', 'disabled')
    date_to.setAttribute('class', 'disabled')

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