// IMPORTANT: Replace with your actual API Gateway URL from the command above
const API_ENDPOINT_BASE = 'https://51yoc1tha9.execute-api.us-east-1.amazonaws.com/prod'; 

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

                    const buttonId = `launch-btn-${app.appName.replace(/\s+/g, '-')}`;

                    appCard.innerHTML = `
                        <div>
                            <h3 class="text-xl font-bold text-gray-800">${app.appName}</h3>
                            <p class="text-gray-600 mt-2 mb-4">${app.description}</p>
                        </div>
                        <div class="flex justify-between items-center mt-4">
                            <span class="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">v${app.version}</span>
                            <button id="${buttonId}" class="bg-blue-600 text-white font-semibold px-4 py-2 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 transition-colors w-24">
                                Launch
                            </button>
                        </div>
                    `;
                    grid.appendChild(appCard);

                    // Add event listener after the element is in the DOM
                    setTimeout(() => {
                        document.getElementById(buttonId).addEventListener('click', (event) => launchApp(event, app.appName));
                    }, 0);
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

function launchApp(event, appName) {
    const button = event.target;
    button.textContent = 'Launching...';
    button.disabled = true;

    // For this PoC, we use a simplified name for the API path.
    // In a real app, you'd have a mapping from appName to task definition or ECR repo name.
    const apiAppName = 'sample-streamlit-app';

    fetch(`${API_ENDPOINT_BASE}/launch/${apiAppName}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.launchUrl) {
            console.log(`App launched. URL: ${data.launchUrl}`);
            window.open(data.launchUrl, '_blank');
            button.textContent = 'Launch';
            button.disabled = false;
        } else {
            throw new Error(data.error || 'Unknown error occurred.');
        }
    })
    .catch(error => {
        console.error('Launch error:', error);
        alert(`Failed to launch app: ${error.message}`);
        button.textContent = 'Launch';
        button.disabled = false;
    });
}

