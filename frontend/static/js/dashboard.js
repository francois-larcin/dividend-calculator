function createPortfolioCard(portfolio) {
    return `
        <div class="bg-white rounded-lg shadow-lg p-6">
            <h3 class="font-bold text-xl mb-2">${portfolio.name}</h3>
            <p class="text-blue-500 mb-4">${portfolio.currency}</p>
            <div class="flex gap-2">
                <button class="bg-blue-500 text-white px-4 py-2 rounded-lg" onclick="viewPortfolio(${portfolio.id})">
                    Voir
                </button>
                <button class="bg-red-500 text-white px-4 py-2 rounded-lg" onclick="openModal('delete-modal')">
                    🗑️
                </button>
            </div>
        </div>
    `
}

async function loadPortfolios() {
    // 1. API call
    const response = await fetch('api/portfolios/')

    // 2. Convert into JSON 
    const portfolios = await response.json()

    // 3. Display in the DOM
    const grid = document.querySelector('#portfolio-grid')
    grid.innerHTML = portfolios.map(p => createPortfolioCard(p)).join('')

    lucide.createIcons()
}

// Navigate to the portfolio page
function viewPortfolio(id) {
    window.location.href = `/portfolio/${id}`
}

// Delete portfolio
async function deletePortfolio() {

    // Get the ID stored in modal dataset
    const modal = document.querySelector('#delete-modal')
    const id = parseInt(modal.dataset.portfolioId)

    await fetch(`/api/portfolios/${id}`, {method: 'DELETE'})
    closeModal('delete-modal')
    loadPortfolios()
}

// Create a portfolio
async function createPortfolio() {
    
    // 1. Get the values from the form
    const name = document.querySelector('#portfolio-name').value
    const currency = document.querySelector('#portfolio-currency').value

    // 2. API call
    await fetch('/api/portfolios/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({user_id: 1, name, currency})
    })

    // 3. Close modal and reload
    closeModal('create-modal')
    loadPortfolios()
}


// Open a portfolio delete modal
function openDeleteModal(portfolioId) {

    // 1 Stock portfolio ID in the modal
    const modal = document.querySelector('#delete-modal')
    modal.dataset.portfolio = portfolioId

    // 2 Open the modal
    openModal('delete-modal')
}

// Call the function at page loading
loadPortfolios()


