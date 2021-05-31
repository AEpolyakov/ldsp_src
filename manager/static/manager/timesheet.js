window.onload = function() {
    const timesheet_date = document.getElementById('timesheet-month')    
    const form_date = document.querySelector('#id_date')
    timesheet_date.value = today()  
    form_date.value = timesheet_date.value
    console.log(form_date)

    function today(){
        const date = new Date()        
        const month = date.getMonth() + 1
        const year = date.getFullYear()
        console.log(year.toString() + '-' + ('0' + month.toString()).slice(-2))
        return year.toString() + '-' + ('0' + month.toString()).slice(-2)
    }
    timesheet_date.addEventListener('change', (event)=>{
    	console.log(timesheet_date.value)
    	form_date.value = timesheet_date.value
    })
}