// IMPORTANT: Replace with your actual API Gateway URL
const API_ENDPOINT_BASE = 'https://51yoc1tha9.execute-api.us-east-1.amazonaws.com/prod';

// --- Main Function to Render UI ---
function renderAppList(data, container) {
    container.innerHTML = ''; // Clear previous content

    data.forEach(category => {
        const categoryElement = createCollapsibleSection(category.category, 0); // Level 0 for main categories
        container.appendChild(categoryElement.section);

        // The content area for this category
        const contentArea = categoryElement.content;

        category.items.forEach(item => {
            if (item.subcategory) { // This is a subcategory
                const subCategoryElement = createCollapsibleSection(item.subcategory, 1); // Level 1 for subcategories
                contentArea.appendChild(subCategoryElement.section);
                renderAppCards(item.apps, subCategoryElement.content); // Render apps inside the subcategory's content area
            } else { // This is an app directly under the category
                renderAppCards([item], contentArea); // Render a single app card
            }
        });
    });
}

// --- Helper Function to Create a Collapsible Section ---
function createCollapsibleSection(title, level) {
    const section = document.createElement('section');
    section.className = level === 0 ? 'mb-4' : 'mb-2 ml-4'; // Indent subcategories

    const header = document.createElement('div');
    const headerClasses = level === 0 
        ? 'bg-white rounded-lg shadow-sm p-4 flex justify-between items-center cursor-pointer' 
        : 'bg-gray-100 rounded-md p-3 flex justify-between items-center cursor-pointer';
    header.className = headerClasses;

    const titleSize = level === 0 ? 'text-2xl' : 'text-xl';
    header.innerHTML = `
        <h${level + 2} class="${titleSize} font-semibold text-gray-700">${title}</h${level + 2}>
        <ion-icon name="chevron-down-outline" class="text-2xl text-gray-500 transition-transform"></ion-icon>
    `;

    const content = document.createElement('div');
    content.className = 'hidden p-4';

    section.appendChild(header);
    section.appendChild(content);

    header.addEventListener('click', () => {
        const icon = header.querySelector('ion-icon');
        content.classList.toggle('hidden');
        icon.classList.toggle('rotate-180');
    });

    return { section, content };
}

// --- Helper Function to Render App Cards ---
function renderAppCards(apps, container) {
    const grid = document.createElement('div');
    grid.className = 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6';

    apps.forEach(app => {
        const appCard = document.createElement('div');
        appCard.className = 'bg-white rounded-lg shadow-md p-6 flex flex-col justify-between';
        const buttonId = `launch-btn-${app.appId}`;
        appCard.innerHTML = `<div><h3 class="text-xl font-bold text-gray-800">${app.appName}</h3><p class="text-gray-600 mt-2 mb-4">${app.description}</p></div><div class="flex justify-between items-center mt-4"><span class="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">v${app.version}</span><button id="${buttonId}" class="bg-blue-600 text-white font-semibold px-4 py-2 rounded-lg hover:bg-blue-700 w-32">Launch</button></div>`;
        grid.appendChild(appCard);
        setTimeout(() => { document.getElementById(buttonId).addEventListener('click', (event) => launchApp(event, app.appId)); }, 0);
    });

    container.appendChild(grid);
}

// --- DOM Loaded Event Listener ---
document.addEventListener('DOMContentLoaded', function() {
    fetch('apps.json')
        .then(response => response.json())
        .then(data => {
            const appContainer = document.getElementById('app-container');
            renderAppList(data, appContainer);
        })
        .catch(error => {
            console.error('Error fetching app data:', error);
            const appContainer = document.getElementById('app-container');
            appContainer.innerHTML = '<p class="text-center text-red-500">Failed to load applications. Please try again later.</p>';
        });
});

// --- Launch App Logic (unchanged) ---
async function launchApp(event, appId) {
    event.stopPropagation();
    const button = event.target;
    button.textContent = 'Launching...';
    button.disabled = true;
    try {
        const response = await fetch(`${API_ENDPOINT_BASE}/launch/${appId}`, { method: 'POST' });
        const data = await response.json();
        if (!data.launchUrl) { throw new Error(data.error || 'Unknown launch error.'); }
        button.textContent = 'Waiting...';
        await pollUntilReady(data.launchUrl);
        window.open(data.launchUrl, '_blank');
    } catch (error) {
        alert(`Failed to launch app: ${error.message}`);
    } finally {
        button.textContent = 'Launch';
        button.disabled = false;
    }
}
function pollUntilReady(url) {
    return new Promise(resolve => {
        const interval = setInterval(async () => {
            try { await fetch(url, { mode: 'no-cors' }); clearInterval(interval); resolve(); }
            catch (e) { console.log('App not ready yet, retrying...'); }
        }, 3000);
    });
}
