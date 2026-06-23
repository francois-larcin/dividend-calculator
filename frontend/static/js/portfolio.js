const portfolioId = document.querySelector('#app').dataset.portfolioId
let portfolioCurrency = ''

function createHolding(holding) {

    return `
    <tr>
        <td class="py-3 pr-4 max-w-[150px] truncate" title="${holding.company_name}">
        ${holding.company_name}
        </td>
        <td class="py-3">${holding.ticker}</td>
        <td class="py-3">${holding.currency}</td>
        <td class="py-3">${holding.total_shares}</td>
        <td class="py-3">${holding.avg_price.toLocaleString('fr-FR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        })}</td>

        <td class="py-3">${holding.total_invested.toLocaleString('fr-FR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        })}</td>

        <td class="py-3 ${holding.gain >= 0 ? 'text-green-500' : 'text-red-500'}">
        ${holding.gain.toLocaleString('fr-FR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        })}</td>

        <td class="py-3 ${holding.gain_percent >= 0 ? 'text-green-500' : 'text-red-500'}">
        ${holding.gain_percent.toLocaleString('fr-FR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        })} %</td>

        <td class="py-3 ${holding.realized_gain >= 0 ? 'text-green-500' : 'text-red-500'}">
        ${holding.realized_gain.toLocaleString('fr-FR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        })}</td>

        <td class="py-3">
            <button onclick="selectStock('${holding.ticker}', '${holding.company_name}')" class="bg-green-500 text-white px-4 py-2 rounded-lg">
                Buy
            </button>

            <button onclick="openSellModal('${holding.ticker}', '${holding.company_name}', ${holding.total_shares})" class="bg-red-500 text-white px-4 py-2 rounded-lg">
                Sell
            </button>
        </td>
        
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

    portfolioCurrency = document.querySelector('#portfolio-currency').innerHTML


    lucide.createIcons()

}

async function loadHoldings(portfolioId) {
    // 1. Get the holdings
    const response = await fetch(`/api/holdings/${portfolioId}/with-gain`)
    const holdings = await response.json()

    console.log('Holdings', holdings);
    

    // 2. Display in the DOM 
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

// buy modal logic
async function selectStock(ticker, companyName) {
    // 1. Hide dropdown (search results)
    const dropdown = document.querySelector('#search-results')
    dropdown.classList.add('hidden')

    // 2. Fill buy modal with ticker, company name and portfolio currency for the fee
    document.querySelector('#buy-ticker').innerHTML = ticker
    document.querySelector('#buy-company').innerHTML = companyName
    document.querySelector('#buy-currency-label').innerHTML = portfolioCurrency

    // 3. Fetch current price and currency
    const response = await fetch(`/api/stocks/${ticker}/price`)
    const data = await response.json()

    console.log('data', data);

    // 4. Display current price and currency in the DOM
    document.querySelector('#buy-price').value = data.price
    document.querySelector('#buy-stock-currency').innerHTML = data.currency
    document.querySelector('#buy-total-currency').innerHTML = data.currency

    // 5. Open buy modal
    openModal('buy-modal')
}


// Sell modal logic
async function openSellModal(ticker, companyName, maxShares) {
    // 1. Fill ticker and company name
    document.querySelector('#sell-ticker').innerHTML = ticker
    document.querySelector('#sell-company').innerHTML = companyName
    document.querySelector('#sell-currency-label').innerHTML = portfolioCurrency

    // 2. Fecth the current price and currency
    const response = await fetch(`/api/stocks/${ticker}/price`)
    const data = await response.json()

    // 3. Display current price and currency in the DOM
    document.querySelector('#sell-price').value = data.price
    document.querySelector('#sell-stock-currency').innerHTML = data.currency
    document.querySelector('#sell-total-currency').innerHTML = data.currency

    // 4. Define max of sell quantity with total_shares
    document.querySelector('#sell-quantity').max = maxShares

    // 5. Open sell-modal
    openModal('sell-modal')
}


function calculateTotal(quantityId, priceId, currencyId, totalId) {
    const quantity = parseFloat(document.querySelector(quantityId).value)
    const price = parseFloat(document.querySelector(priceId).value)
    const currency = document.querySelector(currencyId).innerHTML
    const total = (quantity * price).toFixed(2)
    document.querySelector(totalId).innerHTML = `${total} ${currency}`
}


document.querySelector('#buy-quantity').addEventListener('input', function() {
    calculateTotal('#buy-quantity', '#buy-price', '#buy-stock-currency', '#buy-total')
})

document.querySelector('#sell-quantity').addEventListener('input', function() {
    calculateTotal('#sell-quantity', '#sell-price', '#sell-stock-currency', '#sell-total')
})


async function buyStock() {
    // 1. Get all values from buy modal
    const ticker = document.querySelector('#buy-ticker').innerHTML
    const quantity = document.querySelector('#buy-quantity').value
    const price = document.querySelector('#buy-price').value
    const fee = document.querySelector('#buy-fee').value

    // 2. API call
    await fetch('/api/transactions/buy', {
        method: 'POST',
        headers: {'Content-type': 'application/json'},
        body: JSON.stringify({
            portfolio_id: portfolioId, 
            ticker, 
            quantity, 
            price,
            fee
        })
    })

    // 3. Reset buy modal
    resetModal(
        ['#buy-quantity', '#buy-fee', '#buy-price'],
        ['#buy-ticker', '#buy-company', '#buy-total', '#buy-stock-currency', '#buy-total-currency' ]
    )

    // 4. Close buy modal and reload holdings
    closeModal('buy-modal')
    loadHoldings(portfolioId)
    loadPortfolioGainData(portfolioId)
    lucide.createIcons()

}

async function sellStock(maxShares) {
    // 1. Get all values from sell-modal
    const ticker = document.querySelector('#sell-ticker').innerHTML
    const quantity = document.querySelector('#sell-quantity').value
    const price = document.querySelector('#sell-price').value
    const fee = document.querySelector('#sell-fee').value

    if (quantity > maxShares) {
        alert(`You can't sell more than ${maxShares} positions !`)
        return
    }

    // 2. API call
    await fetch('/api/transactions/sell', {
        method: 'POST',
        headers: {'Content-type': 'application/json'},
        body: JSON.stringify({
            portfolio_id : portfolioId,
            ticker,
            quantity,
            price,
            fee
        })
    })

    // 3. Reset sell modal
    resetModal(
        ['#sell-quantity', '#sell-fee', '#sell-price'],
        ['#sell-ticker', '#sell-company', '#sell-total', '#sell-stock-currency' ]
    )

    // 4. Close sell modal and reload holdings
    closeModal('sell-modal')
    loadHoldings(portfolioId)
    loadPortfolioGainData(portfolioId)
    loadPortfolioRealizedGain(portfolioId)
    lucide.createIcons()
}

// Portfolio total value, life
async function loadPortfolioValue(portfolioId) {
    // 1. API call
    const response = await fetch(`/api/portfolios/${portfolioId}`)

    // 2. Convert into JSON
    const portfolio = await response.json()

    // 3. Diplay in the DOM
    document.querySelector('#portfolio-name').innerHTML = portfolio.name
    document.querySelector('#portfolio-currency').innerHTML = portfolio.currency

    portfolioCurrency = document.querySelector('#portfolio-currency').innerHTML


    lucide.createIcons()
}



// Fecth total gain, gain percent, total value and invested value
async function loadPortfolioGainData(portfolioId) {

    // API call
    const response = await fetch(`/api/portfolios/${portfolioId}/gain`)
    const gainData = await response.json()

    // Current value
    document.querySelector('#portfolio-total-value').innerHTML = `${gainData.current_value.toLocaleString('fr-FR', {
        minimumFractionDigits: 2, 
        maximumFractionDigits: 2
    })}`

    // Invested value
    document.querySelector('#portfolio-invested-value').innerHTML = 
    `${gainData.total_invested.toLocaleString('fr-FR', {
        minimumFractionDigits: 2, 
        maximumFractionDigits: 2
    })}`

    // Gain
    const gainElement = document.querySelector('#portfolio-gain')
    gainElement.innerHTML = `${gainData.gain.toLocaleString('fr-FR', {
        minimumFractionDigits: 2, 
        maximumFractionDigits: 2
    })} (${gainData.gain_percent.toLocaleString('fr-FR', {
        minimumFractionDigits: 2, 
        maximumFractionDigits: 2
    })}%)`

    
    // Color wether it's a profit/loss
    gainElement.classList.remove('text-green-500', 'text-red-500')

    if (gainData.gain >= 0) {
        gainElement.classList.add('text-green-500')
    } else {
        gainElement.classList.add('text-red-500')
    }
}

// Fecth total realized gain + conditional display
async function loadPortfolioRealizedGain(portfolioId) {
    // API call
    const response = await fetch(`/api/transactions/portfolio/${portfolioId}/realized-gain`)
    const gainData = await response.json()

    //Display value in the DOM
    const gainElement = document.querySelector('#portfolio-realized-gain')
    gainElement.innerHTML = gainData.total_realized_gain.toLocaleString('fr-FR', {
        minimumFractionDigits: 2, 
        maximumFractionDigits: 2
    })

    // Color wether it's a profit/loss
    gainElement.classList.remove('text-green-500', 'text-red-500')
    if (gainData.total_realized_gain >= 0) {
        gainElement.classList.add('text-green-500')
    } else {
        gainElement.classList.add('text-red-500')
    }
}


// API call at page loading 
loadPortfolio(portfolioId) // Quick (just DB)
loadHoldings(portfolioId)  // Quick (just DB)
loadPortfolioRealizedGain(portfolioId) // Quick (just DB)

loadPortfolioValue(portfolioId)  // Slow (yfinance)
loadPortfolioGainData(portfolioId)  // Slow (yfinance)
