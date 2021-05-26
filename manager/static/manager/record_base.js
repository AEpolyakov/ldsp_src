window.onload = function() {
    const table = document.getElementById('records-table')

    const killers = document.querySelectorAll(".killer")
    console.log(killers)

    killers.forEach(killer => killer.addEventListener('click', (event) => {
        return confirm(`Удалить запись?`);
    }))

}