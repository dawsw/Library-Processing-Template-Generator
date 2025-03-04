function addLabel() {
    const table = document.getElementById("labelTable");

    const newRow = document.createElement("tr");
    newRow.innerHTML = `
       <td class="item">
            <select id="label" name="label" required>
                <option value="" selected disabled hidden>Select a label</option>
                <optgroup label="Barcode"></optgroup>
                    <option value="Barcode with Protector Attached">Barcode with Protector Attached</option>
                    <option value="Barcode Attached">Barcode Attached</option>
                    <option value="Barcode Unattached">Barcode Unattached</option>
                <optgroup label="Spine"></optgroup>
                    <option value="Spine Label Attached">Spine Label Attached</option>
                    <option value="Spine Label Unattached">Spine Label Unattached</option>
                <optgroup label="A/R"></optgroup>
                    <option value="Small A/R Label Attached">Small A/R Label Attached</option>
                    <option value="Small A/R Label Unattached">Small A/R Label Unattached</option>
                    <option value="Large A/R Label Attached">Large A/R Label Attached</option>
                    <option value="Large A/R Label Unattached">Large A/R Label Unattached</option>
                <optgroup label="Lexile"></optgroup>
                    <option value="Lexile Label Attached">Lexile Label Attached</option>
                    <option value="Lexile Label Unattached">Lexile Label Unattached</option>
                <optgroup label="Genre"></optgroup>
                    <option value="Genre Label Attached">Genre Label Attached</option>
                    <option value="Genre Label Unattached">Genre Label Unattached</option>
                <optgroup label="Property"></optgroup>
                    <option value="Property Label Attached">Property Label Attached</option>
                    <option value="Property Label Unattached">Property Label Unattached</option>
            </select>
        </td>
        <td class="item">
            <select id="location" name="location">
                <option value="" selected disabled hidden>Select a location</option>
                <optgroup label="Spine"></optgroup>
                    <option value="1 Standard Spine">1 - Standard Spine</option>
                    <option value="2 Standard A/R">2 - Standard A/R</option>
                    <option value="5">5</option>
                <optgroup label="Front Cover"> </optgroup>
                    <option value="A">A</option>
                    <option value="B">B</option>
                    <option value="C">C</option>
                    <option value="D">D</option>
                    <option value="U">U</option>
                    <option value="V">V</option>  
                <optgroup label="Back Cover"> </optgroup>
                    <option value="E">E</option>
                    <option value="F">F</option>
                    <option value="G">G</option>
                    <option value="H">H</option>
                    <option value="I">I</option>
                    <option value="T">T</option>
                <optgroup label="Inside Front Cover"></optgroup>
                    <option value="J">J</option>
                    <option value="K">K</option>
                    <option value="L">L</option>
                    <option value="M">M</option>
                    <option value="W">W</option>
                    <option value="X">X</option>                        
                <optgroup label="Inside Back Cover"></optgroup>
                    <option value="N">N</option>
                    <option value="O">O</option>
                    <option value="P">P</option>
                    <option value="Q">Q</option>
                    <option value="Y">Y</option>
                    <option value="Z">Z</option>
                <optgroup label="Front Flyleaf"></optgroup>
                    <option value="3">3</option>
                <optgroup label="Back Flyleaf"></optgroup>
                    <option value="4">4</option>
                <optgroup label="Unattached"></optgroup>
                    <option value="Unattached">Unattached</option>
                <optgroup label="Other"></optgroup>
                    <option value="See Notes">See Notes</option>   
            </select>
        </td>
        <td class="item">
            <select id="direction" name="direction" required>
                <option value="" selected disabled hidden>Select a direction</option>
                <option value="Horizontal">Horizontal</option>
                <option value="Vertical (Top to Bottom)">Vertical (Top to Bottom)</option>
                <option value="Vertical (Bottom to Top)">Vertical (Bottom to Top)</option>
            </select>
        </td>
        <td>
            <button class="remove-button" onclick="removeRow(event)">X</button>
        </td>
    `;

    table.appendChild(newRow);
}


function removeRow(event) {
    let rows = document.querySelectorAll("tr");

    //only remove if more than two rows (headers and first row)
    if (rows.length > 2) {
        let row = event.target.closest("tr"); 
            if (row) {
                row.remove(); 
            }
    }
}

function deleteFileInput() {
    let input = document.getElementById('fileInput');
    input.value = '';
}

 /*reset selects and inputs when refreshed
window.onload = function () {
    document.querySelectorAll("select").forEach(select => {
        select.selectedIndex = 0; 
    });

    const myForm = document.getElementById('fullForm');
        fullForm.reset(); 
};  */