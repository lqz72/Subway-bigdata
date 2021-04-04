// layui.use('form', function(){
//     var form = layui.form;
    
//     //各种基于事件的操作，下面会有进一步介绍
     
//     form.on('radio', function(data){
//         console.log(data.value); //被点击的radio的value值
//         console.log(n_date);
//         //切换 上行、下行 0表示上行 代码写这儿
        
//     }); 

//     form.on('select', function(data){
//         console.log(data.value); //得到被选中的值
//         console.log(n_date);
//         //切换线路代码写这儿

//     }); 
// });


var n_date;
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
            n_date = '2020-01-01';
            //console.log(date); //得到初始的日期时间对象：{year: 2017, month: 8, date: 18, hours: 0, minutes: 0, seconds: 0}
            $(
                function(){
                    value = '2020-01-01';
                    var month_chart = echarts.init(document.getElementById('month_line'), 'white', {renderer: 'canvas'});
                    // console.log(value);
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
                            // console.log(result);
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
            
                    var hourFlow;
                    $.ajax({
                        type: "POST",
                        data: value,
                        url: '/out_hour_flow',
                        dataType: 'json',
                        async: false,
                        success: function (result) {
                            hourFlow = result;
                        }
                    });
            
                    function getJsonData(url){
                        var jsData;
                        $.ajax({
                                url: url,
                                type: "GET",
                                data: value,
                                dataType: "json", 
                                async: false,
                                success: function(data) {
                                    jsData = data;
                                }
                            })
                        return jsData;
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
                    function getHourFlowData(hourFlow, stations) {
                        var hourFlowList = [];
                        for (let i = 6; i <= 21; i++) {
                            var hour = {};
                            hour.staList = [];
                            stations.forEach(function (station) {
                                var staName = station.name;
                
                                var sta = JSON.parse(JSON.stringify(station));
                                
                                if (hourFlow[staName]) {
                                    sta.value = hourFlow[staName][`${i}`];
                                    if (sta.value == 0) 
                                        sta.symbolSize = 10;  //如果客流量为0 设置最小size为10
                                    else 
                                        //否则取对数降低增长速度
                                        sta.symbolSize = Math.log(hourFlow[staName][`${i}`]) * 10 + 10;
                                } else {
                                    sta.value = 0;
                                    sta.symbolSize = 10;
                                }
                                
                                sta.itemStyle.color = station.itemStyle.borderColor;
                                sta.itemStyle.borderWidth = 0;
                                sta.itemStyle.opacity = 0.75;
                
                                hour.staList.push(sta);
                            });
                            hourFlowList.push(hour);
                        }
                        return hourFlowList;
                    }
                    
                    //配置图表属性
                    function setGraphOptions(option, hourFlowData, type = "出站") {
                        option.options = [];
                        for (let i = 0; i <= 15; i++){ 
                            option.options.push({
                                title: {
                                    text: '轨道交通' + type + '客流分布 ' + timelist()[i]
                                },
                                series: [{
                                    data: hourFlowData[i].staList,
                                    links: links,
                                }]
                            })
                            
                        }
                    }

                    var graphOption = {
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
                    
                    var hourFlowData = getHourFlowData(hourFlow, stations);
                    setGraphOptions(graphOption, hourFlowData);
                    graphChart.setOption(graphOption);
                    
                    var splitChart = echarts.init(document.getElementById('split_bar'));
                    var splitFlow;
                    $.ajax({
                        type: 'POST',
                        url: '/split_flow/1',
                        async: false,
                        data: value,
                        datatype: 'json',
                        success: function (result) {
                            splitFlow = result;
                        }
                    });
                    
                    var uplineFlow = downlineFlow = [];
                    var splitNames = Object.keys(splitFlow);
                    for (let index = 0; index < splitNames.length; index++){
                        var split = splitFlow[splitNames[index]];
                        uplineFlow.push(split.up);
                        downlineFlow.push(split.down);
                    }
                                  
                    function setBarOption(option, y1, y2, x, line) {
                        option.title.subtext = line + '号线';
                        option.xAxis[0].data = x;
                        option.xAxis[1].data = x;
                        option.series[0].data = y1;
                        option.series[1].data = y2;
                    }

                    var barOption = {
                        title: {
                            text: '地铁线路断面客流',
                            left:"center",
                            subtext: '1号线',
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

                    setBarOption(barOption, uplineFlow, downlineFlow, splitNames);
                    splitChart.setOption(barOption);

                    //断面排行榜
                    var splitRank = [];
                    function getSplitRank(splitRank, line) {
                        for (let i = 0; i < splitNames.length - 1; i++){
                            var k = i;
                            var maxFlow = splitFlow[splitNames[i]].up;
                            for (let j = i + 1; j < splitNames.length; j++){
                                if (splitFlow[splitNames[j]].up > maxFlow) {
                                    k = j;
                                    maxFlow = splitFlow[splitNames[j]].up;
                                }
                            }
                            splitRank.push({ 'split': splitNames[k], 'flow': maxFlow });
                            delete splitFlow[splitNames[k]];
                            splitNames = Object.keys(splitFlow);
                        }
                        
         
                        for (let i = 1; i <= 6; i++){
                            var split_rank = document.getElementById('split_rank' + `${i}`);
                            var source = document.getElementById('source' + `${i}`);
                            var target = document.getElementById('target' + `${i}`);
                            var split_line = document.getElementById('split_line' + `${i}`);
                            var split_flow = document.getElementById('split_flow' + `${i}`);
    
                            split_rank.innerHTML = i;
                            source.innerHTML = splitRank[i - 1]['split'].split('-')[0];
                            target.innerHTML = splitRank[i - 1]['split'].split('-')[1];
                            split_line.innerHTML = line + '号线';
                            split_flow.innerHTML = splitRank[i - 1]['flow'];
                        }
                    }
                    
                    getSplitRank(splitRank, '1');

                    //od关系图
                    var ODChart = echarts.init(document.getElementById('od_graph'));
                    var ODFlow;
                    $.ajax({
                        type: 'POST',
                        url: '/od_flow',
                        async: false,
                        data: value,
                        dataType: 'json',
                        success: function (result) {
                            ODFlow = result;
                        }
                    });

                    function compare(name)
                    {
                        return function(a,b){
                            var sta1 = a[name];
                            var sta2 = b[name];
                            var line1 = parseInt(ODFlow[sta1][0].split('号')[0]);
                            var line2 =parseInt(ODFlow[sta2][0].split('号')[0]);
                            
                            return line1-line2;
                        }
                    }

                    var staColor = {
                        '1号线': '#73DDFF',
                        '2号线': '#73ACFF',
                        '3号线': '#FDD56A',
                        '4号线': '#FDB36A',
                        '5号线': '#FD866A',
                        '10号线': '#9E87FF',
                        '11号线': '#58D5FF',
                        '12号线': '#E271DE'
                    }

                    var ODLinks = [];
                    var ODstations = [];
                    var stationNames = Object.keys(ODFlow);

                    function getODFlowData(ODLinks, ODstations, stationNames) {
                        for (let i = 0; i < (stationNames.length / 2); i++){
                            let source = stationNames[i];
    
                            let targetDict = ODFlow[source][1];
                            let targetList = Object.keys(targetDict);
                            for (let j = 0; j < (targetList.length / 2); j++) {
                                let target = targetList[j];
                                if (targetDict[target][1] != 0) {
                                    ODLinks.push({
                                        'source': source,
                                        'target': target,
                                        'value': targetDict[target][1]
                                    });
                                }
                            }
    
                            ODstations.push({
                                name: source,
                                symbolSize: 6,
                                itemStyle: {
                                    color: staColor[ODFlow[source][0]]
                                },
                                category: ODFlow[source][0]
                            });
                        }
                        ODstations = ODstations.sort(compare('name'));
                    }

                    function setODOption(ODOption, ODstations, ODLinks) {
                        ODOption.series.data = ODstations;
                        ODOption.series.links = ODLinks;
                        return ODOption;
                    }

                    var ODOption = {
                        title: {
                            text: '地铁站点OD关系图',
                            left:"center",
                            textStyle:{
                                color:"#000"
                            }
                        },
                        legend: [{ data: lineNames, orient: 'vertical', right: '2%' }],
                        tooltip: {trigger:'item'},
                        animationDurationUpdate: 1500,
                        animationEasingUpdate: 'quinticInOut',
                        series: [{
                            name: "relation",
                            type: 'graph',
                            layout: 'circular',
                            circular: {
                                rotateLabel: true
                            },
                            data: ODstations,
                            links: ODLinks,
                            roam: true,
                            label: {
                                show: false,
                                position: 'right',
                                formatter: '{b}',
                                interval: 0
                            },
                            categories:categories,
                            emphasis: {
                                lineStyle: {
                                    width: "3"
                                }
                            },
                            focusNodeAdjacency: true,
                            lineStyle: {
                                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                                        offset: 0,
                                        color: '#4e8ebf'
                                    },
                                    {
                                        offset: 0.45,
                                        color: '#9ac8e0'
                                    },
                                    {
                                        offset: 0.65,
                                        color: '#ba3036'
                                    },
                                    {
                                        offset: 1,
                                        color: '#c84641'
                                    }
                                ]),
                                curveness: 0.3
                            }
                        }]
                    };
                    
                    getODFlowData(ODLinks, ODstations, stationNames);
                    setODOption(ODOption, ODstations, ODLinks);
                    ODChart.setOption(ODOption);

                    //响应控件事件
                    layui.use('form', function(){
                        var form = layui.form;
                        
                        //各种基于事件的操作，下面会有进一步介绍
                        form.on('radio', function(data){
                            console.log(data.value); //被点击的radio的value值
                            console.log(n_date);
                     
                            var hourFlowUrl;
                            var type;
                            if (data.value == "0") {
                                hourFlowUrl = '/in_hour_flow';
                                type = "入站";
                            }
                            else if (data.value == "1"){
                                hourFlowUrl = '/out_hour_flow';
                                type = "出站";
                            }
                            else {
                                console.log('error');
                            }

                            $.ajax({
                                type: "POST",
                                data: value,
                                url: hourFlowUrl,
                                dataType: 'json',
                                async: false,
                                success: function (result) {
                                    //更新数据
                                    hourFlow = result;
                                    hourFlowData = getHourFlowData(hourFlow, stations);

                                    //更新图表
                                    setGraphOptions(graphOption, hourFlowData, type);
                                    graphChart.setOption(graphOption);
                                }
                            });
                            
                        }); 
                        
                        form.on('select', function(data){
                            console.log(data.value); //得到被选中的值
                            console.log(n_date);
                            //切换线路代码写这儿
                            $.ajax({
                                type: 'POST',
                                url: '/split_flow/' + data.value,
                                async: false,
                                data: value,
                                datatype: 'json',
                                success: function (result) {
                                    splitFlow = result;

                                    uplineFlow = downlineFlow = [];
                                    splitNames = Object.keys(splitFlow);
                                    for (let index = 0; index < splitNames.length; index++){
                                        var split = splitFlow[splitNames[index]];
                                        uplineFlow.push(split.up);
                                        downlineFlow.push(split.down);
                                    }

                                    setBarOption(barOption, uplineFlow, downlineFlow, splitNames, data.value);
                                    splitChart.setOption(barOption);

                                    splitRank = [];
                                    getSplitRank(splitRank, data.value);
                                }
                            });
                        }); 
                    });
                    
                    
                }
            )

        }
        ,change: function(value, date){ //改变日期后
            n_date = value;
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
                    // console.log(result);
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
                    // console.log(result);
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
        
            var hourFlow;
            $.ajax({
                type: "POST",
                data: value,
                url: '/out_hour_flow',
                dataType: 'json',
                async: false,
                success: function (result) {
                    hourFlow = result;
                }
            });
    
            function getJsonData(url){
                var jsData;
                $.ajax({
                        url: url,
                        type: "GET",
                        data: value,
                        dataType: "json", 
                        async: false,
                        success: function(data) {
                            jsData = data;
                        }
                    })
                return jsData;
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
            function getHourFlowData(hourFlow, stations) {
                var hourFlowList = [];
                for (let i = 6; i <= 21; i++) {
                    var hour = {};
                    hour.staList = [];
                    stations.forEach(function (station) {
                        var staName = station.name;
        
                        var sta = JSON.parse(JSON.stringify(station));
                        
                        if (hourFlow[staName]) {
                            sta.value = hourFlow[staName][`${i}`];
                            if (sta.value == 0) 
                                sta.symbolSize = 10;  //如果客流量为0 设置最小size为10
                            else 
                                //否则取对数降低增长速度
                                sta.symbolSize = Math.log(hourFlow[staName][`${i}`]) * 10 + 10;
                        } else {
                            sta.value = 0;
                            sta.symbolSize = 10;
                        }
                        
                        sta.itemStyle.color = station.itemStyle.borderColor;
                        sta.itemStyle.borderWidth = 0;
                        sta.itemStyle.opacity = 0.75;
        
                        hour.staList.push(sta);
                    });
                    hourFlowList.push(hour);
                }
                return hourFlowList;
            }
            
            //配置图表属性
            function setGraphOptions(option, hourFlowData, type = "出站") {
                option.options = [];
                for (let i = 0; i <= 15; i++){ 
                    option.options.push({
                        title: {
                            text: '轨道交通' + type + '客流分布 ' + timelist()[i]
                        },
                        series: [{
                            data: hourFlowData[i].staList,
                            links: links,
                        }]
                    })
                    
                }
            }

            var graphOption = {
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
            
            var hourFlowData = getHourFlowData(hourFlow, stations);
            setGraphOptions(graphOption, hourFlowData);
            graphChart.setOption(graphOption);
            
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
            
            var uplineFlow = downlineFlow = [];
            var splitNames = Object.keys(splitFlow);
            for (let index = 0; index < splitNames.length; index++){
                var split = splitFlow[splitNames[index]];
                uplineFlow.push(split.up);
                downlineFlow.push(split.down);
            }
                            
            function setBarOption(option, y1, y2, x) {
                option.xAxis[0].data = x;
                option.xAxis[1].data = x;
                option.series[0].data = y1;
                option.series[1].data = y2;
            }

            var barOption = {
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

            setBarOption(barOption, uplineFlow, downlineFlow, splitNames);
            splitChart.setOption(barOption);

            var ODChart = echarts.init(document.getElementById('od_graph'));
            var ODFlow;
            $.ajax({
                type: 'POST',
                url: '/od_flow',
                async: false,
                data: value,
                dataType: 'json',
                success: function (result) {
                    ODFlow = result;
                    console.log(ODFlow);
                }
            });

            function compare(name)
            {
                return function(a,b){
                    var sta1 = a[name];
                    var sta2 = b[name];
                    var line1 = parseInt(ODFlow[sta1][0].split('号')[0]);
                    var line2 =parseInt(ODFlow[sta2][0].split('号')[0]);
                    
                    return line1-line2;
                }
            }

            var staColor = {
                '1号线': '#73DDFF',
                '2号线': '#73ACFF',
                '3号线': '#FDD56A',
                '4号线': '#FDB36A',
                '5号线': '#FD866A',
                '10号线': '#9E87FF',
                '11号线': '#58D5FF',
                '12号线': '#E271DE'
            }

            var ODLinks = [];
            var ODstations = [];
            var stationNames = Object.keys(ODFlow);

            function GetODFlowData(ODLinks, ODstations, stationNames) {
                for (let i = 0; i < (stationNames.length / 2); i++){
                    let source = stationNames[i];

                    let targetDict = ODFlow[source][1];
                    let targetList = Object.keys(targetDict);
                    for (let j = 0; j < (targetList.length / 2); j++) {
                        let target = targetList[j];
                        if (targetDict[target][1] != 0) {
                            ODLinks.push({
                                'source': source,
                                'target': target,
                                'value': targetDict[target][1]
                            });
                        }
                    }

                    ODstations.push({
                        name: source,
                        symbolSize: 6,
                        itemStyle: {
                            color: staColor[ODFlow[source][0]]
                        },
                        category: ODFlow[source][0]
                    });
                }
                ODstations = ODstations.sort(compare('name'));
            }

            function SetODOption(ODOption, ODstations, ODLinks) {
                ODOption.series.data = ODstations;
                ODOption.series.links = ODLinks;
                return ODOption;
            }

            var ODOption = {
                title: {
                    text: '地铁站点OD关系图',
                    left:"center",
                    textStyle:{
                        color:"#000"
                    }
                },
                legend: [{ data: lineNames, orient: 'vertical', right: '2%' }],
                tooltip: {trigger:'item'},
                animationDurationUpdate: 1500,
                animationEasingUpdate: 'quinticInOut',
                series: [{
                    name: "relation",
                    type: 'graph',
                    layout: 'circular',
                    circular: {
                        rotateLabel: true
                    },
                    data: ODstations,
                    links: ODLinks,
                    roam: true,
                    label: {
                        show: false,
                        position: 'right',
                        formatter: '{b}',
                        interval: 0
                    },
                    categories:categories,
                    emphasis: {
                        lineStyle: {
                            width: "3"
                        }
                    },
                    focusNodeAdjacency: true,
                    lineStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                                offset: 0,
                                color: '#4e8ebf'
                            },
                            {
                                offset: 0.45,
                                color: '#9ac8e0'
                            },
                            {
                                offset: 0.65,
                                color: '#ba3036'
                            },
                            {
                                offset: 1,
                                color: '#c84641'
                            }
                        ]),
                        curveness: 0.3
                    }
                }]
            };
            
            GetODFlowData(ODLinks, ODstations, stationNames);
            SetODOption(ODOption, ODstations, ODLinks);
            ODChart.setOption(ODOption);

            layui.use('form', function(){
                var form = layui.form;
                
                //各种基于事件的操作，下面会有进一步介绍
                form.on('radio', function(data){
                    console.log(data.value); //被点击的radio的value值
                    console.log(n_date);
                
                    var hourFlowUrl;
                    var type;
                    if (data.value == "0") {
                        hourFlowUrl = '/in_hour_flow';
                        type = "入站";
                    }
                    else if (data.value == "1"){
                        hourFlowUrl = '/out_hour_flow';
                        type = "出站";
                    }
                    else {
                        console.log('error');
                    }

                    $.ajax({
                        type: "POST",
                        data: value,
                        url: hourFlowUrl,
                        dataType: 'json',
                        async: false,
                        success: function (result) {
                            //更新数据
                            hourFlow = result;
                            hourFlowData = getHourFlowData(hourFlow, stations);

                            //更新图表
                            setGraphOptions(graphOption, hourFlowData, type);
                            graphChart.setOption(graphOption);
                        }
                    });
                    
                }); 
                
                
                form.on('select', function(data){
                    console.log(data.value); //得到被选中的值
                    console.log(n_date);
                    //切换线路代码写这儿
                    $.ajax({
                        type: 'POST',
                        url: '/split_flow/' + data.value,
                        async: false,
                        data: value,
                        datatype: 'json',
                        success: function (result) {
                            splitFlow = result;

                            uplineFlow = downlineFlow = [];
                            splitNames = Object.keys(splitFlow);
                            for (let index = 0; index < splitNames.length; index++){
                                var split = splitFlow[splitNames[index]];
                                uplineFlow.push(split.up);
                                downlineFlow.push(split.down);
                            }

                            setBarOption(barOption, uplineFlow, downlineFlow, splitNames);
                            splitChart.setOption(barOption);
                        }
                    });
                }); 
            });
        }
    });
})


