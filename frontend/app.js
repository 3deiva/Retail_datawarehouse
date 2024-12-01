async function fetchQueryData(queryName) {
    try {
        const response = await fetch(`http://127.0.0.1:5001/query/${queryName}`);
        const data = await response.json();
        
        const tableBody = document.querySelector('#salesTable tbody');
        tableBody.innerHTML = ''; // Clear any existing rows

        if (data.length > 0) {
            const columns = Object.keys(data[0]);
            const headerRow = document.querySelector('#salesTable thead tr');
            headerRow.innerHTML = columns.map(col => `<th>${col}</th>`).join('');

            data.forEach(row => {
                const tr = document.createElement('tr');
                tr.innerHTML = columns.map(col => `<td>${row[col]}</td>`).join('');
                tableBody.appendChild(tr);
            });
        } else {
            tableBody.innerHTML = '<tr><td colspan="15">No data available</td></tr>';
        }
    } catch (error) {
        alert('An error occurred while fetching query data.');
    }
}


