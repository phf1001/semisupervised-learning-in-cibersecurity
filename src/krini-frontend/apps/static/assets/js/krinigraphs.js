// Krini graphs
var clsNames = $('#cls-names').data('cls-names');
clsNames = clsNames.replace(/'/g, '"');
clsNames = JSON.parse(clsNames);
var clsValues = $('#cls-scores').data('cls-scores');
var scoresChartGlobal;
var lastClsIndex = 0;
var nCls = clsNames.length;


// Bars chart

var BarsChartModels = (function () {

	//
	// Variables
	//

	var $chart = $('#chart-bars-models');
	var model_data = clsValues[0];
	document.getElementById("h6-cls-score-graph").innerText = clsNames[0];

	//
	// Methods
	//

	// Init chart
	function initChart($chart) {

		// Create chart
		var scoresChart = new Chart($chart, {
			type: 'bar',
			data: {
				labels: ['Accuracy', 'Precision', 'Recall'],
				datasets: [{
					label: 'Score',
					data: model_data
				}]
			},
			options: {
				scales: {
					yAxes: [{
						ticks: {
							min: 0,
							max: 1,
							precision: 1
						}
					}]
				},
				legend: {
					display: false
				}
			}
		});

		scoresChartGlobal = scoresChart;

		// Save to jQuery object
		$chart.data('chart', scoresChart);
	}


	// Init chart
	if ($chart.length) {
		initChart($chart);
	}

})();

'use strict';


var nextClsButton = document.getElementById('btn-next-cls-graph');
nextClsButton.addEventListener('click', function () {

	var nextClsIndex = (lastClsIndex + 1) % nCls;
	var nameCls = clsNames[nextClsIndex];
	document.getElementById("h6-cls-score-graph").innerText = nameCls;

	var $chart = $('#chart-bars-models');
	var model_data = clsValues[nextClsIndex];

	// Update chart
	function updateChart($chart) {

		var scoresChart = scoresChartGlobal;
		scoresChart.data.datasets[0].data = model_data;
		scoresChart.update();
		$chart.data('chart', scoresChart);
	}

	if ($chart.length) {
		updateChart($chart);
	}

	lastClsIndex = nextClsIndex;
});




var PieChartPhishing = (function () {

	//
	// Variables
	//

	var $chart = $('#chart-pie-phishing');
	var sum_data = $('#cls-numeric-predictions-sum').data('cls-numeric-predictions-sum');
	console.log(sum_data)

	//
	// Methods
	//

	// Init chart
	function initChart($chart) {

		// Create chart
		var piePhishingChart = new Chart($chart, {

			type: 'doughnut',

			data: {
				datasets: [
					{
						data: sum_data,
						backgroundColor: [
							'rgb(75, 192, 192)',
							'rgb(255, 99, 132)'
						],
					},
				],
				labels: ['Legítima', 'Phishing'],
			},
			options: {
				cutoutPercentage: 45,
				legend: {
					display: true
				}
			},
			plugins: {
				legend: {
					display: true,
					position: 'bottom',
					title: {
						display: true,
						padding: 10,
					},
				}
			}
	});

		// Save to jQuery object
		$chart.data('chart', piePhishingChart);
	}


	// Init chart
	if ($chart.length) {
		initChart($chart);
	}

})();

'use strict';