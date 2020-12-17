//datatable
$(document).ready(function() {
    $('#player-score-table').DataTable({
        order: [[ 0, "asc" ]],
        columnDefs: [
            { orderable: false, targets: [2, 7, 8]}
        ],
        pagingType: "full_numbers"
    });
} );


//plotly
var data = [{
  values: [19, 26, 55, 18, 8],
  labels: ['NM', 'HD', 'HR', 'DT', 'FM/TB'],
  marker:{
      colors: ["#6d9eeb", "#ffd966" , "#e06666", "#8e7cc3", "#93c47d"]
  },
  sort: false,
  type: 'pie'
}];

var layout = {
  legend:{
      font:{
          color:"#FFF"
      }
  },
  paper_bgcolor:"rgba(0,0,0,0)",
  plot_bgcolor:"rgba(0,0,0,0)",
  height: 390
};

var config = {
    responsive: true
}

let pie_element =  document.getElementById("mod-chart");
Plotly.newPlot(pie_element, data, layout, config);

var x = [];
for (var i = 0; i < 500; i ++) {
	x[i] = Math.random();
}

var trace = {
    x: x,
    type: 'histogram',
  };
var data = [trace];

let histogram_element =  document.getElementById("score-histogram");
Plotly.newPlot(histogram_element, data, layout, config);