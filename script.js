document.addEventListener('DOMContentLoaded', function() {
    fetch('apps.json')
        .then(response => response.json())
        .then(data => {
            const appContainer = document.getElementById('app-container');
            appContainer.innerHTML = ''; // Clear the 'Loading...' text

            data.forEach(category => {
                const categorySection = document.createElement('section');
                categorySection.className = 'mb-12';
                
                const categoryTitle = document.createElement('h2');
                categoryTitle.className = 'text-2xl font-semibold text-gray-700 border-b pb-2 mb-6';
                categoryTitle.textContent = category.category;
                categorySection.appendChild(categoryTitle);

                const grid = document.createElement('div');
                grid.className = 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6';

                category.apps.forEach(app => {
                    const appCard = document.createElement('div');
                    appCard.className = 'bg-white rounded-lg shadow-md p-6 flex flex-col justify-between';
                    
                    appCard.innerHTML = `
                        <div>
                            <h3 class="text-xl font-bold text-gray-800">${app.appName}</h3>
                            <p class="text-gray-600 mt-2 mb-4">${app.description}</p>
                        </div>
                        <div class="flex justify-between items-center mt-4">
                            <span class="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">v${app.version}</span>
                            <button class="bg-blue-600 text-white font-semibold px-4 py-2 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 transition-colors">
                                Launch
                            </button>
                        </div>
                    `;
                    grid.appendChild(appCard);
                });

                categorySection.appendChild(grid);
                appContainer.appendChild(categorySection);
            });
        })
        .catch(error => {
            console.error('Error fetching app data:', error);
            const appContainer = document.getElementById('app-container');
            appContainer.innerHTML = '<p class="text-center text-red-500">Failed to load applications. Please try again later.</p>';
        });
});
