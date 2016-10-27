var width  = 720,
    height = 720;

var scale = 530000;
var offset = [width / 2 + 22850, height / 2 - 9170];
var center = [-71.47496712465082, 41.525055483742605]

var projection = d3.geo.mercator()
  .scale(scale)
  .center(center)
  .translate(offset);

var car = d3.select("#js-geojson-example").append("svg")
      .attr("width", width)
      .attr("height", height);

// add a rectangle to see the bound of the svg
car.append("rect")
  .attr('width', width)
  .attr('height', height)
  .style('stroke', 'black')
  .style('fill', 'none');

// function to scale bubble size based on data (GPS accuracy)
var radius = d3.scale.linear()
      .domain([1, 7])
      .range([3, 10]);

// function to scale bubble opacity based on data (GPS accuracy)
var opacity = d3.scale.linear()
      .domain([1, 7])
      .range([1, 0.3]);

function randomize(cardata){
      // replace accuracy with random values [2..6]
      for(var d in cardata.features){
          cardata.features[d].properties.accuracy = Math.floor((Math.random() * 5)) + 2;
      }

      // Then set one random element to min (1) and max (7)
      var minIndex = Math.floor((Math.random() * cardata.features.length))
      console.log(minIndex)
      cardata.features[minIndex].properties.accuracy = 1;

      // make sure we don't change the same as above, i.e. minIndex needs to be different from maxIndex
      var maxIndex = minIndex
      while(maxIndex == minIndex){
         maxIndex = Math.floor((Math.random() * cardata.features.length))
         console.log(maxIndex)
      }
      cardata.features[maxIndex].properties.accuracy = 7;

      return cardata;
}
