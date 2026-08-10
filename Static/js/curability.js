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

document.addEventListener("change", function(event){
    if(event.target.classList.contains("sample-select")){
        let selected =
            event.target.options[event.target.selectedIndex];
        let afterstorage =
            selected.dataset.afterstorage || "";
        let row =
            event.target.closest("tr");
        row.querySelector(".afterstorage-id").value =
            afterstorage;
    }
});