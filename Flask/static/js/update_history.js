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
                        async: true,
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
                        async: true,
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
                        async: true,
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
                        async: true,
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
                        async: true,
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
                    var graphChart = echarts.init(document.getElementById('line_graph'));
            
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
                                    sta.symbolSize = Math.log(in_hour_flow[sta_name][`${i}`]) * 10 + 10;
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
                                roam:false,
                                label: {
                                    show: false, 
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
            
                    graphChart.setOption(option);
                    
                    var splitChart = echarts.init(document.getElementById('split_bar'));
                    var splitFlow;
                    $.ajax({
                        type: 'POST',
                        url: '/split_flow/2',
                        async: false,
                        data: value,
                        datatype: 'json',
                        success: function (result) {
                            splitFlow = result;
                        }
                    });
                    
                    var uplineFlow = [];
                    var downlineFlow = [];
                    splitNames = Object.keys(splitFlow);
                    for (let index = 0; index < splitNames.length; index++){
                        let split = splitFlow[splitNames[index]];
                        uplineFlow.push(split.up);
                        downlineFlow.push(split.down);
                    }
    
                    option = {
                        title: {
                            text: '地铁线路断面客流',
                            left:"center",
                            subtext: '2号线',
                            textStyle:{
                                color:"#000"
                            }
                        },
                        color:['#9E87FF', '#73ACFF'],
                        tooltip: {
                            trigger: 'axis',
                            axisPointer: {
                                type: 'shadow'
                            },
                        },
                        legend: {
                            left:"right",
                            data: ['上行','下行'],
                            textStyle:{fontSize:16}
                        },
                        toolbox: {
                            show: false
                        },
                        grid: [{bottom:"50%"},{top:'50%'}],
                        xAxis: [
                            {
                                type: 'category',
                                show:true,
                                axisLine: {show: true, onZero: false},
                                axisTick: {show: false},
                                axisLabel: {show: false,color:"grey",fontSize:20},
                                splitArea: {show: false},
                                splitLine: {show: false},
                                position:"bottom",
                                nameTextStyle:{fontSize:16},
                                data: splitNames
                            },
                            {
                                type: 'category',
                                show:true,
                                axisLine: {show: false, onZero: false},
                                axisTick: {show: false},
                                axisLabel: {show: false,color:"grey",fontSize:16},
                                splitArea: {show: false},
                                splitLine: {show: false},
                                gridIndex:1,
                                position:"bottom",
                                nameTextStyle: { fontSize: 16 },
                                data: splitNames
                            }
                        ],
                        yAxis: [
                            {
                                type: 'value',
                                name: "上行客流 /人次",
                                position:"left",
                                splitLine: true,
                                splitNumber:5,
                                gridIndex:0,
                                axisLabel: {
                                    color: '#949AA8',
                                },
                            },
                            {
                                type: 'value',
                                name:"下行客流 /人次",
                                position:"left",
                                splitLine: true,
                                splitNumber:5,
                                gridIndex:1,
                                inverse:true, 
                                axisLabel: {
                                    color: '#949AA8',
                                },
                            }
                        ],
                        series: [
                            {
                                type:"bar",
                                name:"上行",
                                barMaxWidth:40,
                                data: uplineFlow,
                                xAxisIndex: 0,
                                yAxisIndex: 0,
                                itemStyle: {
                                    color: '#9E87FF',
                                    barBorderRadius: [4, 4, 0, 0]
                                },
                            },
                            {
                                type:"bar",
                                name:"下行",
                                barMaxWidth:40,
                                data:downlineFlow,
                                xAxisIndex: 1,
                                yAxisIndex: 1,
                                itemStyle: {
                                    color: '#73ACFF',
                                    barBorderRadius: [0, 0, 4, 4]
                                },
                                
                            }
                        ]
                    };

                    splitChart.setOption(option);
                    
                    // var ODChart = echarts.init(document.getElementById('od_graph'));
                    // var ODFlow;
                    // $.ajax({
                    //     type: 'POST',
                    //     url: '/od_flow',
                    //     async: false,
                    //     data: value,
                    //     dataType: 'json',
                    //     success: function (result) {
                    //         ODFlow = result;
                    //         console.log(ODFlow);
                    //     }
                    // });

                    // var stationNames = Object.keys(ODFlow);

                    // var staColor = {
                    //     '1号线': '#73DDFF',
                    //     '2号线': '#73ACFF',
                    //     '3号线': '#FDD56A',
                    //     '4号线': '#FDB36A',
                    //     '5号线': '#FD866A',
                    //     '10号线': '#9E87FF',
                    //     '11号线': '#58D5FF',
                    //     '12号线': '#E271DE'
                    // }

                    // var links = [];
                    // for (let source in ODFlow) {
                        
                    //     let targetDict = ODFlow[source][1];
                    //     for (let target in targetDict) {
                    //         links.push({
                    //             'source': source,
                    //             'target': target,
                    //             'value': targetDict[target][1]
                    //         });
                    //     }
                    // }
                    
                    // var stations = [];
                    // stationNames.forEach(function (station) {
                    //     stations.push({
                    //         'name': station,
                    //         'symbolSize': 2,
                    //         'color': staColor[ODFlow[station][0]]
                    //     });
                    // })
                    
                    // option = {
                    //     animationDurationUpdate: 1500,
                    //     animationEasingUpdate: 'quinticInOut',
                    //     series: [{
                    //         name: "relation",
                    //         type: 'graph',
                    //         layout: 'circular',
                    //         circular: {
                    //             rotateLabel: true
                    //         },
                    //         data: stations,
                    //         links: links,
                    //         roam: true,
                    //         label: {
                    //             show: true,
                    //             position: 'right',
                    //             formatter: '{b}',
                    //             interval: 0
                    //         },
                    //         emphasis: {
                    //             lineStyle: {
                    //                 width: "3"
                    //             }
                    //         },
                    //         focusNodeAdjacency: true,
                    //         lineStyle: {
                    //             color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                    //                     offset: 0,
                    //                     color: '#4e8ebf'
                    //                 },
                    //                 {
                    //                     offset: 0.45,
                    //                     color: '#9ac8e0'
                    //                 },
                    //                 {
                    //                     offset: 0.65,
                    //                     color: '#ba3036'
                    //                 },
                    //                 {
                    //                     offset: 1,
                    //                     color: '#c84641'
                    //                 }
                    //             ]),
                    //             curveness: 0.3
                    //         }
                    //     }]
                    // };

                    // ODChart.setOption(option);
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
                async: true,
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
                async: true,
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
                async: true,
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
                async: true,
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
                async: true,
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
        
            var stations = getJsonData('sta/json');
            var links = getJsonData('link/json');
        
            //初始化图表
            var graphChart = echarts.init(document.getElementById('line_graph'));
        
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
                            sta.symbolSize = Math.log(in_hour_flow[sta_name][`${i}`]) * 10 + 10;
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
                        roam:false,
                        label: {
                            show: false,
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
        
            graphChart.setOption(option);

            var splitChart = echarts.init(document.getElementById('split_bar'));
            var splitFlow;
            $.ajax({
                type: 'POST',
                url: '/split_flow/2',
                async: false,
                data: value,
                datatype: 'json',
                success: function (result) {
                    splitFlow = result;
                }
            });
            
            var uplineFlow = [];
            var downlineFlow = [];
            splitNames = Object.keys(splitFlow);
            for (let index = 0; index < splitNames.length; index++){
                let split = splitFlow[splitNames[index]];
                uplineFlow.push(split.up);
                downlineFlow.push(split.down);
            }

            option = {
                title: {
                    text: '地铁线路断面客流',
                    left:"center",
                    subtext: '2号线',
                    textStyle:{
                        color:"#000"
                    }
                },
                color:['#9E87FF', '#73ACFF'],
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'shadow'
                    },
                },
                legend: {
                    left:"right",
                    data: ['上行','下行'],
                    textStyle:{fontSize:16}
                },
                toolbox: {
                    show: false
                },
                grid: [{bottom:"50%"},{top:'50%'}],
                xAxis: [
                    {
                        type: 'category',
                        show:true,
                        axisLine: {show: true, onZero: false},
                        axisTick: {show: false},
                        axisLabel: {show: false,color:"grey",fontSize:20},
                        splitArea: {show: false},
                        splitLine: {show: false},
                        position:"bottom",
                        nameTextStyle:{fontSize:16},
                        data: splitNames
                    },
                    {
                        type: 'category',
                        show:true,
                        axisLine: {show: false, onZero: false},
                        axisTick: {show: false},
                        axisLabel: {show: false,color:"grey",fontSize:16},
                        splitArea: {show: false},
                        splitLine: {show: false},
                        gridIndex:1,
                        position:"bottom",
                        nameTextStyle: { fontSize: 16 },
                        data: splitNames
                    }
                ],
                yAxis: [
                    {
                        type: 'value',
                        name: "上行客流 /人次",
                        position:"left",
                        splitLine: true,
                        splitNumber:5,
                        gridIndex:0,
                        axisLabel: {
                            color: '#949AA8',
                        },
                    },
                    {
                        type: 'value',
                        name:"下行客流 /人次",
                        position:"left",
                        splitLine: true,
                        splitNumber:5,
                        gridIndex:1,
                        inverse:true, 
                        axisLabel: {
                            color: '#949AA8',
                        },
                    }
                ],
                series: [
                    {
                        type:"bar",
                        name:"上行",
                        barMaxWidth:40,
                        data: uplineFlow,
                        xAxisIndex: 0,
                        yAxisIndex: 0,
                        itemStyle: {
                            color: '#9E87FF',
                            barBorderRadius: [4, 4, 0, 0]
                        },
                    },
                    {
                        type:"bar",
                        name:"下行",
                        barMaxWidth:40,
                        data:downlineFlow,
                        xAxisIndex: 1,
                        yAxisIndex: 1,
                        itemStyle: {
                            color: '#73ACFF',
                            barBorderRadius: [0, 0, 4, 4]
                        },
                        
                    }
                ]
            };
            
            splitChart.setOption(option);

        }
    });
})


