var width  = 1000,
    height = 1000;

var blocks = d3.select("#js-geojson-example").append("svg")
      .attr("width", width)
      .attr("height", height);

var car = d3.select("#js-geojson-example").append("svg")
      .attr("width", width)
      .attr("height", height);

// function to scale bubble size based on data (GPS accuracy)
var radius = d3.scale.sqrt()
      .domain([0, 7])
      .range([2, 10]);

// function to scale bubble opacity based on data (GPS accuracy)
var opacity = d3.scale.linear()
      .domain([0, 7])
      .range([1, 0.3]);

function randomize(cardata){
      // replace accuracy with random values [2..6]
      for(var d in cardata.features){
          cardata.features[d].properties.accuracy = Math.floor((Math.random() * 5)) + 2;
      }

      // Then set one random element to min (1) and max (7)
      cardata.features[Math.floor((Math.random() * cardata.features.length + 1))].properties.accuracy = 1;
      cardata.features[Math.floor((Math.random() * cardata.features.length + 1))].properties.accuracy = 7;

      return cardata;
}
