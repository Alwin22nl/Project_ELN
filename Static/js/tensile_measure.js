function calculateAverages(row) {

    // Widths
    const w1 = parseFloat(row.querySelector('[name="width_1[]"]').value) || 0;
    const w2 = parseFloat(row.querySelector('[name="width_2[]"]').value) || 0;
    const w3 = parseFloat(row.querySelector('[name="width_3[]"]').value) || 0;

    // Thicknesses
    const t1 = parseFloat(row.querySelector('[name="thickness_1[]"]').value) || 0;
    const t2 = parseFloat(row.querySelector('[name="thickness_2[]"]').value) || 0;
    const t3 = parseFloat(row.querySelector('[name="thickness_3[]"]').value) || 0;

    // Only calculate when all three values are entered
    if (
        row.querySelector('[name="width_1[]"]').value &&
        row.querySelector('[name="width_2[]"]').value &&
        row.querySelector('[name="width_3[]"]').value
    ) {

        row.querySelector(".width-avg").value =
            ((w1 + w2 + w3) / 3).toFixed(3);

    } else {

        row.querySelector(".width-avg").value = "";

    }

    if (
        row.querySelector('[name="thickness_1[]"]').value &&
        row.querySelector('[name="thickness_2[]"]').value &&
        row.querySelector('[name="thickness_3[]"]').value
    ) {

        row.querySelector(".thickness-avg").value =
            ((t1 + t2 + t3) / 3).toFixed(3);

    } else {

        row.querySelector(".thickness-avg").value = "";

    }

}


// Recalculate whenever a measurement changes
document.querySelectorAll("tbody tr").forEach(function(row){

    row.querySelectorAll("input").forEach(function(input){

        input.addEventListener("input", function(){

            calculateAverages(row);

        });

    });

});