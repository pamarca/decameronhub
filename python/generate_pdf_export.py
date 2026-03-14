import os

# ======================================================
# CONFIG
# ======================================================

BASE_DIR = os.path.dirname(__file__)
OUT_DIR = os.path.join(BASE_DIR, "output")

# ======================================================
# GENERATE PDF EXPORT CODE
# ======================================================

pdf_code = '''
<!-- Add this BEFORE the closing </div> of person-index -->

<!-- PDF Export Button -->
<div class="pdf-export-section">
    <button id="export-pdf-btn" class="btn btn-pdf">
        <span class="pdf-icon">📄</span> Export as PDF
    </button>
</div>

<!-- PDF Export Modal -->
<div id="pdf-modal" class="pdf-modal hidden">
    <div class="pdf-modal-content">
        <div class="pdf-modal-header">
            <h3>Export Person Index as PDF</h3>
            <button id="close-pdf-modal" class="close-btn">×</button>
        </div>
        
        <div class="pdf-modal-body">
            <div class="pdf-option">
                <label>
                    <input type="radio" name="pdf-scope" value="all" checked>
                    <span>All Characters</span>
                </label>
            </div>
            
            <div class="pdf-option">
                <label>
                    <input type="radio" name="pdf-scope" value="brigata">
                    <span>Brigata Members Only</span>
                </label>
            </div>
            
            <div class="pdf-option">
                <label>
                    <input type="radio" name="pdf-scope" value="visible">
                    <span>Currently Filtered Characters</span>
                </label>
            </div>
            
            <div class="pdf-settings">
                <label class="checkbox-label">
                    <input type="checkbox" id="pdf-include-mentions" checked>
                    <span>Include mention lists</span>
                </label>
                
                <label class="checkbox-label">
                    <input type="checkbox" id="pdf-include-meta" checked>
                    <span>Include metadata (role, origin, etc.)</span>
                </label>
            </div>
        </div>
        
        <div class="pdf-modal-footer">
            <button id="generate-pdf-btn" class="btn btn-primary">
                Generate PDF
            </button>
            <button id="cancel-pdf-btn" class="btn">
                Cancel
            </button>
        </div>
        
        <div id="pdf-progress" class="pdf-progress hidden">
            <div class="progress-bar">
                <div class="progress-fill" id="pdf-progress-fill"></div>
            </div>
            <p id="pdf-progress-text">Preparing PDF...</p>
        </div>
    </div>
</div>

<!-- jsPDF Library -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>

<style>
/* PDF Export Button */
.pdf-export-section {
    text-align: center;
    margin: 3rem 0;
    padding: 2rem;
    background: #f9fafb;
    border-radius: 8px;
}

.btn-pdf {
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    background: #dc2626;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

.btn-pdf:hover {
    background: #b91c1c;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
}

.pdf-icon {
    font-size: 1.2rem;
}

/* PDF Modal */
.pdf-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
}

.pdf-modal.hidden {
    display: none;
}

.pdf-modal-content {
    background: white;
    border-radius: 8px;
    width: 90%;
    max-width: 500px;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.pdf-modal-header {
    padding: 1.5rem;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #7c3aed;
    color: white;
    border-radius: 8px 8px 0 0;
}

.pdf-modal-header h3 {
    margin: 0;
    font-size: 1.2rem;
}

.close-btn {
    background: transparent;
    border: none;
    font-size: 2rem;
    cursor: pointer;
    color: white;
    padding: 0;
    width: 2rem;
    height: 2rem;
    line-height: 1;
}

.close-btn:hover {
    opacity: 0.8;
}

.pdf-modal-body {
    padding: 1.5rem;
}

.pdf-option {
    margin: 1rem 0;
}

.pdf-option label {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    cursor: pointer;
    padding: 0.75rem;
    border-radius: 4px;
    transition: background 0.2s;
}

.pdf-option label:hover {
    background: #f9fafb;
}

.pdf-option input[type="radio"] {
    width: 1.25rem;
    height: 1.25rem;
    cursor: pointer;
}

.pdf-settings {
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid #eee;
}

.checkbox-label {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 0.75rem 0;
    cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
    width: 1.25rem;
    height: 1.25rem;
    cursor: pointer;
}

.pdf-modal-footer {
    padding: 1.5rem;
    border-top: 1px solid #eee;
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
}

.btn {
    padding: 0.75rem 1.5rem;
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

.pdf-progress {
    padding: 1.5rem;
    border-top: 1px solid #eee;
}

.pdf-progress.hidden {
    display: none;
}

.progress-bar {
    width: 100%;
    height: 8px;
    background: #eee;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 1rem;
}

.progress-fill {
    height: 100%;
    background: #7c3aed;
    width: 0%;
    transition: width 0.3s;
}

#pdf-progress-text {
    text-align: center;
    color: #666;
    margin: 0;
}
</style>

<script>
// PDF Export Functionality
(function() {
    const modal = document.getElementById('pdf-modal');
    const openBtn = document.getElementById('export-pdf-btn');
    const closeBtn = document.getElementById('close-pdf-modal');
    const cancelBtn = document.getElementById('cancel-pdf-btn');
    const generateBtn = document.getElementById('generate-pdf-btn');
    const progress = document.getElementById('pdf-progress');
    const progressFill = document.getElementById('pdf-progress-fill');
    const progressText = document.getElementById('pdf-progress-text');
    
    // Open modal
    openBtn.addEventListener('click', () => {
        modal.classList.remove('hidden');
    });
    
    // Close modal
    function closeModal() {
        modal.classList.add('hidden');
        progress.classList.add('hidden');
        progressFill.style.width = '0%';
    }
    
    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });
    
    // Generate PDF
    generateBtn.addEventListener('click', async function() {
        // Show progress
        progress.classList.remove('hidden');
        generateBtn.disabled = true;
        
        // Get options
        const scope = document.querySelector('input[name="pdf-scope"]:checked').value;
        const includeMentions = document.getElementById('pdf-include-mentions').checked;
        const includeMeta = document.getElementById('pdf-include-meta').checked;
        
        // Get persons to include
        let personsToExport = [];
        const allCards = document.querySelectorAll('.person-card');
        
        if (scope === 'all') {
            personsToExport = Array.from(allCards);
        } else if (scope === 'brigata') {
            personsToExport = Array.from(allCards).filter(card => card.classList.contains('brigata'));
        } else if (scope === 'visible') {
            personsToExport = Array.from(allCards).filter(card => card.style.display !== 'none');
        }
        
        updateProgress(10, `Preparing ${personsToExport.length} characters...`);
        
        // Initialize jsPDF
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        
        // Add title
        doc.setFontSize(20);
        doc.text('Decameron - Index of Persons', 20, 20);
        
        doc.setFontSize(10);
        doc.text(`Generated: ${new Date().toLocaleDateString()}`, 20, 28);
        doc.text(`Scope: ${scope.charAt(0).toUpperCase() + scope.slice(1)}`, 20, 33);
        
        let y = 45;
        const margin = 20;
        const pageHeight = doc.internal.pageSize.height;
        const lineHeight = 6;
        
        updateProgress(20, 'Adding characters...');
        
        // Add each person
        for (let i = 0; i < personsToExport.length; i++) {
            const card = personsToExport[i];
            
            // Check if we need a new page
            if (y > pageHeight - 40) {
                doc.addPage();
                y = 20;
            }
            
            // Person name
            const name = card.querySelector('.person-name').textContent.trim();
            doc.setFontSize(12);
            doc.setFont(undefined, 'bold');
            doc.text(name, margin, y);
            y += lineHeight + 2;
            
            // Metadata
            if (includeMeta) {
                const meta = card.querySelector('.person-meta');
                if (meta) {
                    doc.setFontSize(9);
                    doc.setFont(undefined, 'normal');
                    const metaText = meta.textContent.trim();
                    doc.text(metaText, margin + 5, y);
                    y += lineHeight;
                }
            }
            
            // Mentions
            if (includeMentions) {
                const mentionList = card.querySelector('.mention-list');
                if (mentionList) {
                    doc.setFontSize(8);
                    doc.setFont(undefined, 'italic');
                    
                    const mentions = mentionList.querySelectorAll('li:not(.mention-hidden)');
                    const mentionCount = mentions.length;
                    
                    doc.text(`Appears in ${mentionCount} section(s):`, margin + 5, y);
                    y += lineHeight;
                    
                    // List first 10 mentions
                    const showCount = Math.min(mentions.length, 10);
                    for (let j = 0; j < showCount; j++) {
                        const mention = mentions[j];
                        const link = mention.querySelector('a');
                        if (link) {
                            const text = link.textContent.trim();
                            
                            // Check page break
                            if (y > pageHeight - 20) {
                                doc.addPage();
                                y = 20;
                            }
                            
                            doc.text(`  • ${text}`, margin + 8, y);
                            y += lineHeight - 1;
                        }
                    }
                    
                    if (mentions.length > 10) {
                        doc.text(`  ... and ${mentions.length - 10} more`, margin + 8, y);
                        y += lineHeight;
                    }
                }
            }
            
            y += 5; // Space between persons
            
            // Update progress
            const percent = 20 + ((i + 1) / personsToExport.length) * 70;
            updateProgress(percent, `Processing ${i + 1}/${personsToExport.length}...`);
        }
        
        updateProgress(95, 'Finalizing PDF...');
        
        // Save PDF
        setTimeout(() => {
            doc.save('decameron-person-index.pdf');
            updateProgress(100, 'Complete!');
            
            setTimeout(() => {
                closeModal();
                generateBtn.disabled = false;
            }, 1000);
        }, 500);
    });
    
    function updateProgress(percent, text) {
        progressFill.style.width = percent + '%';
        progressText.textContent = text;
    }
})();
</script>
'''

# Save
output_file = os.path.join(OUT_DIR, 'pdf-export-addon.html')
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(pdf_code)

print(f"✅ Generated: {output_file}")
print(f"\n📊 Features:")
print(f"   ✓ Export all characters or filtered selection")
print(f"   ✓ Include/exclude mentions and metadata")
print(f"   ✓ Progress indicator")
print(f"   ✓ Professional PDF formatting")
print(f"\n💡 Add this code to the BOTTOM of your person index HTML")
print(f"   (before the final </div>)")
