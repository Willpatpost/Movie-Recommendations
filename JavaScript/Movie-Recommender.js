// New movie recommender code
let movies = [];  // This will hold the data once loaded

// Helper function to extract relevant features from each movie
function extractFeatures(movie) {
    const keywords = movie.keywords ? movie.keywords : "";
    const cast = movie.cast ? movie.cast : "";
    const genres = movie.genres ? movie.genres : "";
    return (keywords + " " + cast + " " + genres).toLowerCase();
}

// Function to vectorize text features (simple word count)
function vectorize(text) {
    const words = text.split(" ");
    const wordCount = {};
    
    words.forEach(word => {
        wordCount[word] = (wordCount[word] || 0) + 1;
    });
    
    return wordCount;
}

// Function to compute cosine similarity between two word count vectors
function cosineSimilarity(vecA, vecB) {
    let dotProduct = 0;
    let normA = 0;
    let normB = 0;
    
    const allWords = new Set([...Object.keys(vecA), ...Object.keys(vecB)]);
    
    allWords.forEach(word => {
        const a = vecA[word] || 0;
        const b = vecB[word] || 0;
        
        dotProduct += a * b;
        normA += a * a;
        normB += b * b;
    });
    
    return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}

// Load the dataset and extract features
fetch('Data/movie_dataset.json')
    .then(response => response.json())
    .then(data => {
        movies = data.map(movie => ({
            title: movie.title.trim(),  // Keep original title case
            features: vectorize(extractFeatures(movie))  // Vectorize the features
        }));
        console.log('Movies loaded and processed:', movies.map(movie => movie.title));
    })
    .catch(error => console.error('Error loading the movie dataset:', error));

// Helper function to find a movie index by title
function getIndexFromTitle(title) {
    const normalizedTitle = title.trim();
    return movies.findIndex(movie => movie.title.toLowerCase() === normalizedTitle.toLowerCase());
}

// Function to recommend movies
function recommendMovies() {
    const inputTitle = document.getElementById('movieTitle').value.trim();
    const movieIndex = getIndexFromTitle(inputTitle);

    if (movieIndex === -1) {
        alert('Movie not found!');
        return;
    }

    const inputMovie = movies[movieIndex];
    const similarities = movies.map((movie, index) => {
        if (index === movieIndex) return 0;  // Ignore the same movie
        return { title: movie.title, score: cosineSimilarity(inputMovie.features, movie.features) * 100 };  // Convert to percentage
    });

    similarities.sort((a, b) => b.score - a.score);
    const topMovies = similarities.slice(0, 10);  // Top 10

    let resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';  // Clear previous results
    topMovies.forEach((movie, index) => {
        const resultItem = document.createElement('p');
        resultItem.textContent = `${index + 1}. ${movie.title} (Score: ${movie.score.toFixed(2)}%)`;
        resultsDiv.appendChild(resultItem);
    });
}

// Function to open and close the movie recommender popup
function openMovieRecommender() {
    const popup = document.getElementById('moviePopup');
    popup.style.display = 'flex';  // Open popup
}

function closeMovieRecommender() {
    const popup = document.getElementById('moviePopup');
    popup.style.display = 'none';  // Close popup
}

document.getElementById('recommendBtn').addEventListener('click', recommendMovies);
