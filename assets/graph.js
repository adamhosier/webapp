MAX_CANDLESTICKS = 100;

function loadGraph(ticker) {
    var margin = {top: 20, right: 20, bottom: 30, left: 50},
            width = 800 - margin.left - margin.right,
            height = 400 - margin.top - margin.bottom;

    //var parseDate = d3.time.format("%d-%b-%y").parse;
    var parseDate = d3.time.format("%Y-%m-%d %H:%M").parse;

    var x = techan.scale.financetime()
            .range([0, width]);

    var y = d3.scale.linear()
            .range([height, 0]);

    var candlestick = techan.plot.candlestick()
            .xScale(x)
            .yScale(y);

    var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom");

    var yAxis = d3.svg.axis()
            .scale(y)
            .orient("left");

    var svg = d3.select("#graph-body").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    d3.csv("assets/data/" + ticker + ".csv", function(error, dataorig) {
        data = []
        $.each(dataorig, function(i, el) {
          if(data.length == 0 || data[data.length -1].Close != el.Close) data.push(el);
        });
        data = data.slice(data.length - MAX_CANDLESTICKS, data.length);
        var accessor = candlestick.accessor(),
            timestart = Date.now();

        data = data.slice(0, 200).map(function(d) {
            return {
                date: parseDate(d.Date),
                open: +d.Open,
                high: +d.High,
                low: +d.Low,
                close: +d.Close,
                volume: +d.Volume
            };
        }).sort(function(a, b) { return d3.ascending(accessor.d(a), accessor.d(b)); });

        x.domain(data.map(accessor.d));
        y.domain(techan.scale.plot.ohlc(data, accessor).domain());

        svg.append("g")
                .datum(data)
                .attr("class", "candlestick")
                .call(candlestick);

        svg.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + height + ")")
                .call(xAxis);

        svg.append("g")
                .attr("class", "y axis")
                .call(yAxis)
                .append("text")
                .attr("transform", "rotate(-90)")
                .attr("y", 6)
                .attr("dy", ".71em")
                .style("text-anchor", "end")
                .text("Price ($)");
    });
}
