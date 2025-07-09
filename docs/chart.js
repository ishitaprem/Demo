async function fetchData() {
  const response = await fetch('data.json');
  return await response.json();
}

fetchData().then(data => {
  const ctx1 = document.getElementById('statusChart').getContext('2d');
  const ctx2 = document.getElementById('labelChart').getContext('2d');

  new Chart(ctx1, {
    type: 'bar',
    data: {
      labels: ['Open', 'Closed'],
      datasets: [{
        label: 'Issues by Status',
        data: [data.open_issues, data.closed_issues],
        backgroundColor: ['#36a2eb', '#4caf50']
      }]
    }
  });

  new Chart(ctx2, {
    type: 'pie',
    data: {
      labels: Object.keys(data.labels),
      datasets: [{
        label: 'Labels',
        data: Object.values(data.labels),
        backgroundColor: ['#ff6384', '#ffcd56', '#4bc0c0', '#9966ff', '#e7e9ed']
      }]
    }
  });
});
