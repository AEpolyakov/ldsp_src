window.onload = function() {
    const timesheet_date = document.getElementById('id_date')
    timesheet_date.value = today()

    function today(){
        const date = new Date()
        const currentDate = date.toISOString().substring(0,10)
        return currentDate
    }
}