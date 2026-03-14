import json
import os

# ======================================================
# CONFIG
# ======================================================

BASE_DIR = os.path.dirname(__file__)
OUT_DIR = os.path.join(BASE_DIR, "output")

# Load network data
with open(os.path.join(OUT_DIR, 'network_data.json'), encoding='utf-8') as f:
    network = json.load(f)

# ======================================================
# GENERATE HTML
# ======================================================

html = []

html.append('''
<!-- D3.js from CDN -->
<script src="https://d3js.org/d3.v7.min.js"></script>

<div class="network-container">
    
    <!-- Controls -->
    <div class="network-controls">
        <div class="control-group">
            <label>Filter by:</label>
            <select id="group-filter">
                <option value="all">All Characters</option>
                <option value="brigata">Brigata Only</option>
                <option value="merchant">Merchants</option>
                <option value="noble">Nobles</option>
                <option value="religious">Religious</option>
            </select>
        </div>
        
        <div class="control-group">
            <label>Minimum connections:</label>
            <input type="range" id="connection-filter" min="0" max="50" value="0" step="1">
            <span id="connection-value">0</span>
        </div>
        
        <div class="control-group">
            <label>Layout:</label>
            <select id="layout-type">
                <option value="force">Force-Directed</option>
                <option value="radial">Radial</option>
                <option value="cluster">Clustered</option>
            </select>
        </div>
        
        <button id="reset-zoom" class="btn">Reset View</button>
        <button id="export-graph" class="btn btn-primary">Export as PNG</button>
    </div>
    
    <!-- Stats -->
    <div class="network-stats">
        <span id="visible-nodes">0</span> persons shown • 
        <span id="visible-edges">0</span> connections
    </div>
    
    <!-- Graph -->
    <div id="network-graph"></div>
    
    <!-- Legend -->
    <div class="network-legend">
        <h4>Legend</h4>
        <div class="legend-item">
            <span class="legend-color" style="background: #7c3aed;">●</span>
            <span>Brigata</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #f59e0b;">●</span>
            <span>Merchants</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #10b981;">●</span>
            <span>Nobles</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #3b82f6;">●</span>
            <span>Religious</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #6b7280;">●</span>
            <span>Other</span>
        </div>
        <div class="legend-note">
            <strong>Size:</strong> Number of mentions<br>
            <strong>Line thickness:</strong> Shared sections<br>
            <strong>Click:</strong> See details • <strong>Drag:</strong> Move nodes
        </div>
    </div>
    
</div>

<style>
.network-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem 1rem;
}

.network-controls {
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
    align-items: center;
    margin-bottom: 1rem;
    padding: 1rem;
    background: #f9fafb;
    border-radius: 8px;
}

.control-group {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.control-group label {
    font-weight: 600;
    font-size: 0.9rem;
}

.control-group select,
.control-group input[type="range"] {
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: white;
}

.control-group select {
    min-width: 150px;
}

#connection-value {
    font-weight: 600;
    color: #7c3aed;
    min-width: 2rem;
}

.btn {
    padding: 0.5rem 1rem;
    border: 1px solid #ddd;
    background: white;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.2s;
}

.btn:hover {
    background: #f3f4f6;
}

.btn-primary {
    background: #7c3aed;
    color: white;
    border-color: #7c3aed;
}

.btn-primary:hover {
    background: #6d28d9;
}

.network-stats {
    text-align: center;
    font-size: 0.9rem;
    margin-bottom: 1rem;
    font-weight: 600;
    color: #666;
}

#network-graph {
    width: 100%;
    height: 700px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background: #fafafa;
    position: relative;
    overflow: hidden;
}

.network-legend {
    margin-top: 1.5rem;
    padding: 1rem;
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.network-legend h4 {
    margin: 0 0 0.75rem 0;
    font-size: 1rem;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0.5rem 0;
    font-size: 0.9rem;
}

.legend-color {
    font-size: 1.5rem;
    line-height: 1;
}

.legend-note {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #eee;
    font-size: 0.85rem;
    color: #666;
}

/* Tooltip */
.node-tooltip {
    position: absolute;
    padding: 0.75rem;
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    pointer-events: none;
    font-size: 0.85rem;
    max-width: 250px;
    z-index: 1000;
}

.node-tooltip h4 {
    margin: 0 0 0.5rem 0;
    color: #7c3aed;
}

.node-tooltip .meta {
    color: #666;
    margin-bottom: 0.5rem;
}

/* Graph elements */
.node {
    cursor: pointer;
    stroke: white;
    stroke-width: 2px;
}

.node:hover {
    stroke: #7c3aed;
    stroke-width: 3px;
}

.node.selected {
    stroke: #f59e0b;
    stroke-width: 4px;
}

.link {
    stroke: #999;
    stroke-opacity: 0.3;
}

.link.highlighted {
    stroke: #7c3aed;
    stroke-opacity: 0.8;
}

.node-label {
    font-size: 10px;
    font-weight: 600;
    pointer-events: none;
    text-shadow: 0 0 3px white, 0 0 3px white, 0 0 3px white;
}
</style>

<script>
// Network data
const networkData = ''' + json.dumps(network, ensure_ascii=False) + ''';

console.log('Network loaded:', networkData.nodes.length, 'nodes,', networkData.edges.length, 'edges');

// Graph dimensions
const width = document.getElementById('network-graph').clientWidth;
const height = 700;

// Color scale
const colorScale = {
    'brigata': '#7c3aed',
    'merchant': '#f59e0b',
    'noble': '#10b981',
    'religious': '#3b82f6',
    'other': '#6b7280'
};

function getNodeColor(node) {
    if (node.brigata) return colorScale.brigata;
    if (node.group in colorScale) return colorScale[node.group];
    return colorScale.other;
}

// Create SVG
const svg = d3.select('#network-graph')
    .append('svg')
    .attr('width', width)
    .attr('height', height);

// Add zoom behavior
const g = svg.append('g');
const zoom = d3.zoom()
    .scaleExtent([0.1, 4])
    .on('zoom', (event) => {
        g.attr('transform', event.transform);
    });

svg.call(zoom);

// Create force simulation
let simulation = d3.forceSimulation()
    .force('link', d3.forceLink().id(d => d.id).distance(d => 100 + Math.random() * 50))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(d => Math.sqrt(d.size) * 3 + 15))
    .force('x', d3.forceX(width / 2).strength(0.05))
    .force('y', d3.forceY(height / 2).strength(0.05));

// Initialize random positions to avoid clustering
function randomizePositions(nodes) {
    const radius = Math.min(width, height) / 3;
    nodes.forEach((node, i) => {
        const angle = (i / nodes.length) * 2 * Math.PI;
        node.x = width / 2 + radius * Math.cos(angle) + (Math.random() - 0.5) * 100;
        node.y = height / 2 + radius * Math.sin(angle) + (Math.random() - 0.5) * 100;
    });
}

// Create tooltip
const tooltip = d3.select('.network-container')
    .append('div')
    .attr('class', 'node-tooltip')
    .style('opacity', 0);

// Store current data
let currentNodes = [];
let currentLinks = [];
let link, node, label;

// Initialize graph
function initGraph(nodes, edges) {
    currentNodes = JSON.parse(JSON.stringify(nodes));
    currentLinks = JSON.parse(JSON.stringify(edges));
    
    // Randomize initial positions
    randomizePositions(currentNodes);
    
    // Clear existing
    g.selectAll('*').remove();
    
    // Create links
    link = g.append('g')
        .selectAll('line')
        .data(currentLinks)
        .join('line')
        .attr('class', 'link')
        .attr('stroke-width', d => Math.sqrt(d.weight));
    
    // Create nodes
    node = g.append('g')
        .selectAll('circle')
        .data(currentNodes)
        .join('circle')
        .attr('class', 'node')
        .attr('r', d => Math.sqrt(d.size) * 3 + 5)
        .attr('fill', getNodeColor)
        .call(drag(simulation))
        .on('mouseover', showTooltip)
        .on('mouseout', hideTooltip)
        .on('click', selectNode);
    
    // Create labels (only for brigata and high-mention characters)
    label = g.append('g')
        .selectAll('text')
        .data(currentNodes.filter(d => d.brigata || d.size > 15))
        .join('text')
        .attr('class', 'node-label')
        .text(d => d.label)
        .attr('text-anchor', 'middle')
        .attr('dy', d => Math.sqrt(d.size) * 3 + 18);
    
    // Start simulation
    simulation.nodes(currentNodes).on('tick', ticked);
    simulation.force('link').links(currentLinks);
    simulation.alpha(1).restart();
    
    updateStats();
}

// Simulation tick
function ticked() {
    link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);
    
    node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);
    
    label
        .attr('x', d => d.x)
        .attr('y', d => d.y);
}

// Drag behavior
function drag(simulation) {
    function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }
    
    function dragged(event) {
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }
    
    function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }
    
    return d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended);
}

// Tooltip functions
function showTooltip(event, d) {
    const days = d.days.length > 0 ? d.days.join(', ') : 'None';
    
    tooltip.transition()
        .duration(200)
        .style('opacity', 1);
    
    tooltip.html(`
        <h4>${d.label}</h4>
        <div class="meta">
            ${d.role ? d.role.charAt(0).toUpperCase() + d.role.slice(1) : 'Unknown'}
            ${d.origin ? ' from ' + d.origin : ''}
        </div>
        <div>
            <strong>Mentions:</strong> ${d.mention_count}<br>
            <strong>Days:</strong> ${days}<br>
            <strong>Connections:</strong> ${currentLinks.filter(l => 
                l.source.id === d.id || l.target.id === d.id
            ).length}
        </div>
    `)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 10) + 'px');
}

function hideTooltip() {
    tooltip.transition()
        .duration(200)
        .style('opacity', 0);
}

// Select node
let selectedNode = null;

function selectNode(event, d) {
    // Deselect previous
    node.classed('selected', false);
    link.classed('highlighted', false);
    
    if (selectedNode === d) {
        selectedNode = null;
        return;
    }
    
    selectedNode = d;
    
    // Highlight selected node
    d3.select(this).classed('selected', true);
    
    // Highlight connected links
    link.classed('highlighted', l => 
        l.source.id === d.id || l.target.id === d.id
    );
}

// Filter functions
function filterGraph() {
    const groupFilter = document.getElementById('group-filter').value;
    const minConnections = parseInt(document.getElementById('connection-filter').value);
    
    // Filter nodes
    let filteredNodes = networkData.nodes.filter(node => {
        if (groupFilter !== 'all') {
            if (groupFilter === 'brigata' && !node.brigata) return false;
            if (groupFilter !== 'brigata' && node.group !== groupFilter) return false;
        }
        return true;
    });
    
    const nodeIds = new Set(filteredNodes.map(n => n.id));
    
    // Filter edges
    let filteredEdges = networkData.edges.filter(edge => 
        nodeIds.has(edge.source) && 
        nodeIds.has(edge.target) &&
        edge.weight >= minConnections
    );
    
    // Further filter nodes that have no connections
    const connectedNodeIds = new Set();
    filteredEdges.forEach(e => {
        connectedNodeIds.add(e.source);
        connectedNodeIds.add(e.target);
    });
    
    filteredNodes = filteredNodes.filter(n => 
        connectedNodeIds.has(n.id) || n.brigata
    );
    
    initGraph(filteredNodes, filteredEdges);
}

// Update stats
function updateStats() {
    document.getElementById('visible-nodes').textContent = currentNodes.length;
    document.getElementById('visible-edges').textContent = currentLinks.length;
}

// Event listeners
document.getElementById('group-filter').addEventListener('change', filterGraph);
document.getElementById('connection-filter').addEventListener('input', function() {
    document.getElementById('connection-value').textContent = this.value;
    filterGraph();
});

document.getElementById('reset-zoom').addEventListener('click', function() {
    svg.transition().duration(750).call(
        zoom.transform,
        d3.zoomIdentity
    );
});

document.getElementById('export-graph').addEventListener('click', function() {
    // Create canvas
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    
    // White background
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, width, height);
    
    // Convert SVG to image
    const svgData = new XMLSerializer().serializeToString(svg.node());
    const img = new Image();
    const blob = new Blob([svgData], {type: 'image/svg+xml;charset=utf-8'});
    const url = URL.createObjectURL(blob);
    
    img.onload = function() {
        ctx.drawImage(img, 0, 0);
        URL.revokeObjectURL(url);
        
        // Download
        canvas.toBlob(function(blob) {
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = 'decameron-network.png';
            a.click();
        });
    };
    
    img.src = url;
});

// Layout change
document.getElementById('layout-type').addEventListener('change', function() {
    const layout = this.value;
    
    if (layout === 'radial') {
        simulation.force('center', null);
        simulation.force('x', d3.forceX(width / 2).strength(0.1));
        simulation.force('y', d3.forceY(height / 2).strength(0.1));
        simulation.force('charge').strength(-300);
    } else if (layout === 'cluster') {
        simulation.force('center', null);
        simulation.force('x', d => d3.forceX(width / 4 * (d.brigata ? 1 : 3)).strength(0.3));
        simulation.force('y', d3.forceY(height / 2).strength(0.1));
    } else {
        simulation.force('center', d3.forceCenter(width / 2, height / 2));
        simulation.force('x', null);
        simulation.force('y', null);
        simulation.force('charge').strength(-200);
    }
    
    simulation.alpha(1).restart();
});

// Initialize with full data
initGraph(networkData.nodes, networkData.edges);
</script>
''')

network_html = '\n'.join(html)

# Save
output_file = os.path.join(OUT_DIR, 'person-network-graph.html')
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(network_html)

print(f"✅ Generated: {output_file}")
print(f"\n📊 Features:")
print(f"   ✓ Interactive force-directed graph")
print(f"   ✓ Filter by character type")
print(f"   ✓ Filter by connection strength")
print(f"   ✓ Three layout options")
print(f"   ✓ Zoom and pan")
print(f"   ✓ Export as PNG")
print(f"\n💡 Create a new WordPress page and paste this HTML")
