const url = window.location.href
const searchForm = document.getElementById('search-form')
const searchInput = document.getElementById('search-input')
const resultsBox = document.getElementById('results-box')

const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value
const sendSearchData = (user) => {
    $.ajax({
        type: 'POST',
        url: 'search_results',
        data: {
            'csrfmiddlewaretoken': csrf,
            'user': user
        },
        success: (res) => {
            console.log(res)
            const data = JSON.parse(res.data)
            if (Array.isArray(data) && data.length > 0) {
                resultsBox.innerHTML = '';
                data.forEach(user => {
                    resultsBox.innerHTML += `
                    <a href="/profile/${user.username}">
                        <div class="user">
                            
                                <div class="user-image">
                                    <img src="${user.image}">
                                </div>
                                <div class="user-details">
                                    <p>${user.username}</p>
                                </div>
                            
                        </div>
                        </a>
                        <hr>`;
                });
            } else {
                if (searchInput.value.length > 0) {
                    resultsBox.innerHTML = `<b>${data}</b>`

                } else {
                    resultsBox.classList.add('not-visible')
                }
            }
        },
        error: (err) => {
            console.log(err)
        },
    })
}

// Add an event listener on the search input that listens for the input event
searchInput.addEventListener('input', e => {

    if (e.target.value === '') {
        // If the input value is empty, clear the results box
        resultsBox.innerHTML = ''
    } else {
        // Otherwise, send the search data
        if (resultsBox.classList.contains('not-visible')) {
            resultsBox.classList.remove('not-visible')
        }
        sendSearchData(e.target.value)
    }
})