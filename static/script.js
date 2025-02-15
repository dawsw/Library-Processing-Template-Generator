function addLabel() {
    const table = document.getElementById("labelTable");

    const newRow = document.createElement("tr");
    newRow.innerHTML = `
        <td class="item">
            <select id="label" name="label">
                <option value="select" selected disabled hidden>Select a label</option>
                <optgroup label="Barcode">
                    <option value="barcode-with-protector-attached">Barcode with Protector Attached</option>
                    <option value="barcode-attached">Barcode Attached</option>
                    <option value="barcode-unattached">Barcode Unattached</option>
                </optgroup>
                <optgroup label="Spine">
                    <option value="spine-label-attached">Spine Label Attached</option>
                    <option value="spine-label-unattached">Spine Label Unattached</option>
                </optgroup>
                <optgroup label="AR">
                    <option value="smallAR-label-attached">Small AR Label Attached</option>
                    <option value="smallAR-label-unattached">Small AR Label Unattached</option>
                    <option value="largeAR-label-attached">Large AR Label Attached</option>
                    <option value="largeAR-label-unattached">Large AR Label Unattached</option>
                </optgroup>
                <optgroup label="Lexile">
                    <option value="spine-label-attached">Spine Label Attached</option>
                    <option value="spine-label-unattached">Spine Label Unattached</option>
                </optgroup>
            </select>
        </td>
        <td class="item">
            <select id="location" name="location">
                <option value="select" selected disabled hidden>Select a location</option>
                <optgroup label="Spine"></optgroup>
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="5">5</option>
                <optgroup label="Front Cover"></optgroup>
                <option value="A">A</option>
                <option value="U">U</option>
                <option value="C">C</option>
                <option value="B">B</option>
                <option value="V">V</option>
                <option value="D">D</option>
                <optgroup label="Back Cover"></optgroup>
                <option value="F">F</option>
                <option value="I">I</option>
                <option value="H">H</option>
                <option value="E">E</option>
                <option value="T">V</option>
                <option value="G">D</option>
                <optgroup label="Inside Front Cover"></optgroup>
                <option value="J">J</option>
                <option value="W">W</option>
                <option value="L">L</option>
                <option value="K">K</option>
                <option value="X">X</option>
                <option value="M">M</option>
                <optgroup label="Inside Back Cover"></optgroup>
                <option value="N">N</option>
                <option value="Y">Y</option>
                <option value="P">P</option>
                <option value="O">O</option>
                <option value="Z">Z</option>
                <option value="Q">Q</option>
                <optgroup label="Front Flyleaf"></optgroup>
                <option value="3">3</option>
                <optgroup label="Back Flyleaf"></optgroup>
                <option value="4">4</option>
            </select>
        </td>
        <td class="item">
            <select id="direction" name="direction">
                <option value="select" selected disabled hidden>Select a direction</option>
                <option value="horizontal">Horizontal</option>
                <option value="top-to-bottom">Vertical (Top to Bottom)</option>
                <option value="bottom-to-top">Vertical (Bottom to Top)</option>
            </select>
        </td>
        <td>
            <button class="removeButton" onclick="removeRow(event)">X</button>
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

// reset each select to its first option if refreshed
window.onload = function () {
    document.querySelectorAll("select").forEach(select => {
        select.selectedIndex = 0; 
    });
};