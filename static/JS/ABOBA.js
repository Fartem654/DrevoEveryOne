fetch("{% url 'DApp:family_graph_json' %}")
    .then(response => response.json())
    .then(graphData => {
        // Инициализируем граф
        const cy = cytoscape({
            container: document.getElementById('cy'),
            elements: graphData,
            style: [{
                selector: 'node',
                style: {
                    'background-color': data => data.data('gender') === 'M' ? '#66B2FF' : '#FF99CC',
                    'label': 'data(label)',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'color': '#000',
                    'font-size': 14
                }
            }, {
                selector: 'edge[type="parent-child"]',
                style: {
                    'line-color': '#555',
                    'target-arrow-color': '#555',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier'
                }
            }, {
                selector: 'edge[type="spouse"]',
                style: {
                    'line-color': '#e74c3c',
                    'width': 2,
                    'curve-style': 'bezier',
                    'control-point-distance': -40,
                    'line-style': data => data.data('married') ? 'solid' : 'dashed'
                }
            }]
        });

        // Расположение графа слева направо
        cy.layout({
            name: 'dagre',
            rankDir: 'LR',  // left to right
            padding: 10
        }).run;
    });