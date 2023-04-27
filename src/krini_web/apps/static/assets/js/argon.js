
/*!

=========================================================
* Argon Dashboard - v1.2.0
=========================================================

* Product Page: https://www.creative-tim.com/product/argon-dashboard
* Copyright 2020 Creative Tim (https://www.creative-tim.com)
* Licensed under MIT (https://github.com/creativetimofficial/argon-dashboard/blob/master/LICENSE.md)

* Coded by www.creative-tim.com

=========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

*/



//
// Layout
//

'use strict';

var Layout = (function () {

	function pinSidenav() {
		$('.sidenav-toggler').addClass('active');
		$('.sidenav-toggler').data('action', 'sidenav-unpin');
		$('body').removeClass('g-sidenav-hidden').addClass('g-sidenav-show g-sidenav-pinned');
		$('body').append('<div class="backdrop d-xl-none" data-action="sidenav-unpin" data-target=' + $('#sidenav-main').data('target') + ' />');

		// Store the sidenav state in a cookie session
		Cookies.set('sidenav-state', 'pinned');
	}

	function unpinSidenav() {
		$('.sidenav-toggler').removeClass('active');
		$('.sidenav-toggler').data('action', 'sidenav-pin');
		$('body').removeClass('g-sidenav-pinned').addClass('g-sidenav-hidden');
		$('body').find('.backdrop').remove();

		// Store the sidenav state in a cookie session
		Cookies.set('sidenav-state', 'unpinned');
	}

	// Set sidenav state from cookie

	var $sidenavState = Cookies.get('sidenav-state') ? Cookies.get('sidenav-state') : 'pinned';

	if ($(window).width() > 1200) {
		if ($sidenavState == 'pinned') {
			pinSidenav()
		}

		if (Cookies.get('sidenav-state') == 'unpinned') {
			unpinSidenav()
		}

		$(window).resize(function () {
			if ($('body').hasClass('g-sidenav-show') && !$('body').hasClass('g-sidenav-pinned')) {
				$('body').removeClass('g-sidenav-show').addClass('g-sidenav-hidden');
			}
		})
	}

	if ($(window).width() < 1200) {
		$('body').removeClass('g-sidenav-hide').addClass('g-sidenav-hidden');
		$('body').removeClass('g-sidenav-show');
		$(window).resize(function () {
			if ($('body').hasClass('g-sidenav-show') && !$('body').hasClass('g-sidenav-pinned')) {
				$('body').removeClass('g-sidenav-show').addClass('g-sidenav-hidden');
			}
		})
	}



	$("body").on("click", "[data-action]", function (e) {

		e.preventDefault();

		var $this = $(this);
		var action = $this.data('action');
		var target = $this.data('target');


		// Manage actions

		switch (action) {
			case 'sidenav-pin':
				pinSidenav();
				break;

			case 'sidenav-unpin':
				unpinSidenav();
				break;

			case 'search-show':
				target = $this.data('target');
				$('body').removeClass('g-navbar-search-show').addClass('g-navbar-search-showing');

				setTimeout(function () {
					$('body').removeClass('g-navbar-search-showing').addClass('g-navbar-search-show');
				}, 150);

				setTimeout(function () {
					$('body').addClass('g-navbar-search-shown');
				}, 300)
				break;

			case 'search-close':
				target = $this.data('target');
				$('body').removeClass('g-navbar-search-shown');

				setTimeout(function () {
					$('body').removeClass('g-navbar-search-show').addClass('g-navbar-search-hiding');
				}, 150);

				setTimeout(function () {
					$('body').removeClass('g-navbar-search-hiding').addClass('g-navbar-search-hidden');
				}, 300);

				setTimeout(function () {
					$('body').removeClass('g-navbar-search-hidden');
				}, 500);
				break;
		}
	})


	// Add sidenav modifier classes on mouse events

	$('.sidenav').on('mouseenter', function () {
		if (!$('body').hasClass('g-sidenav-pinned')) {
			$('body').removeClass('g-sidenav-hide').removeClass('g-sidenav-hidden').addClass('g-sidenav-show');
		}
	})

	$('.sidenav').on('mouseleave', function () {
		if (!$('body').hasClass('g-sidenav-pinned')) {
			$('body').removeClass('g-sidenav-show').addClass('g-sidenav-hide');

			setTimeout(function () {
				$('body').removeClass('g-sidenav-hide').addClass('g-sidenav-hidden');
			}, 300);
		}
	})


	// Make the body full screen size if it has not enough content inside
	$(window).on('load resize', function () {
		if ($('body').height() < 800) {
			$('body').css('min-height', '100vh');
			$('#footer-main').addClass('footer-auto-bottom')
		}
	})

})();

//
// Charts
//

'use strict';

var Charts = (function () {

	// Variable

	var $toggle = $('[data-toggle="chart"]');
	var mode = 'light';//(themeMode) ? themeMode : 'light';
	var fonts = {
		base: 'Open Sans'
	}

	// Colors
	var colors = {
		gray: {
			100: '#f6f9fc',
			200: '#e9ecef',
			300: '#dee2e6',
			400: '#ced4da',
			500: '#adb5bd',
			600: '#8898aa',
			700: '#525f7f',
			800: '#32325d',
			900: '#212529'
		},
		theme: {
			'default': '#172b4d',
			'primary': '#5e72e4',
			'secondary': '#f4f5f7',
			'info': '#11cdef',
			'success': '#2dce89',
			'danger': '#f5365c',
			'warning': '#fb6340'
		},
		black: '#12263F',
		white: '#FFFFFF',
		transparent: 'transparent',
	};


	// Methods

	// Chart.js global options
	function chartOptions() {

		// Options
		var options = {
			defaults: {
				global: {
					responsive: true,
					maintainAspectRatio: false,
					defaultColor: (mode == 'dark') ? colors.gray[700] : colors.gray[600],
					defaultFontColor: (mode == 'dark') ? colors.gray[700] : colors.gray[600],
					defaultFontFamily: fonts.base,
					defaultFontSize: 13,
					layout: {
						padding: 0
					},
					legend: {
						display: false,
						position: 'bottom',
						labels: {
							usePointStyle: true,
							padding: 16
						}
					},
					elements: {
						point: {
							radius: 0,
							backgroundColor: colors.theme['primary']
						},
						line: {
							tension: .4,
							borderWidth: 4,
							borderColor: colors.theme['primary'],
							backgroundColor: colors.transparent,
							borderCapStyle: 'rounded'
						},
						rectangle: {
							backgroundColor: colors.theme['warning']
						},
						arc: {
							backgroundColor: colors.theme['primary'],
							borderColor: (mode == 'dark') ? colors.gray[800] : colors.white,
							borderWidth: 4
						}
					},
					tooltips: {
						enabled: true,
						mode: 'index',
						intersect: false,
					}
				},
				doughnut: {
					cutoutPercentage: 83,
					legendCallback: function (chart) {
						var data = chart.data;
						var content = '';

						data.labels.forEach(function (label, index) {
							var bgColor = data.datasets[0].backgroundColor[index];

							content += '<span class="chart-legend-item">';
							content += '<i class="chart-legend-indicator" style="background-color: ' + bgColor + '"></i>';
							content += label;
							content += '</span>';
						});

						return content;
					}
				}
			}
		}

		// yAxes
		Chart.scaleService.updateScaleDefaults('linear', {
			gridLines: {
				borderDash: [2],
				borderDashOffset: [2],
				color: (mode == 'dark') ? colors.gray[900] : colors.gray[300],
				drawBorder: false,
				drawTicks: false,
				drawOnChartArea: true,
				zeroLineWidth: 0,
				zeroLineColor: 'rgba(0,0,0,0)',
				zeroLineBorderDash: [2],
				zeroLineBorderDashOffset: [2]
			},
			ticks: {
				beginAtZero: true,
				padding: 10,
				callback: function (value) {
					if (!(value % 10)) {
						return value
					}
				}
			}
		});

		// xAxes
		Chart.scaleService.updateScaleDefaults('category', {
			gridLines: {
				drawBorder: false,
				drawOnChartArea: false,
				drawTicks: false
			},
			ticks: {
				padding: 20
			},
			maxBarThickness: 10
		});

		return options;

	}

	// Parse global options
	function parseOptions(parent, options) {
		for (var item in options) {
			if (typeof options[item] !== 'object') {
				parent[item] = options[item];
			} else {
				parseOptions(parent[item], options[item]);
			}
		}
	}

	// Push options
	function pushOptions(parent, options) {
		for (var item in options) {
			if (Array.isArray(options[item])) {
				options[item].forEach(function (data) {
					parent[item].push(data);
				});
			} else {
				pushOptions(parent[item], options[item]);
			}
		}
	}

	// Pop options
	function popOptions(parent, options) {
		for (var item in options) {
			if (Array.isArray(options[item])) {
				options[item].forEach(function (data) {
					parent[item].pop();
				});
			} else {
				popOptions(parent[item], options[item]);
			}
		}
	}

	// Toggle options
	function toggleOptions(elem) {
		var options = elem.data('add');
		var $target = $(elem.data('target'));
		var $chart = $target.data('chart');

		if (elem.is(':checked')) {

			// Add options
			pushOptions($chart, options);

			// Update chart
			$chart.update();
		} else {

			// Remove options
			popOptions($chart, options);

			// Update chart
			$chart.update();
		}
	}

	// Update options
	function updateOptions(elem) {
		var options = elem.data('update');
		var $target = $(elem.data('target'));
		var $chart = $target.data('chart');

		// Parse options
		parseOptions($chart, options);

		// Toggle ticks
		toggleTicks(elem, $chart);

		// Update chart
		$chart.update();
	}

	// Toggle ticks
	function toggleTicks(elem, $chart) {

		if (elem.data('prefix') !== undefined || elem.data('suffix') !== undefined) {
			var prefix = elem.data('prefix') ? elem.data('prefix') : '';
			var suffix = elem.data('suffix') ? elem.data('suffix') : '';

			// Update ticks
			$chart.options.scales.yAxes[0].ticks.callback = function (value) {
				if (!(value % 10)) {
					return prefix + value + suffix;
				}
			}

			// Update tooltips
			$chart.options.tooltips.callbacks.label = function (item, data) {
				var label = data.datasets[item.datasetIndex].label || '';
				var yLabel = item.yLabel;
				var content = '';

				if (data.datasets.length > 1) {
					content += '<span class="popover-body-label mr-auto">' + label + '</span>';
				}

				content += '<span class="popover-body-value">' + prefix + yLabel + suffix + '</span>';
				return content;
			}

		}
	}


	// Events

	// Parse global options
	if (window.Chart) {
		parseOptions(Chart, chartOptions());
	}

	// Toggle options
	$toggle.on({
		'change': function () {
			var $this = $(this);

			if ($this.is('[data-add]')) {
				toggleOptions($this);
			}
		},
		'click': function () {
			var $this = $(this);

			if ($this.is('[data-update]')) {
				updateOptions($this);
			}
		}
	});


	// Return

	return {
		colors: colors,
		fonts: fonts,
		mode: mode
	};

})();

//
// Icon code copy/paste
//

'use strict';

var CopyIcon = (function () {

	// Variables

	var $element = '.btn-icon-clipboard',
		$btn = $($element);


	// Methods

	function init($this) {
		$this.tooltip().on('mouseleave', function () {
			// Explicitly hide tooltip, since after clicking it remains
			// focused (as it's a button), so tooltip would otherwise
			// remain visible until focus is moved away
			$this.tooltip('hide');
		});

		var clipboard = new ClipboardJS($element);

		clipboard.on('success', function (e) {
			$(e.trigger)
				.attr('title', 'Copied!')
				.tooltip('_fixTitle')
				.tooltip('show')
				.attr('title', 'Copy to clipboard')
				.tooltip('_fixTitle')

			e.clearSelection()
		});
	}


	// Events
	if ($btn.length) {
		init($btn);
	}

})();

//
// Navbar
//

'use strict';

var Navbar = (function () {

	// Variables

	var $nav = $('.navbar-nav, .navbar-nav .nav');
	var $collapse = $('.navbar .collapse');
	var $dropdown = $('.navbar .dropdown');

	// Methods

	function accordion($this) {
		$this.closest($nav).find($collapse).not($this).collapse('hide');
	}

	function closeDropdown($this) {
		var $dropdownMenu = $this.find('.dropdown-menu');

		$dropdownMenu.addClass('close');

		setTimeout(function () {
			$dropdownMenu.removeClass('close');
		}, 200);
	}


	// Events

	$collapse.on({
		'show.bs.collapse': function () {
			accordion($(this));
		}
	})

	$dropdown.on({
		'hide.bs.dropdown': function () {
			closeDropdown($(this));
		}
	})

})();


//
// Navbar collapse
//


var NavbarCollapse = (function () {

	// Variables

	var $nav = $('.navbar-nav'),
		$collapse = $('.navbar .navbar-custom-collapse');


	// Methods

	function hideNavbarCollapse($this) {
		$this.addClass('collapsing-out');
	}

	function hiddenNavbarCollapse($this) {
		$this.removeClass('collapsing-out');
	}


	// Events

	if ($collapse.length) {
		$collapse.on({
			'hide.bs.collapse': function () {
				hideNavbarCollapse($collapse);
			}
		})

		$collapse.on({
			'hidden.bs.collapse': function () {
				hiddenNavbarCollapse($collapse);
			}
		})
	}

	var navbar_menu_visible = 0;

	$(".sidenav-toggler").click(function () {
		if (navbar_menu_visible == 1) {
			$('body').removeClass('nav-open');
			navbar_menu_visible = 0;
			$('.bodyClick').remove();

		} else {

			var div = '<div class="bodyClick"></div>';
			$(div).appendTo('body').click(function () {
				$('body').removeClass('nav-open');
				navbar_menu_visible = 0;
				$('.bodyClick').remove();

			});

			$('body').addClass('nav-open');
			navbar_menu_visible = 1;

		}

	});

})();

//
// Popover
//

'use strict';

var Popover = (function () {

	// Variables

	var $popover = $('[data-toggle="popover"]'),
		$popoverClass = '';


	// Methods

	function init($this) {
		if ($this.data('color')) {
			$popoverClass = 'popover-' + $this.data('color');
		}

		var options = {
			trigger: 'focus',
			template: '<div class="popover ' + $popoverClass + '" role="tooltip"><div class="arrow"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>'
		};

		$this.popover(options);
	}


	// Events

	if ($popover.length) {
		$popover.each(function () {
			init($(this));
		});
	}

})();

//
// Scroll to (anchor links)
//

'use strict';

var ScrollTo = (function () {

	//
	// Variables
	//

	var $scrollTo = $('.scroll-me, [data-scroll-to], .toc-entry a');


	//
	// Methods
	//

	function scrollTo($this) {
		var $el = $this.attr('href');
		var offset = $this.data('scroll-to-offset') ? $this.data('scroll-to-offset') : 0;
		var options = {
			scrollTop: $($el).offset().top - offset
		};

		// Animate scroll to the selected section
		$('html, body').stop(true, true).animate(options, 600);

		event.preventDefault();
	}


	//
	// Events
	//

	if ($scrollTo.length) {
		$scrollTo.on('click', function (event) {
			scrollTo($(this));
		});
	}

})();

//
// Tooltip
//

'use strict';

var Tooltip = (function () {

	// Variables

	var $tooltip = $('[data-toggle="tooltip"]');


	// Methods

	function init() {
		$tooltip.tooltip();
	}


	// Events

	if ($tooltip.length) {
		init();
	}

})();

//
// Form control
//

'use strict';

var FormControl = (function () {

	// Variables

	var $input = $('.form-control');


	// Methods

	function init($this) {
		$this.on('focus blur', function (e) {
			$(this).parents('.form-group').toggleClass('focused', (e.type === 'focus'));
		}).trigger('blur');
	}


	// Events

	if ($input.length) {
		init($input);
	}

})();

//
// Google maps
//

var $map = $('#map-default'),
	map,
	lat,
	lng,
	color = "#5e72e4";

function initMap() {

	map = document.getElementById('map-default');
	lat = map.getAttribute('data-lat');
	lng = map.getAttribute('data-lng');

	var myLatlng = new google.maps.LatLng(lat, lng);
	var mapOptions = {
		zoom: 12,
		scrollwheel: false,
		center: myLatlng,
		mapTypeId: google.maps.MapTypeId.ROADMAP,
	}

	map = new google.maps.Map(map, mapOptions);

	var marker = new google.maps.Marker({
		position: myLatlng,
		map: map,
		animation: google.maps.Animation.DROP,
		title: 'Hello World!'
	});

	var contentString = '<div class="info-window-content"><h2>Argon Dashboard</h2>' +
		'<p>A beautiful Dashboard for Bootstrap 4. It is Free and Open Source.</p></div>';

	var infowindow = new google.maps.InfoWindow({
		content: contentString
	});

	google.maps.event.addListener(marker, 'click', function () {
		infowindow.open(map, marker);
	});
}

if ($map.length) {
	google.maps.event.addDomListener(window, 'load', initMap);
}

//
// Bars chart
//

var BarsChart = (function () {

	//
	// Variables
	//

	var $chart = $('#chart-bars');


	//
	// Methods
	//

	// Init chart
	function initChart($chart) {

		// Create chart
		var ordersChart = new Chart($chart, {
			type: 'bar',
			data: {
				labels: ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
				datasets: [{
					label: 'Sales',
					data: [25, 20, 30, 22, 17, 29]
				}]
			}
		});

		// Save to jQuery object
		$chart.data('chart', ordersChart);
	}


	// Init chart
	if ($chart.length) {
		initChart($chart);
	}

})();

'use strict';

//
// Sales chart
//

var SalesChart = (function () {

	// Variables

	var $chart = $('#chart-sales-dark');


	// Methods

	function init($chart) {

		var salesChart = new Chart($chart, {
			type: 'line',
			options: {
				scales: {
					yAxes: [{
						gridLines: {
							lineWidth: 1,
							color: Charts.colors.gray[900],
							zeroLineColor: Charts.colors.gray[900]
						},
						ticks: {
							callback: function (value) {
								if (!(value % 10)) {
									return '$' + value + 'k';
								}
							}
						}
					}]
				},
				tooltips: {
					callbacks: {
						label: function (item, data) {
							var label = data.datasets[item.datasetIndex].label || '';
							var yLabel = item.yLabel;
							var content = '';

							if (data.datasets.length > 1) {
								content += '<span class="popover-body-label mr-auto">' + label + '</span>';
							}

							content += '<span class="popover-body-value">$' + yLabel + 'k</span>';
							return content;
						}
					}
				}
			},
			data: {
				labels: ['May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
				datasets: [{
					label: 'Performance',
					data: [0, 20, 10, 30, 15, 40, 20, 60, 60]
				}]
			}
		});

		// Save to jQuery object

		$chart.data('chart', salesChart);

	};


	// Events

	if ($chart.length) {
		init($chart);
	}

})();

//
// Bootstrap Datepicker
//

'use strict';

var Datepicker = (function () {

	// Variables

	var $datepicker = $('.datepicker');


	// Methods

	function init($this) {
		var options = {
			disableTouchKeyboard: true,
			autoclose: false
		};

		$this.datepicker(options);
	}


	// Events

	if ($datepicker.length) {
		$datepicker.each(function () {
			init($(this));
		});
	}

})();

//
// Form control
//

'use strict';

var noUiSlider = (function () {

	// Variables

	// var $sliderContainer = $('.input-slider-container'),
	// 		$slider = $('.input-slider'),
	// 		$sliderId = $slider.attr('id'),
	// 		$sliderMinValue = $slider.data('range-value-min');
	// 		$sliderMaxValue = $slider.data('range-value-max');;


	// // Methods
	//
	// function init($this) {
	// 	$this.on('focus blur', function(e) {
	//       $this.parents('.form-group').toggleClass('focused', (e.type === 'focus' || this.value.length > 0));
	//   }).trigger('blur');
	// }
	//
	//
	// // Events
	//
	// if ($input.length) {
	// 	init($input);
	// }



	if ($(".input-slider-container")[0]) {
		$('.input-slider-container').each(function () {

			var slider = $(this).find('.input-slider');
			var sliderId = slider.attr('id');
			var minValue = slider.data('range-value-min');
			var maxValue = slider.data('range-value-max');

			var sliderValue = $(this).find('.range-slider-value');
			var sliderValueId = sliderValue.attr('id');
			var startValue = sliderValue.data('range-value-low');

			var c = document.getElementById(sliderId),
				d = document.getElementById(sliderValueId);

			noUiSlider.create(c, {
				start: [parseInt(startValue)],
				connect: [true, false],
				//step: 1000,
				range: {
					'min': [parseInt(minValue)],
					'max': [parseInt(maxValue)]
				}
			});

			c.noUiSlider.on('update', function (a, b) {
				d.textContent = a[b];
			});
		})
	}

	if ($("#input-slider-range")[0]) {
		var c = document.getElementById("input-slider-range"),
			d = document.getElementById("input-slider-range-value-low"),
			e = document.getElementById("input-slider-range-value-high"),
			f = [d, e];

		noUiSlider.create(c, {
			start: [parseInt(d.getAttribute('data-range-value-low')), parseInt(e.getAttribute('data-range-value-high'))],
			connect: !0,
			range: {
				min: parseInt(c.getAttribute('data-range-value-min')),
				max: parseInt(c.getAttribute('data-range-value-max'))
			}
		}), c.noUiSlider.on("update", function (a, b) {
			f[b].textContent = a[b]
		})
	}

})();

//
// Scrollbar
//

'use strict';

var Scrollbar = (function () {

	// Variables

	var $scrollbar = $('.scrollbar-inner');


	// Methods

	function init() {
		$scrollbar.scrollbar().scrollLock()
	}


	// Events

	if ($scrollbar.length) {
		init();
	}

})();



// Krini 
$("[data-toggle=myCollapse]").click(function (ev) {
	ev.preventDefault();
	var target;
	if (this.hasAttribute('data-target')) {
		target = $(this.getAttribute('data-target'));
	} else {
		target = $(this.getAttribute('href'));
	};
	target.toggleClass("in");
});


function showDiv(hd1, hd2, hd3, element) {

	if (element.value == 0) {
		document.getElementById(hd1).style.display = 'none'
		document.getElementById(hd2).style.display = 'none'
		document.getElementById(hd3).style.display = 'none'
	}

	if (element.value == 1) {
		document.getElementById(hd1).style.display = 'block'
		document.getElementById(hd2).style.display = 'none'
		document.getElementById(hd3).style.display = 'none'
	}

	else if (element.value == 2) {
		document.getElementById(hd1).style.display = 'none'
		document.getElementById(hd2).style.display = 'block'
		document.getElementById(hd3).style.display = 'none'
	}

	else if (element.value == 3) {
		document.getElementById(hd1).style.display = 'none'
		document.getElementById(hd2).style.display = 'none'
		document.getElementById(hd3).style.display = 'block'
	}
}



// Krini graphs

var clsNames = $('#cls-names').data('cls-names');
// Cls values is a list of lists containing decimals
var clsValues = $('#cls-scores').data('cls-scores');

// Only the dashboard or the test page contains that element
if (clsValues && clsNames) {
	const graphColours = [
		'rgba(255, 206, 86, 1)',
		'rgba(54, 162, 235, 1)',
		'rgba(75, 192, 192, 1)',
		'rgba(153, 102, 255, 1)',
		'rgb(255, 102, 153)',
		'rgba(255, 159, 64, 1)',
		'rgba(255, 99, 132, 1)',
		'rgba(0, 128, 128, 1)',
		'rgba(170, 255, 195, 1)',
		'rgba(210, 245, 60, 1)',
		'rgba(145, 30, 180, 1)',
		'rgba(0, 0, 128, 1)',
		'rgba(230, 190, 255, 1)',
		'rgba(255, 215, 180, 1)',
		'rgba(170, 110, 40, 1)',
	]

	clsNames = clsNames.replace(/'/g, '"');
	clsNames = JSON.parse(clsNames);
	var nCls = clsNames.length;

	var nMetrics = clsValues[0].length;
	var metrics = ['Accuracy', 'Precision', 'Recall', 'F1 x 100', 'AUC ROC x 100'];
	var accuracys = [];
	var precisions = [];
	var recalls = [];
	var f1s = [];
	var rocs = [];
	var lastClsIndex = 0;
	var clsColours = [];

	for (var i = 0; i < nCls; i++) {
		for (var j = 0; j < nMetrics; j++) {
			clsValues[i][j] = Math.round(clsValues[i][j] * 10000) / 100;
		}
		clsColours.push(graphColours[i % graphColours.length]);
		accuracys.push(clsValues[i][0]);
		precisions.push(clsValues[i][1]);
		recalls.push(clsValues[i][2]);
		f1s.push(clsValues[i][3]);
		rocs.push(clsValues[i][4]);
	}


	if ($('#chart-bars-models') != undefined) {

		var scoresChartGlobal;

		var BarsChartModels = (function () {

			var $chart = $('#chart-bars-models');
			var model_data = clsValues[lastClsIndex];
			document.getElementById("h6-cls-score-graph").innerText = clsNames[0];
			var bckColor = [];
			for (var i = 0; i < nMetrics; i++) {
				bckColor.push(clsColours[0]);
			}

			function initChart($chart) {

				var scoresChart = new Chart($chart, {
					type: 'bar',
					data: {
						labels: metrics,
						datasets: [{
							label: 'Score (%)',
							data: model_data,
							backgroundColor: bckColor,
						}]
					},
					options: {
						scales: {
							yAxes: [{
								ticks: {
									min: 0,
									max: 100
								},
								display: true,
								scaleLabel: {
									display: true,
									labelString: 'Score (%)'
								}
							}]
						},
						legend: {
							display: false
						}
					}
				});

				scoresChartGlobal = scoresChart;
				$chart.data('chart', scoresChart);
			}

			if ($chart.length) {
				initChart($chart);
			}
		})();

		'use strict';

	}

	var nextClsButton = document.getElementById('btn-next-cls-graph');

	if (nextClsButton != undefined) {
		nextClsButton.addEventListener('click', function () {

			var nextClsIndex = (lastClsIndex + 1) % nCls;
			var nameCls = clsNames[nextClsIndex];
			document.getElementById("h6-cls-score-graph").innerText = nameCls;
			var $chart = $('#chart-bars-models');
			var model_data = clsValues[nextClsIndex];

			function updateChart($chart) {

				var scoresChart = scoresChartGlobal;
				scoresChart.data.datasets[0].data = model_data;

				var bckColor = [];
				for (var i = 0; i < nMetrics; i++) {
					bckColor.push(clsColours[nextClsIndex]);
				}

				scoresChart.data.datasets[0].backgroundColor = bckColor;
				scoresChart.update();
				$chart.data('chart', scoresChart);
			}
			if ($chart.length) {
				updateChart($chart);
			}

			lastClsIndex = nextClsIndex;
		});
	}

	if ($('#chart-pie-phishing') != undefined) {

		var PieChartPhishing = (function () {

			var $chart = $('#chart-pie-phishing');
			var sum_data = $('#cls-numeric-predictions-sum').data('cls-numeric-predictions-sum');

			function initChart($chart) {

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
								borderColor: 'transparent',
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
				$chart.data('chart', piePhishingChart);
			}

			if ($chart.length) {
				initChart($chart);
			}

		})();

		'use strict';
	}

	if ($('#chart-bars-general') != undefined) {

		var GeneralChartScores = (function () {
			var $chart = $('#chart-bars-general');

			const data = {
				labels: clsNames,

				datasets: [{
					label: metrics[0],
					data: accuracys,
					backgroundColor: 'rgb(153, 255, 102)'
				},

				{
					label: metrics[1],
					data: precisions,
					backgroundColor: 'rgb(255, 153, 255)'
				},

				{
					label: metrics[2],
					data: recalls,
					backgroundColor: 'rgb(255, 255, 102)'
				},
				{
					label: metrics[3],
					data: f1s,
					backgroundColor: 'rgb(153, 204, 255)'
				},
				{
					label: metrics[4],
					data: rocs,
					backgroundColor: 'rgb(255, 204, 102)'
				}]
			};

			function initChart($chart) {

				var generalChartScores = new Chart($chart, {

					type: 'bar',
					data: data,
					options: {
						scales: {
							yAxes: [{
								ticks: {
									min: 0,
									max: 100
								},
								display: true,
								scaleLabel: {
									display: true,
									labelString: 'Score (%)'
								}
							}]
						},

						legend: {
							display: true,
						}
					},
				});
				$chart.data('chart', generalChartScores);
			}

			if ($chart.length) {
				initChart($chart);
			}
		})();

		'use strict';
	}

	if ($('#chart-bars-test') != undefined) {

		var BarsChartTest = (function () {

			var $chart = $('#chart-bars-test');
			var model_data = clsValues[lastClsIndex];
			document.getElementById("h6-cls-score-graph").innerText = clsNames[0];
			var bckColor = [];
			for (var i = 0; i < nMetrics; i++) {
				bckColor.push(graphColours[i]);
			}

			function initChart($chart) {

				var scoresChart = new Chart($chart, {
					type: 'bar',
					data: {
						labels: metrics,
						datasets: [{
							label: ['Score'],
							data: model_data,
							backgroundColor: bckColor,
						}]
					},
					options: {
						scales: {
							yAxes: [{
								ticks: {
									min: 0,
									max: 100
								},
								display: true,
								scaleLabel: {
									display: true,
									labelString: 'Score (%)'
								}
							}]
						},
						legend: {
							display: false
						}
					}
				});
				$chart.data('chart', scoresChart);
			}

			if ($chart.length) {
				initChart($chart);
			}
		})();
		'use strict';
	}
}