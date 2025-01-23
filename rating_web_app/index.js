/*******************************************************************
 * SLIDER FUNCTIONALITY
 *******************************************************************/
/* position = containerHeight - (rating / 10 * containerHeight) */
// Example data structure
const trialRatings = {
    'Trial1': 7.5,
    'Trial2': 4.2,
    'Trial3': 8.0,
    'Trial4': 8.0,
    'Trial5': 10.0,
    // etc...
}

const trialRating = document.getElementById('trialRating');
/* trialRating.addEventListener('input', function(e) {
    const newValue = e.target.value;
    // Update current trial position
    updateLabelPositions();
}); */

const currentTrialLabel = document.getElementById('currentTrialLabel');

function updateLabelPositions() {
    const containerHeight = 600; // Match your CSS
    
    // For each trial label
    Object.entries(trialRatings).forEach(([trial, rating]) => {
        const position = containerHeight - (rating / 10 * containerHeight);
        // Find and update label position
    });
}

trialRating.addEventListener('input', function(e) {
    currentTrialLabel.textContent = `CurrentTrial=${e.target.value}`;
});

/*******************************************************************
 * DRAG AND DROP LOGIC
 *******************************************************************/
let dragSrcEl = null;

function handleDragStart(e) {
    // Only allow dragging if this is the CurrentTrial
    if (!this.classList.contains('current')) {
        e.preventDefault();
        return;
    }
    dragSrcEl = this;
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.innerHTML);
}

function handleDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    return false;
}

function handleDragEnter(e) {
    this.classList.add('drag-over');
}

function handleDragLeave(e) {
    this.classList.remove('drag-over');
}

function handleDrop(e) {
    if (e.stopPropagation) e.stopPropagation();
    
    if (dragSrcEl !== this) {
        // Swap the dragged element with the drop target
        const tempHTML = this.innerHTML;
        const tempClasses = this.className;
        
        this.innerHTML = dragSrcEl.innerHTML;
        this.className = dragSrcEl.className;
        
        dragSrcEl.innerHTML = tempHTML;
        dragSrcEl.className = tempClasses;
    }
    return false;
}

function handleDragEnd(e) {
    const items = document.querySelectorAll('.trial-label');
    items.forEach((item) => {
        item.classList.remove('drag-over');
    });
}

// Attach event listeners to each trial label
const items = document.querySelectorAll('.trial-label');
items.forEach((item) => {
    item.addEventListener('dragstart', handleDragStart, false);
    item.addEventListener('dragenter', handleDragEnter, false);
    item.addEventListener('dragover', handleDragOver, false);
    item.addEventListener('dragleave', handleDragLeave, false);
    item.addEventListener('drop', handleDrop, false);
    item.addEventListener('dragend', handleDragEnd, false);
});

/*******************************************************************
 * FORM SUBMISSION TO GOOGLE SHEETS
 *******************************************************************/
const scriptURL = 'YOUR_GOOGLE_SCRIPT_URL';

function submitData() {
    const subjectName = document.getElementById('subjectName').value.trim();
    const dataCollectionName = document.getElementById('dataCollectionName').value.trim();
    const trialRatingValue = document.getElementById('trialRating').value;

    if (!subjectName || !dataCollectionName) {
        alert("Please fill in both Subject Name and Data Collection Name.");
        return;
    }

    // Get the final order of the trial labels
    const trialElements = document.querySelectorAll('#previousTrials .trial-label');
    const trialOrderArray = [];
    trialElements.forEach(label => {
        trialOrderArray.push(label.textContent.trim());
    });
    const trialOrderString = trialOrderArray.join(',');

    // Build the form data
    const formData = new FormData();
    formData.append('subjectName', subjectName);
    formData.append('dataCollectionName', dataCollectionName);
    formData.append('trialRating', trialRatingValue);
    formData.append('trialOrder', trialOrderString);

    fetch(scriptURL, {
        method: 'POST',
        body: formData,
        mode: 'no-cors'
    })
    .then(response => {
        alert("Submitted successfully!");
    })
    .catch(error => {
        console.error('Error!', error);
        alert('Something went wrong! Check console for details.');
    });
}