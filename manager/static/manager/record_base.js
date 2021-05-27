window.onload = function() {

    const date_clear = document.querySelector("#date_clear")
    const date_input = document.querySelector("#id_date")
    date_clear.addEventListener('click', (event)=>{
        console.log('click')
        date_input.value = ''
    })


}

function confirmSubmit(){
    var agree=confirm("Удалить запись?");
    if (agree)
     return true ;
    else
     return false ;
}