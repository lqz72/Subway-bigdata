layui.use('laydate', function(){
    var laydate = layui.laydate;
    
    //执行一个laydate实例
    laydate.render({
      elem: '#timectrl'
      ,position: 'static'
      ,value: '2020-01-01'
      ,showBottom: false
      ,min: '2019-12-26'
      ,max: '2020-07-16'
      ,ready: function(date){//初始化
        console.log(date); //得到初始的日期时间对象：{year: 2017, month: 8, date: 18, hours: 0, minutes: 0, seconds: 0}
        $(
            function(){
                value = '2020-01-01';
                var month_chart = echarts.init(document.getElementById('month_line'), 'white', {renderer: 'canvas'});
                console.log(value);
                $.ajax({
                    type: 'POST',
                    data: value,
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
                    data: value,
                    async: false,
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
                    data: value,
               
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
                    data: value,
                    async: false,
                    url: '/sta_rank',
                    dataType: 'json',
                    success: function (result) {
                        console.log(result);
                        for (let i = 1; i <= 25; i++){
        
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
                    data: value,
                    async: false,
                    url: "/history/line/pie",
                    dataType: 'json',
                    success: function (result) {
                        line_pie.setOption(result);
                    }
                });
        
                var in_hour_flow;
                var out_hour_flow;
                $.ajax({
                    type: "POST",
                    data: value,
                    url: "/in_hour_flow",
                    dataType: 'json',
                    async: false,
                    success: function (result) {
                        in_hour_flow = result;
                    }
                });
                
                // $.ajax({
                //     type: "POST",
                //     data: value,
                //     url: "/out_hour_flow",
                //     dataType: 'json',
                //     async: false,
                //     success: function (result) {
                //         out_hour_flow = result;
                //     }
                // });
        
                function getJsonData(url){
                    var js_data;
                    $.ajax({
                            url: url,
                            type: "GET",
                            data: value,
                            dataType: "json", 
                            async: false,
                            success: function(data) {
                                js_data = data;
                            }
                        })
                    return js_data;
                }
        
                var stations = getJsonData('/sta/json');
                var links = getJsonData('/link/json');
        
                //初始化图表
                var myChart = echarts.init(document.getElementById('line_graph'));
        
                //获取线路名称列表
                var lineNames = [];
                for (let index = 0; index < stations.length - 1; index++) {
                    if (lineNames.indexOf(stations[index].category) == -1) {
                        lineNames.push(stations[index].category);
                    }
                }
        
                //图例的数据数组 数组中的每一项代表一个系列的name
                var legend = [{ data: lineNames, top: "5%" }];
        
                //获取类目名称数组 用于和 legend 对应以及格式化 tooltip 的内容
                var categories = lineNames.map(lineName => { return { name: lineName } });
                
                function timelist() {
                    var timelist = [];
                    for(let i = 6; i <= 21; i++){
                        timelist.push(`${i}:00`);
                    }
                    return timelist;
                }
        
                //生成6-21点的客流数据
                var stations_lq = [];
                for (let i = 6; i <= 21; i++) {
                    let lq_tmp = {};
                    lq_tmp.lq = [];
                    stations.forEach(function (station) {
                        var sta_name = station.name;
        
                        var sta = JSON.parse(JSON.stringify(station));
                        
                        if (in_hour_flow[sta_name]) {
                            sta.value = in_hour_flow[sta_name][`${i}`];
                            if (sta.value == 0) 
                                sta.symbolSize = 10;  //如果客流量为0 设置最小size为10
                            else 
                                //否则取对数降低增长速度
                                sta.symbolSize = Math.log(in_hour_flow[sta_name][`${i}`]) * 5 + 10;
                        } else {
                            sta.value = 0;
                            sta.symbolSize = 10;
                        }
                        
                        sta.itemStyle.color = station.itemStyle.borderColor;
                        sta.itemStyle.borderWidth = 0;
                        sta.itemStyle.opacity = 0.75;
        
                        lq_tmp.lq.push(sta);
                    });
                    stations_lq.push(lq_tmp);
                }
                
            
                option = {
                    timeline: {
                        axisType: 'category',
                        show: true,
                        autoPlay: false,
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
                        {gridIndex: 0, show:false, type: 'value'},
                    ],
                    yAxis:[
                        {gridIndex: 0, show:false, type: 'value'},
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
                            xAxis:0,
                            yAxis:0,
                            symbolSize: 3,
                            roam:true,
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
                            // data: stations_lq[0]['lq'],
                            // links: links,
                            categories: categories,
                            lineStyle: {
                                normal: {
                                    opacity: 0.9,
                                    width: 5,
                                    curveness: 0
                                }
                            }
                        },

                    ],
                    options: []
                }
              
                for (let i = 0; i <= 15; i++){
                    option.options.push({
                        title: {
                            text: '轨道交通进站客流分布 ' + timelist()[i]
                        },
                        series: [{
                            data: stations_lq[i]['lq'],
                            links: links,
                        }]
                    })
                }
        
                myChart.setOption(option);
                
            }
        )

      }
      ,change: function(value, date){ //改变日期后
        //   console.log(value); //得到日期生成的值，如：2017-08-18
        //   // console.log(date); //得到日期时间对象：{year: 2017, month: 8, date: 18, hours: 0, minutes: 0, seconds: 0}
        //   var bt = document.querySelectorAll('.bts>.bt')[1];
        //   bt.addEventListener('click',function(){
            console.log(value);
        
            var month_chart = echarts.init(document.getElementById('month_line'), 'white', {renderer: 'canvas'});
            $.ajax({
                type: 'POST',
                data: value,
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
                data: value,
                async: false,
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
                data: value ,
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
                data: value,
                async: false,
                url: '/sta_rank',
                dataType: 'json',
                success: function (result) {
                    console.log(result);
                    for (let i = 1; i <= 25; i++){
                        
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
                data: value,
            
                url: "/history/line/pie",
                dataType: 'json',
                success: function (result) {
                    line_pie.setOption(result);
                }
            });
        
            var in_hour_flow;
            var out_hour_flow;
            $.ajax({
                type: "POST",
                data: value,
                url: "/in_hour_flow",
                dataType: 'json',
                async: false,
                success: function (result) {
                    in_hour_flow = result;
                    console.log(in_hour_flow);
                }
            });
            
            // $.ajax({
            //     type: "POST",
            //     data: value,
            //     url: "/out_hour_flow",
            //     dataType: 'json',
            //     async: false,
            //     success: function (result) {
            //         out_hour_flow = result;
            //     }
            // });
        
        
            function getJsonData(url){
                var js_data;
                $.ajax({
                        url: url,
                        type: "GET",
                        data: value,
                        dataType: "json", 
                        async: false,
                        success: function(data) {
                            js_data = data;
                        }
                    })
                return js_data;
            }
        
            var stations = getJsonData('sta/json');
            var links = getJsonData('link/json');
        
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
            var legend = [{data: lineNames , top:"5%"}]
        
            //获取类目名称数组 用于和 legend 对应以及格式化 tooltip 的内容
            var categories = lineNames.map(lineName => {return {name: lineName}})
            
            function timelist() {
                var timelist = []
                for(let i = 6; i <= 21; i++){
                    timelist.push(`${i}:00`)
                }
                return timelist
            }
        
            //生成6-21点的客流数据
            var stations_lq = [];
            for (let i = 6; i <= 21; i++) {
                let lq_tmp = {};
                lq_tmp.lq = [];
                stations.forEach(function (station) {
                    var sta_name = station.name;
        
                    var sta = JSON.parse(JSON.stringify(station));
                    
                    if (in_hour_flow[sta_name]) {
                        sta.value = in_hour_flow[sta_name][`${i}`];
                        if (sta.value == 0) 
                            sta.symbolSize = 10;  //如果客流量为0 设置最小size为10
                        else 
                            //否则取对数降低增长速度
                            sta.symbolSize = Math.log(in_hour_flow[sta_name][`${i}`]) * 5 + 10;
                    } else {
                        sta.value = 0;
                        sta.symbolSize = 10;
                    }
                    
                    // sta.name = sta_name;
                    sta.itemStyle.color = station.itemStyle.borderColor;
                    sta.itemStyle.borderWidth = 0;
                    sta.itemStyle.opacity = 0.75;
        
                    lq_tmp.lq.push(sta);
                });
                stations_lq.push(lq_tmp);
            }
            
        
            option = {
                timeline: {
                    axisType: 'category',
                    show: true,
                    autoPlay: false,
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
                    {gridIndex: 0, show:false, type: 'value'},
                ],
                yAxis:[
                    {gridIndex: 0, show:false, type: 'value'},
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
                        xAxis:0,
                        yAxis:0,
                        symbolSize: 3,
                        roam:true,
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
                        categories: categories,
                        lineStyle: {
                            normal: {
                                opacity: 0.9,
                                width: 5,
                                curveness: 0
                            }
                        }
                    },
                
                ],
                options: []
            }
        
            for (let i = 0; i <= 15; i++){
                option.options.push({
                    title: {
                        text: '轨道交通进站客流分布 ' + timelist()[i]
                    },
                    series: [{
                        data: stations_lq[i]['lq'],
                        links: links,
                    }]
                })
            }
        
            myChart.setOption(option);
          
        }
    });
})


