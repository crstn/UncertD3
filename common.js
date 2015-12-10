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
      .range([0, 10]);

// function to scale bubble opacity based on data (GPS accuracy)
var opacity = d3.scale.linear()
      .domain([0, 7])
      .range([1, 0.2]);

function randomize(cardata){
      // replace accuracy with random values
      for(var d in cardata.features){
          cardata.features[d].properties.accuracy = Math.floor((Math.random() * 8));;
      }

      return cardata;
}
