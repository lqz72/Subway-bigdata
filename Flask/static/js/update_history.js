var d = new DateJs({
    inputEl: '#inputdate',
    el: '#date'
})
console.log(d);
console.log(d.choiceDate.date);


//初始化代码写这儿
$(
    function(){
        var month_chart = echarts.init(document.getElementById('month_line'), 'white', {renderer: 'canvas'});
        $.ajax({
            type: 'POST',
            data: d.choiceDate.date,
            async: false,
            url: 'history/day_flow/line',
            dataType: 'json',
            success: function (result) {
                month_chart.setOption(result);
            }
        });

        var week_chart = echarts.init(document.getElementById('curr_week_line'), 'white', {renderer: 'canvas'});
        $.ajax({
            type: "POST",
            data: d.choiceDate.date,
            async : false,
            url: "/history/curr_week_flow/line",
            dataType: 'json',
            success: function (result) {
                week_chart.setOption(result);
            }
        });

        var weather_info = document.getElementById('weather');
        var is_hoilday = document.getElementById('is_hoilday');
        var day_flow = document.getElementById('day_flow');
        $.ajax({
            type: 'POST',
            data: d.choiceDate.date,
            async: false,
            url: '/thisday_info',
            dataType: 'json',
            success: function (result) {
                console.log(result);
                weather_info.innerHTML = result.weather;
                is_hoilday.innerHTML = result.is_hoilday;
                day_flow.innerHTML = result.day_flow;
            }
        });

        $.ajax({
            type: 'POST',
            data: d.choiceDate.date,
            async: false,
            url: '/sta_rank',
            dataType: 'json',
            success: function (result) {
                console.log(result);
                for (let i = 1; i <= 10; i++){

                    var rank = document.getElementById(i+"");
                    var sta_name = document.getElementById('Sta' + i+"");
                    var line = document.getElementById('line' + i+"");
                    var flow = document.getElementById('flow' + i+"");
    
                    rank.innerHTML = i;
                    sta_name.innerHTML = result[i-1][0];
                    line.innerHTML = result[i-1][1];
                    flow.innerHTML = result[i-1][2];
                }
            }
        });

        var line_pie = echarts.init(document.getElementById('line_percent'));
        $.ajax({
            type: "POST",
            data: d.choiceDate.date,
            async : false,
            url: "/history/line/pie",
            dataType: 'json',
            success: function (result) {
                line_pie.setOption(result);
            }
        });

        function get_data(url){
            var js_data;
            $.ajax({
                    url: url,
                    type: "GET",
                    dataType: "json", 
                    async: false,  //请求方式 设置为异步
                    success: function(data) {
                        js_data = data
                    }
                })
            return js_data;
        }

        var stations = get_data('http://127.0.0.1:5000/sta/json');
        var links = get_data('http://127.0.0.1:5000/link/json');
        
        console.log(stations)
        //初始化图表
        var myChart = echarts.init(document.getElementById('line_graph'));

        //获取线路名称列表
        var lineNames = []
        for (let index = 0; index < stations.length - 1; index++) {
            if (lineNames.indexOf(stations[index].category) == -1) {
                lineNames.push(stations[index].category)
            }
        }

        //图例的数据数组 数组中的每一项代表一个系列的name
        var legend = [{data: lineNames }]

        //获取类目名称数组 用于和 legend 对应以及格式化 tooltip 的内容
        var categories = lineNames.map(lineName => {return {name: lineName}})

        //随机数函数 后期修改为真实数据
        var rdm = function(min, max){
            return Math.floor(Math.random() * (max - min)) + min;
        }

        // 组装模拟数据
        var stations_lq = [];
        var stations_len = stations.length;
        
        let lq_tmp = {};
        lq_tmp.lq = [];
        stations.forEach(function(v){
            vt = JSON.parse(JSON.stringify(v));
            vt.value = rdm(60,200);
            vt.itemStyle.color = v.itemStyle.borderColor;
            vt.itemStyle.borderWidth = 0;
            vt.itemStyle.opacity = 0.75;
            lq_tmp.lq.push(vt);
        });
        stations_lq.push(lq_tmp); 
        
        function timelist() {
            var timelist = []
            for(let i = 1; i <= 24; i++){
                timelist.push(`${i}:00`)
            }
            return timelist
        }

        myChart.on('click', function (params) {
            console.log(params);
        });

        option = {
            timeline: {
                axisType: 'category',
                show: true,
                autoPlay: true,
                playInterval: 1000,
                data: timelist()
            },
            title: {
                text: '早晚高峰客流'
            },
            backgroundColor:'#fff',
            color: ['#EE1822', '#85C73F', '#FDD303', '#4E2C8D', '#8F57A2', '#D7156B', '#F26F1F', '#009DD7', '#67CCF6', '#B8A8CF', '#7C1F31', '#54ae11', '#E77DAD', '#78d6cd', '#bc796f'],
            grid:[
                {left:0, top:0, width:'100%', height: '100%'} // 放主图
            ],
            xAxis:[
                {gridIndex: 0, show:false},
            ],
            yAxis:[
                {gridIndex: 0, show:false},
            ],
            tooltip: {},
            legend: legend,
            animationDurationUpdate: 1500,
            animationEasingUpdate: 'quinticInOut',
            series: [
                // 用关系图实现地铁地图
                {
                    type: 'graph',
                    layout: 'none',
                    xAxis:1,
                    yAxis:1,
                    symbolSize: 3,
                    roam: true,
                    label: {
                            show: false,
                            rotate: '30', 
                            color: 'black',
                            position: 'right'
                    },
                    focusNodeAdjacency: true,
                    edgeSymbol: ['none', 'none'],
                    edgeSymbolSize: [4, 6],
                    edgeLabel: {
                        normal: {
                            textStyle: {
                                fontSize: 20
                            }
                        }
                    },
                    data: stations,
                    links: links,
                    categories: categories,
                    lineStyle: {
                        normal: {
                            opacity: 0.9,
                            width: 5,
                            curveness: 0
                        }
                    }
                },
                // 在同样的关系图坐标上，展示数据大小。
                {
                    type: 'graph',
                    xAxis:1,
                    yAxis:1,
                    roam:true,
                    symbolSize: function (params) {
                        return params/10;
                    },
                    symbol:'circle',
                    data: stations_lq[0]['lq']
                },
            
            ]
        }
        myChart.setOption(option);

    },

)


var bt = document.querySelectorAll('.bts>.bt')[1];
console.log(bt);
bt.addEventListener('click',function(){

    console.log(d.choiceDate);
    console.log((d.choiceDate.date));
    console.log(JSON.stringify(d.choiceDate.date))

    var month_chart = echarts.init(document.getElementById('month_line'), 'white', {renderer: 'canvas'});
    $.ajax({
        type: 'POST',
        data: d.choiceDate.date,
        async: false,
        url: 'history/day_flow/line',
        dataType: 'json',
        success: function (result) {
            month_chart.setOption(result);
        }
    });

    var week_chart = echarts.init(document.getElementById('curr_week_line'), 'white', {renderer: 'canvas'});
    $.ajax({
        type: "POST",
        data: d.choiceDate.date,
        async : false,
        url: "/history/curr_week_flow/line",
        dataType: 'json',
        success: function (result) {
            week_chart.setOption(result);
        }
    });
    
    var weather_info = document.getElementById('weather');
    var is_hoilday = document.getElementById('is_hoilday');
    var day_flow = document.getElementById('day_flow');
    $.ajax({
        type: 'POST',
        data: d.choiceDate.date ,
        async: false,
        url: '/thisday_info',
        dataType: 'json',
        success: function (result) {
            console.log(result);
            weather_info.innerHTML = result.weather;
            is_hoilday.innerHTML = result.is_hoilday;
            day_flow.innerHTML = result.day_flow;
        }
    });

    $.ajax({
        type: 'POST',
        data: d.choiceDate.date,
        async: false,
        url: '/sta_rank',
        dataType: 'json',
        success: function (result) {
            console.log(result);
            for (let i = 1; i <= 10; i++){
                
                var rank = document.getElementById(i+"");
                var sta_name = document.getElementById('Sta' + i+"");
                var line = document.getElementById('line' + i+"");
                var flow = document.getElementById('flow' + i+"");
                 
                rank.innerHTML = i;
                sta_name.innerHTML = result[i-1][0];
                line.innerHTML = result[i-1][1];
                flow.innerHTML = result[i-1][2];
            }
        }
    });

    var line_pie = echarts.init(document.getElementById('line_percent'));
    $.ajax({
        type: "POST",
        data: d.choiceDate.date,
        async : false,
        url: "/history/line/pie",
        dataType: 'json',
        success: function (result) {
            line_pie.setOption(result);
        }
    });
  
});