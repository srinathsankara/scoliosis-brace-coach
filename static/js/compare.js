document.addEventListener('DOMContentLoaded', () => {
    const btn = document.createElement('button');
    btn.textContent = 'Compare Selected Sessions';
    btn.className = 'bg-blue-500 text-white px-4 py-2 rounded mt-4';
    document.querySelector('.grid').after(btn);

    btn.onclick = async () => {
        const id1 = document.getElementById('session1').value;
        const id2 = document.getElementById('session2').value;
        
        const res1 = await fetch(`/api/session/${id1}`);
        const data1 = await res1.json();
        
        const res2 = await fetch(`/api/session/${id2}`);
        const data2 = await res2.json();
        
        if (data1.metrics && data2.metrics) {
            const tbody = document.getElementById('comparison-table-body');
            tbody.innerHTML = '';
            document.getElementById('comparison-results').classList.remove('hidden');
            
            for (const key of Object.keys(data1.metrics)) {
                const v1 = data1.metrics[key] || 0;
                const v2 = data2.metrics[key] || 0;
                const diff = (v2 - v1).toFixed(2);
                
                // Assuming lower is better for asymmetry/lean metrics
                const isImprovement = (key.includes('asymmetry') || key.includes('lean') || key.includes('tilt') || key.includes('deviation'))
                    ? parseFloat(diff) < 0 : parseFloat(diff) > 0;
                
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td class="p-2 border font-medium capitalize">${key.replace(/_/g, ' ')}</td>
                    <td class="p-2 border">${v1}</td>
                    <td class="p-2 border">${v2}</td>
                    <td class="p-2 border">${diff}</td>
                    <td class="p-2 border font-bold ${isImprovement ? 'text-green-600' : 'text-red-600'}">
                        ${isImprovement ? 'Improved' : 'Needs Attention'}
                    </td>
                `;
                tbody.appendChild(row);
            }
        }
    };
});
