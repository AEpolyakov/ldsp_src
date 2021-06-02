window.addEventListener("load", function(){

    console.log("department_change.js")
    const persons = document.querySelector('#id_person')
    const dep_select = document.querySelector('#department-selector')

    const records_table = document.querySelector('#records-table')

    dep_select.addEventListener('change', (event)=>{
        var xhr = new XMLHttpRequest()
        if (persons){
            const params = dep_select.value
            xhr.open('GET', '/records_dep_change/' + params, true)

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
        }
        if (records_table){
            const params = dep_select.value
            xhr.open('GET', '/base_dep_change/' + params, true)

            xhr.onload = function(){
                const fetched_records = xhr.response.split('---')

                console.log(fetched_records)

                for (i=records_table.rows.length-1; i >= 1; i--){
                    records_table.deleteRow(i)
                }
                for (i=0; i < fetched_records.length-1; i++){
                    const row = records_table.insertRow(i+1)

                    record_fields = fetched_records[i].split("--")
                    console.log(record_fields)
                    for (j=0; j<record_fields.length; j++){
                        const cell = row.insertCell(j)
                        const text = document.createTextNode(record_fields[j])
                        cell.appendChild(text)
                    }
                    const cell = row.insertCell(record_fields.length)
                    const killButton = document.createElement("button")
                    killButton.innerHTML = '<img class="image-close" src="/static/close.png" />'
                    killButton.name = "kill"
                    killButton.value = parseInt(record_fields[0])
                    killButton.addEventListener('click', confirmSubmit)
                    cell.appendChild(killButton)
                }
            }
        }
        xhr.send()
    })
})