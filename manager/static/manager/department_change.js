window.addEventListener("load", function(){
        console.log("department_change.js")
        const persons = document.querySelector('#id_person')

        const dep_select = document.querySelector('#department-selector')
        dep_select.addEventListener('change', (event)=>{
        var xhr = new XMLHttpRequest()
        const params = dep_select.value
        xhr.open('GET', '/dep_change/' + params, true)

        xhr.onload = function(){
            if (persons){
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
        xhr.send()
    })
})