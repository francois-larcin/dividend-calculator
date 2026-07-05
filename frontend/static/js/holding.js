const portfolioId = document.querySelector('#app').dataset.portfolioId
const stockId = document.querySelector('#app').dataset.stockId

// Load all holding related data
async function loadHoldingDetail(portfolioId, stockId) {
    // 1. API call
    const response = await fetch(`/api/holdings/${portfolioId}/${stockId}/detail`)

    // 2. Convert into JSON
    const data = await response.json()

    // 3. Display in the DOM
    document.querySelector('#holding-company').innerHTML = data.company_name
    document.querySelector('#holding-ticker').innerHTML = data.ticker
    document.querySelector('#holding-description').innerHTML = data.description
    document.querySelector('#holding-unrealized-gain').innerHTML = data.gain.toLocaleString('fr-FR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    })
    document.querySelector('#holding-realized-gain').innerHTML = data.realized_gain
    document.querySelector('#holding-weight').innerHTML = data.weight.toLocaleString('fr-FR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    })
    document.querySelector('#holding-total-invested').innerHTML = data.total_invested.toLocaleString('fr-FR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    })
    console.log(data);


    lucide.createIcons()
}

//API calls at page loading

loadHoldingDetail(portfolioId, stockId)
