const portfolioId = document.querySelector('#app').dataset.portfolioId
console.log(portfolioId);

function createHolding(holding) {
    return `
    <tr>
        <td class="py-3">${holding.ticker}</td>
        <td class="py-3">${holding.company_name}</td>
        <td class="py-3">${holding.total_shares}</td>
        <td class="py-3">${holding.avg_price}</td>
        <td class="py-3">${holding.total_invested}</td>
        <td class="py-3">${holding.currency}</td>
        <td class="py-3">-</td>
    </tr>
    `
}

async function loadPortfolio(portfolioId) {
    // 1. API call
    const response = await fetch(`/api/portfolios/${portfolioId}`)

    // 2. Convert into JSON
    const portfolio = await response.json()

    // 3. Diplay in the DOM
    document.querySelector('#portfolio-name').innerHTML = portfolio.name
    document.querySelector('#portfolio-currency').innerHTML = portfolio.currency


    lucide.createIcons()

}

async function loadHoldings(portfolioId) {
    // 1. API call
    const response = await fetch(`/api/holdings/${portfolioId}`)

    // 2. Convert into JSON
    const holdings = await response.json()

    // 3. Display in the DOM
    const tbody = document.querySelector('#holdings-table')
    tbody.innerHTML = holdings.map(h => createHolding(h)).join('')

    lucide.createIcons()
}

// Stock search
let searchTimeout = null

const searchInput = document.querySelector('#stock-search')

searchInput.addEventListener('input', function() {

    // Delete old timer
    clearTimeout(searchTimeout)

    const query = searchInput.value

    if (query.lenght < 1) return

    // Wait 300ms before searching
    searchTimeout = setTimeout(async function() {
        const response = await fetch(`/api/stocks/search?q=${query}`)
        const results = await response.json()
        
        // Dipslay results
        const dropdown = document.querySelector('#search-results')

        // If results empty -> hide
        if (results.lenght === 0) {
            dropdown.classList.add('hidden')
            return
        }

        // Display dropdown
        dropdown.classList.remove('hidden')
        dropdown.innerHTML = results.map(r => createSearchResult(r)).join('')
    }, 300)

})

function createSearchResult(result) {
    return `
        <div class="px-4 py-3 hover:bg-gray-100 cursor-pointer"
             onclick="selectStock('${result.ticker}', '${result.company_name}')">
            <span class="font-bold">${result.ticker}</span>
            <span class="text-gray-500"> - ${result.company_name}</span>
        </div>
    `
}

async function selectStock(ticker, companyName) {
    // 1. Hide dropdown (search results)
    const dropdown = document.querySelector('#search-results')
    dropdown.classList.add('hidden')

    // 2. Fill buy modal with ticker and company name
    document.querySelector('#buy-ticker').innerHTML = ticker
    document.querySelector('#buy-company').innerHTML = companyName

    // 3. Fetch current price and currency
    const response = await fetch(`/api/stocks/${ticker}/price`)
    const data = await response.json()

    // 4. Display current price and currency in the DOM
    document.querySelector('#current-price').innerHTML = data.price
    document.querySelector('#currency').innerHTML = data.currency

    // 5. Open buy modal
    openModal('buy-modal')
}



// Direct call at page loading 
loadPortfolio(portfolioId)
loadHoldings(portfolioId)