function addBatchRow() {
    const template = document.getElementById("batch-row-template");
    const clone = template.content.cloneNode(true);
    document
        .getElementById("batch-body")
        .appendChild(clone);
}

document
    .getElementById("add-row")
    .addEventListener("click", addBatchRow);

document.addEventListener("click", function(event){
    if(event.target.classList.contains("remove-row")){
        event.target.closest("tr").remove();
    }
});

window.onload = function(){
    addBatchRow();
};