document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const loadingDiv = document.getElementById('loading');
    const resultsDiv = document.getElementById('results');
    
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const fileInput = document.getElementById('resume');
        if (!fileInput.files.length) {
            alert('Please select a file first');
            return;
        }
        
        // Show loading, hide results
        loadingDiv.style.display = 'block';
        resultsDiv.style.display = 'none';
        
        const formData = new FormData();
        formData.append('resume', fileInput.files[0]);
        
        fetch('/analyze', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            displayResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error analyzing resume: ' + error.message);
        })
        .finally(() => {
            loadingDiv.style.display = 'none';
            resultsDiv.style.display = 'block';
        });
    });
    
    function displayResults(data) {
        // Update overall score
        document.getElementById('totalScore').textContent = Math.round(data.total_score);
        document.getElementById('overallRating').textContent = data.overall;
        document.getElementById('overallFeedback').textContent = `Your resume scored ${Math.round(data.total_score)}/100 - ${data.overall}`;
        
        // Update section scores
        const sectionScoresDiv = document.getElementById('sectionScores');
        sectionScoresDiv.innerHTML = '';
        
        for (const [section, info] of Object.entries(data.sections)) {
            const sectionDiv = document.createElement('div');
            sectionDiv.className = 'section-card';
            
            const sectionName = document.createElement('h4');
            sectionName.textContent = section.charAt(0).toUpperCase() + section.slice(1).replace('_', ' ');
            
            const sectionScore = document.createElement('div');
            sectionScore.className = 'section-score';
            sectionScore.textContent = `Score: ${Math.round(info.score)}`;
            
            const sectionFeedback = document.createElement('div');
            sectionFeedback.className = 'section-feedback';
            sectionFeedback.textContent = info.feedback;
            
            sectionDiv.appendChild(sectionName);
            sectionDiv.appendChild(sectionScore);
            sectionDiv.appendChild(sectionFeedback);
            
            sectionScoresDiv.appendChild(sectionDiv);
        }
        
        // Update suggestions
        const suggestionsList = document.getElementById('suggestionsList');
        suggestionsList.innerHTML = '';
        
        data.suggestions.forEach(suggestion => {
            const li = document.createElement('li');
            li.textContent = suggestion;
            suggestionsList.appendChild(li);
        });
        
        // Color the overall score circle based on rating
        const scoreCircle = document.querySelector('.score-circle');
        if (data.total_score >= 80) {
            scoreCircle.style.background = '#2ecc71'; // Green
        } else if (data.total_score >= 60) {
            scoreCircle.style.background = '#f39c12'; // Orange
        } else {
            scoreCircle.style.background = '#e74c3c'; // Red
        }
    }
});