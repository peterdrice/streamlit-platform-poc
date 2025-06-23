const API_ENDPOINT_BASE = 'https://51yoc1tha9.execute-api.us-east-1.amazonaws.com/prod';

document.addEventListener('DOMContentLoaded', function() {
    fetch('apps.json')
        .then(response => response.json())
        .then(data => {
            const appContainer = document.getElementById('app-container');
            appContainer.innerHTML = ''; // Clear the 'Loading...' text

            data.forEach(category => {
                const categorySection = document.createElement('section');
                categorySection.className = 'mb-4';

                // Create the category header that will be clickable
                const header = document.createElement('div');
                header.className = 'bg-white rounded-lg shadow-sm p-4 flex justify-between items-center cursor-pointer';
                header.innerHTML = `
                    <h2 class="text-2xl font-semibold text-gray-700">${category.category}</h2>
                    <ion-icon name="chevron-down-outline" class="text-2xl text-gray-500 transition-transform"></ion-icon>
                `;

                // Create the collapsible content area
                const content = document.createElement('div');
                content.className = 'hidden p-4'; // Hidden by default

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
                            <button id="${buttonId}" class="bg-blue-600 text-white font-semibold px-4 py-2 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 transition-colors w-32">
                                Launch
                            </button>
                        </div>
                    `;
                    grid.appendChild(appCard);

                    setTimeout(() => {
                        document.getElementById(buttonId).addEventListener('click', (event) => launchApp(event, app.appName));
                    }, 0);
                });

                content.appendChild(grid);
                categorySection.appendChild(header);
                categorySection.appendChild(content);
                appContainer.appendChild(categorySection);

                // Add the click event listener to the header
                header.addEventListener('click', () => {
                    const icon = header.querySelector('ion-icon');
                    content.classList.toggle('hidden');
                    icon.classList.toggle('rotate-180');
                });
            });
        })
        .catch(error => {
            console.error('Error fetching app data:', error);
            const appContainer = document.getElementById('app-container');
            appContainer.innerHTML = '<p class="text-center text-red-500">Failed to load applications. Please try again later.</p>';
        });
});

async function launchApp(event, appName) {
    // Stop the click from bubbling up and triggering the collapse/expand
    event.stopPropagation();

    const button = event.target;
    button.textContent = 'Launching...';
    button.disabled = true;

    const apiAppName = 'sample-streamlit-app';

    try {
        const response = await fetch(`${API_ENDPOINT_BASE}/launch/${apiAppName}`, { method: 'POST' });
        const data = await response.json();

        if (!data.launchUrl) {
            throw new Error(data.error || 'Unknown error occurred during launch.');
        }

        console.log(`App launched, waiting for it to become ready at: ${data.launchUrl}`);
        button.textContent = 'Waiting...';

        await pollUntilReady(data.launchUrl);

        console.log(`App is ready! Opening now.`);
        window.open(data.launchUrl, '_blank');
        button.textContent = 'Launch';
        button.disabled = false;

    } catch (error) {
        console.error('Launch error:', error);
        alert(`Failed to launch app: ${error.message}`);
        button.textContent = 'Launch';
        button.disabled = false;
    }
}

function pollUntilReady(url) {
    return new Promise(resolve => {
        const interval = setInterval(async () => {
            try {
                await fetch(url, { mode: 'no-cors' });
                clearInterval(interval);
                resolve();
            } catch (e) {
                console.log('App not ready yet, retrying...');
            }
        }, 3000); // Poll every 3 seconds
    });
}

