function drawComparison(ticker1, ticker2) {

var margin = {top: 20, right: 80, bottom: 30, left: 80},
    width = 1040 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

var parseDate = d3.time.format("%Y-%m-%d %H:%M").parse;

var x = d3.time.scale()
    .range([0, width]);

var y1 = d3.scale.linear()
    .range([height, 0]);

var y2 = d3.scale.linear()
    .range([height, 0]);

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var yAxis1 = d3.svg.axis()
    .scale(y1)
    .orient("left");

var yAxis2 = d3.svg.axis()
    .scale(y2)
    .orient("right");

var line1 = d3.svg.line()
    .x(function(d) { return x(d.Date); })
    .y(function(d) { return y1(+d.Close); });

var line2 = d3.svg.line()
    .x(function(d) { return x(d.Date); })
    .y(function(d) { return y2(+d.Close); });

var svg = d3.select('#comparison').append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

d3.csv("assets/data/" + ticker1 + ".csv", type, function(error, data1orig) {
  if (error) throw error;
  d3.csv("assets/data/" + ticker2 + ".csv", type, function(error, data2orig) {
    if (error) throw error;
    data1 = []
    data2 = []
    $.each(data1orig, function(i, el) {
      if(data1.length == 0 || data1[data1.length -1].Close != el.Close) data1.push(el);
    });
    $.each(data2orig, function(i, el) {
      if(data2.length == 0 || data2[data2.length -1].Close != el.Close) data2.push(el);
    });
    data1 = data1.slice(data1.length - 200, data1.length);
    data2 = data2.slice(data2.length - 200, data2.length);
    data = data1.concat(data2);

    x.domain(d3.extent(data, function(d) { return d.Date; }));
    y1.domain(d3.extent(data1, function(d) { return +d.Close; }));
    y2.domain(d3.extent(data2, function(d) { return +d.Close; }));

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    svg.append("g")
        .attr("class", "y axis")
        .style("fill", "steelblue")
        .call(yAxis1);

    svg.append("g")
        .attr("class", "y axis")
        .attr("transform", "translate(" + width + ", 0)")
        .style("fill", "red")
        .call(yAxis2);
    
    svg.append("path")
        .datum(data1)
        .attr("class", "line")
        .attr("d", line1);

    svg.append("path")
        .datum(data2)
        .style("stroke", "red")
        .attr("class", "line")
        .attr("d", line2);

    svg.append("text")
        .attr("text-anchor", "middle")
        .attr("transform", "translate("+ - (margin.left / 2) +","+ (height / 2) +")rotate(-90)")
        .style("font-size", "16px")
        .text(ticker1);

    svg.append("text")
        .attr("text-anchor", "middle")
        .attr("transform", "translate("+ (width + (margin.left / 2)) +","+ (height / 2) +")rotate(-270)")
        .style("font-size", "16px")
        .text(ticker2);

  });
});

function type(d) {
  d.Date = parseDate(d.Date);
  d.Close = +d.Close;
  d.equals = function() {
    return true;
  };
  return d;
}
}

