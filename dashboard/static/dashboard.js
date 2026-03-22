// dashboard.js
// Currently placeholder for future JS interactions
// Example: auto-refresh data every 10 seconds
setInterval(() => {
    fetch('/api/users')
        .then(res => res.json())
        .then(data => console.log('Users updated', data));
    fetch('/api/leads')
        .then(res => res.json())
        .then(data => console.log('Leads updated', data));
}, 10000);