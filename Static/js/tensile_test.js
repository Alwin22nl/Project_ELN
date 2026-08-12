document
.getElementById("batch_select")
.addEventListener("change", function(){


    let sample_id = this.value;

    let table =
        document.getElementById("specimen_body");


    table.innerHTML = "";


    if (!sample_id){
        return;
    }


    fetch("/get_tensile_specimens/" + sample_id)

    .then(response => response.json())

    .then(data => {


        data.specimens.forEach(function(specimen){


            let row =
            document.createElement("tr");


            row.innerHTML = `

            <td>

            ${specimen.specimen_no}

            <input
            type="hidden"
            name="specimen_id[]"
            value="${specimen.specimen_id}">

            </td>


            <td>
            ${Number(specimen.width_avg).toFixed(3)}
            </td>

            <td>
            ${Number(specimen.thickness_avg).toFixed(3)}
            </td>


            <td>
            <input
            type="number"
            step="0.001"
            name="t_50[]"
            min="0.100"
            max="10.000">
            </td>


            <td>
            <input
            type="number"
            step="0.001"
            name="t_100[]"
            min="0.100"
            max="10.000" >
            </td>


            <td>
            <input
            type="number"
            step="0.001"
            name="t_max[]"
            min="0.100"
            max="10.000"
            required>
            </td>


            <td>
            <input
            type="number"
            step="0.001"
            name="e_max[]"
            min="1.000"
            max="2000.000"
            required>
            </td>
            
            <td>
            <input 
            type="text"
            name="remark[]">
            </td>

            `;


            table.appendChild(row);


        });


    });


});