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
var nav = document.querySelector(".nav");
var content = document.querySelector(".content");
var taggle = document.querySelector(".mytoggle");
taggle.addEventListener('click',function()
{
    if(!state){
        nav.style.width = '50px';
        content.style.marginLeft = '50px';
        state = 1;
    }
    else{
        nav.style.width = '250px';
        content.style.marginLeft = '250px';
        state = 0;
    }
    
    month_chart.resize();
    week_chart.resize();
    line_pie.resize();
    graphChart.resize();
    splitChart.resize();
    ODChart.resize();
});
var month_chart;
var week_chart;
var line_pie;
var graphChart;
var splitChart;
var ODChart;
var state = 0;//表示未折叠


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
            // $(
            //     function(){
            value = '2020-01-01';
            month_chart = echarts.init(document.getElementById('month_line'), 'white', {renderer: 'canvas'});
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
    
            week_chart = echarts.init(document.getElementById('curr_week_line'), 'white', {renderer: 'canvas'});
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
            var day_cmp = document.getElementById('day_cmp');
            var month_cmp = document.getElementById('month_cmp');
            var year_cmp = document.getElementById('year_cmp');
            var am_peak_flow = document.getElementById('am_peak_flow');
            var pm_peak_flow = document.getElementById('pm_peak_flow');
            $.ajax({
                type: 'POST',
                data: value,
                async: true,
                url: '/history/thisday_info',
                dataType: 'json',
                success: function (result) {
                    weather_info.innerHTML = result.weather;
                    is_hoilday.innerHTML = result.is_hoilday;
                    day_flow.innerHTML = result.day_flow;
                    day_cmp.innerHTML = result.day_cmp + '%';
                    month_cmp.innerHTML = result.month_cmp + '%';
                    year_cmp.innerHTML = result.year_cmp + '%';
                    am_peak_flow.innerHTML = result.am_peak_flow;
                    pm_peak_flow.innerHTML = result.pm_peak_flow;
                }
            });
    
            $.ajax({
                type: 'POST',
                data: value,
                async: true,
                url: '/history/sta_rank',
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
    
            line_pie = echarts.init(document.getElementById('line_percent'));
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
    
            
            //线路关系图
            graphChart = echarts.init(document.getElementById('line_graph'));

            graphChart.on('click', function (param) {
                var reg = /Sta[1-9][0-9][0-9]/;
                if(reg.test(param.data.name)){
                    location.href = '/station/' + param.data.name;
                }
            });


            $.ajax({
                type: "POST",
                data: value,
                url: '/history/out_hour_flow',
                dataType: 'json',
                async: true,
                success: function (result) {
                    var hourFlow = result;
                    var res = getHourFlowData(hourFlow, stations);

                    var hourFlowData = res['hourFlow'];
                    var alertStations = res['alertStations'];
                    setGraphOptions(graphOption, hourFlowData, alertStations);
                    graphChart.setOption(graphOption);
                }
            });
            
            
            // 线路断面图
            splitChart = echarts.init(document.getElementById('split_bar'));

            $.ajax({
                type: 'POST',
                url: '/history/split_flow/1',
                async: true,
                data: value,
                datatype: 'json',
                success: function (result) {
                    var splitFlow = result;

                    var uplineFlow  = [];
                    var downlineFlow = [];
                    var splitNames = Object.keys(splitFlow);
                    for (let index = 0; index < splitNames.length; index++){
                        var split = splitFlow[splitNames[index]];
                        uplineFlow.push(split.up);
                        downlineFlow.push(split.down);
                    }

                    setBarOption(barOption, uplineFlow, downlineFlow, splitNames);
                    splitChart.setOption(barOption);
                }
            });
            

            //od关系图
            ODChart = echarts.init(document.getElementById('od_graph'));            var ODFlow;
            $.ajax({
                type: 'POST',
                url: '/history/od_flow',
                data: value,
                dataType: 'json',
                async: true,
                success: function (result) {
                    var ODLinks = [];
                    var ODstations = [];
                    var stationNames = Object.keys(result);
                    
                    getODFlowData(result, ODLinks, ODstations, stationNames);
                    setODOption(ODOption, ODstations, ODLinks);
                     ODChart.setOption(ODOption);
                }
            });

            //单站点入点出图表
            inoutChart = echarts.init(document.getElementById('area_inout'));

            $.ajax({
                type: "POST",
                url: '/history/area/inout_flow',
                data: value,
                dataType: 'json',
                async: true,
                success: function (param) {
                    setAreaInoutChart(param[0], param[1], param[2]);
                    inoutChart.setOption(inoutOption);
                }
            });

            
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
                        hourFlowUrl = '/history/in_hour_flow';
                        type = "入站";
                    }
                    else if (data.value == "1"){
                        hourFlowUrl = '/history/out_hour_flow';
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
                        async: true,
                        success: function (result) {
                            //更新数据
                            var res = getHourFlowData(result, stations);
                            var hourFlowData = res['hourFlow']
                            var alertStations = res['alertStations'];

                            //更新图表
                            setGraphOptions(graphOption, hourFlowData, alertStations, type);
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
                        url: '/history/split_flow/' + data.value,
                        async: true,
                        data: value,
                        datatype: 'json',
                        success: function (result) {
                            splitFlow = result;

                            uplineFlow = [];
                            downlineFlow = [];
                            splitNames = Object.keys(splitFlow);
                            for (let index = 0; index < splitNames.length; index++){
                                var split = splitFlow[splitNames[index]];
                                uplineFlow.push(split.up);
                                downlineFlow.push(split.down);
                            }

                            setBarOption(barOption, uplineFlow, downlineFlow, splitNames, data.value);
                            splitChart.setOption(barOption);
                        }
                    });
                }); 
            });

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
            var day_cmp = document.getElementById('day_cmp');
            var month_cmp = document.getElementById('month_cmp');
            var year_cmp = document.getElementById('year_cmp');
            var am_peak_flow = document.getElementById('am_peak_flow');
            var pm_peak_flow = document.getElementById('pm_peak_flow');
            $.ajax({
                type: 'POST',
                data: value,
                async: true,
                url: '/history/thisday_info',
                dataType: 'json',
                success: function (result) {
                    weather_info.innerHTML = result.weather;
                    is_hoilday.innerHTML = result.is_hoilday;
                    day_flow.innerHTML = result.day_flow;
                    day_cmp.innerHTML = result.day_cmp + '%';
                    month_cmp.innerHTML = result.month_cmp + '%';
                    year_cmp.innerHTML = result.year_cmp + '%';
                    am_peak_flow.innerHTML = result.am_peak_flow;
                    pm_peak_flow.innerHTML = result.pm_peak_flow;
                }
            });
            $.ajax({
                type: 'POST',
                data: value,
                async: true,
                url: '/history/sta_rank',
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
        
            //线路关系图
            graphChart = echarts.init(document.getElementById('line_graph'));

            graphChart.on('click', function (param) {
                var reg = /Sta[1-9][0-9][0-9]/;
                if(reg.test(param.data.name)){
                    location.href = '/station/' + param.data.name;
                }
            });


            $.ajax({
                type: "POST",
                data: value,
                url: '/history/out_hour_flow',
                dataType: 'json',
                async: true,
                success: function (result) {
                    var hourFlow = result;
                    var res = getHourFlowData(hourFlow, stations);

                    var hourFlowData = res['hourFlow'];
                    var alertStations = res['alertStations'];
                    setGraphOptions(graphOption, hourFlowData, alertStations);
                    graphChart.setOption(graphOption);
                }
            });
            
            
            // 线路断面图
            splitChart = echarts.init(document.getElementById('split_bar'));

            $.ajax({
                type: 'POST',
                url: '/history/split_flow/1',
                async: true,
                data: value,
                datatype: 'json',
                success: function (result) {
                    var splitFlow = result;

                    var uplineFlow  = [];
                    var downlineFlow = [];
                    var splitNames = Object.keys(splitFlow);
                    for (let index = 0; index < splitNames.length; index++){
                        var split = splitFlow[splitNames[index]];
                        uplineFlow.push(split.up);
                        downlineFlow.push(split.down);
                    }

                    setBarOption(barOption, uplineFlow, downlineFlow, splitNames);
                    splitChart.setOption(barOption);
                }
            });
            

            //od关系图
            ODChart = echarts.init(document.getElementById('od_graph'));

            $.ajax({
                type: 'POST',
                url: '/history/od_flow',
                async: true,
                data: value,
                dataType: 'json',
                success: function (result) {
                    var ODLinks = [];
                    var ODstations = [];
                    var stationNames = Object.keys(result);
                    
                    getODFlowData(result, ODLinks, ODstations, stationNames);
                    setODOption(ODOption, ODstations, ODLinks);
                    ODChart.setOption(ODOption);
                }
            });

            //单站点入点出图表
            inoutChart = echarts.init(document.getElementById('area_inout'));

            $.ajax({
                type: "POST",
                url: '/history/area/inout_flow',
                data: value,
                dataType: 'json',
                success: function (param) {
                    setAreaInoutChart(param[0], param[1], param[2]);
                    inoutChart.setOption(inoutOption);
                }
            });

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
                        hourFlowUrl = '/history/in_hour_flow';
                        type = "入站";
                    }
                    else if (data.value == "1"){
                        hourFlowUrl = '/history/out_hour_flow';
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
                        async: true,
                        success: function (result) {
                            //更新数据
                            var res = getHourFlowData(result, stations);
                            var hourFlowData = res['hourFlow']
                            var alertStations = res['alertStations'];

                            //更新图表
                            setGraphOptions(graphOption, hourFlowData, alertStations, type);
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
                        url: '/history/split_flow/' + data.value,
                        async: true,
                        data: value,
                        datatype: 'json',
                        success: function (result) {
                            splitFlow = result;

                            uplineFlow = [];
                            downlineFlow = [];
                            splitNames = Object.keys(splitFlow);
                            for (let index = 0; index < splitNames.length; index++){
                                var split = splitFlow[splitNames[index]];
                                uplineFlow.push(split.up);
                                downlineFlow.push(split.down);
                            }

                            setBarOption(barOption, uplineFlow, downlineFlow, splitNames, data.value);
                            splitChart.setOption(barOption);
                        }
                    });
                }); 
            });

        }
    });
})

var lineNames = ['1号线', '2号线', '3号线', '4号线', '5号线', '10号线', '11号线', '12号线'];

//图例的数据数组 数组中的每一项代表一个系列的name
var legend = [{ data: lineNames, orient: 'vertical', top: '20%', right: '2%'  }];

//获取类目名称数组 用于和 legend 对应以及格式化 tooltip 的内容
var categories = lineNames.map(lineName => { return { name: lineName } });

var stations = getJsonData('/api/sta/json');
var links = getJsonData('/api/link/json');

var hoursList = ['7-9', '10-12', '13-15', '16-18', '19-21'];

var lineColor = {
    '1号线': '#73DDFF',
    '2号线': '#73ACFF',
    '3号线': '#FDD56A',
    '4号线': '#FDB36A',
    '5号线': '#9E87FF',
    '10号线': '#F8456B',
    '11号线': '#4AEAB0',
    '12号线': '#E271DE',
}

//----------关系图--------------
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
    color: ['#0000FF', '#EE1822', '#F39C12', '#FF00FF', '#800080', '#00FF00', '#00FFFF', '#FFFF00'], 
    backgroundColor: '#fff',
    coordinateSystem: "cartesian2d", //使用二维的直角坐标系（也称笛卡尔坐标系）
    xAxis: {
        show: false,
        min: 50,
        max: 2300,
        axisPointer: {
            show: true
        },
    },
    yAxis: {
        show: false,
        min: 0,
        max: 2000,
        axisPointer: {
            show: true
        },
    },
    tooltip: {
        trigger: 'item',
        formatter: function (param) {
            let label = "";

            if(param.componentType != 'timeline'){
                if (param.value) {
                    label = `站点名称: ${param.name} <br> 站点客流: ${param.value[2]}人`;
                }
            }
            else{
                label = param.name;
            }
            return label;
        }
    },
    legend: legend,
    series: [
        // 用关系图实现地铁地图
        {
            type: "graph",
            zlevel: 5,
            draggable: false,
            coordinateSystem: "cartesian2d", //使用二维的直角坐标系（也称笛卡尔坐标系）
            categories :categories,
            edgeSymbolSize: [0, 8], //边两端的标记大小，可以是一个数组分别指定两端，也可以是单个统一指定
            edgeLabel: {
              normal: {
                textStyle: {
                  fontSize: 60
                }
              }
            },
            symbol: "rect",
            symbolOffset: ["15%", 0],
            links: links,
            label: {
                normal: {
                    show: false,
                }
            },
            lineStyle: {
                normal: {
                    opacity: 0.6, //线条透明度
                    curveness: 0, //站点间连线曲度，0表示直线
                    width: 5, //线条宽度
                }
            }
        },
    ],
    options: []
}

function getJsonData(url){
    var jsData;
    $.ajax({
            url: url,
            type: "GET",
            dataType: "json", 
            async: false,
            success: function(data) {
                jsData = data;
            }
        })
    return jsData;
}

function timelist() {
    var timelist = [];
    for(let i = 6; i <= 21; i++){
        timelist.push(`${i}:00`);
    }
    return timelist;
}

//生成6-21点的客流数据
function getHourFlowData(hourFlow, stations) {
    var alertStations = [];

    var hourFlowList = [];
    for (let i = 6; i <= 21; i++) {
        var hour = {};
        hour.staList = [];
        var hourAlertList = [];
        stations.forEach(function (station) {
            var staName = station.name;
            var sta = JSON.parse(JSON.stringify(station));

            if (lineNames.indexOf(sta.name) == -1) {
                sta.label.show = false 
                sta.itemStyle.color = station.itemStyle.color;
                sta.symbolSize = [10, 10];
                sta.value.push(0);
                if (hourFlow[staName]) {
                    sta.value[2] = hourFlow[staName][`${i}`];
                    if (sta.value[2]) {
                        let size = Math.log(hourFlow[staName][`${i}`]) * 5 + 10;
                        sta.symbolSize = [size, size];
                        if (sta.value[2] >= 20) {
                            sta.symbolSize = [10, 10];
                            hourAlertList.push({
                                name: sta.name,
                                value: sta.value,
                                itemStyle: {
                                    color: station.itemStyle.color 
                                }
                            });
                        }
                    }
                }      
            } 
            hour.staList.push(sta);
        });
        hourFlowList.push(hour);
        alertStations.push(hourAlertList);
    }

    return {
        'hourFlow': hourFlowList, 
        'alertStations': alertStations
    };
}

//配置图表属性
function setGraphOptions(option, hourFlowData, alertStations, type = "出站") {
    option.options = [];
    for (let i = 0; i <= 15; i++){ 
        option.options.push({
            title: {
                text: '轨道交通' + type + '客流分布 ' + timelist()[i],
                textStyle: {
                    color: 'black',
                    fontSize: 20
                },
                x: 'center',
                top: 10
            },
            series: [{
                    data: hourFlowData[i].staList,
                },
                {
                    type: "effectScatter",
                    scaling: 1.5,
                    // color: '#F8456B',
                    //该系列使用的坐标系
                    coordinateSystem: "cartesian2d",
                    symbolSize: function(val) {
                        return val[2]*1.2;
                    },
                    data: alertStations[i],
                    showEffectOn: "render",
                    effectType: "ripple",
                    rippleEffect: {
                        period: 4,
                        scale: 4,
                        brushType: "stroke" 
                    },
                    hoverAnimation: true            
                }
            ]
        },
        )
    }
}

//----------线路断面--------------
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
            data: []
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
            data: []
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
            data: [],
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
            data: [],
            xAxisIndex: 1,
            yAxisIndex: 1,
            itemStyle: {
                color: '#73ACFF',
                barBorderRadius: [0, 0, 4, 4]
            },
            
        }
    ]
};

function setBarOption(option, y1, y2, x, line) {
    if (line)
        option.title.subtext = line + '号线';
    else
        option.title.subtext = '1号线';
    option.xAxis[0].data = x;
    option.xAxis[1].data = x;
    option.series[0].data = y1;
    option.series[1].data = y2;
}

//----------OD客流--------------
var ODOption = {
    title: {
        text: '地铁站点OD关系图',
        left:"center",
        textStyle:{
            color:"#000"
        }
    },
    color: ['#73DDFF','#73ACFF','#FDD56A','#FDB36A', '#9E87FF', '#F8456B', '#4AEAB0', '#E271DE'],
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
        data: [],
        links: [],
        roam: false,
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

function compare(name, ODFlow)
{
    return function(a,b){
        var sta1 = a[name];
        var sta2 = b[name];
        var line1 = parseInt(ODFlow[sta1][0].split('号')[0]);
        var line2 =parseInt(ODFlow[sta2][0].split('号')[0]);
        
        return line1-line2;
    }
}

function getODFlowData(ODFlow, ODLinks, ODStations, stationNames) {
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

        ODStations.push({
            name: source,
            symbolSize: 6,
            itemStyle: {
                color: lineColor[ODFlow[source][0]]
            },
            category: ODFlow[source][0]
        });
    }
    ODStations = ODStations.sort(compare('name', ODFlow));
}

function setODOption(ODOption, ODstations, ODLinks) {
    ODOption.series[0].data = ODstations;
    ODOption.series[0].links = ODLinks;
    return ODOption;
}

//----------单站点入点出--------------
var inoutOption =  {
    timeline: {
        axisType: 'category',
        show: true,
        autoPlay: false,
        playInterval: 1000,
        data: hoursList
    },
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "shadow"
      }
    },
    grid: {
      bottom: "10%"
    },
    legend: {
      data: [
        { name: "流入量", icon: "circle" },
        { name: "流出量", icon: "circle" },
      ],
      itemGap: 12,
      right: 20,
      textStyle: {
        fontSize: 14,
        color: "#5D6C8E",
        fontFamily: "SourceHanSansCN-Regular"
      }
    },
    xAxis: [
      {
        type: "value",
        axisPointer: {
          type: "shadow"
        },
        // 横坐标 分割线等取消显示
        axisTick: {
          show: false
        },
        axisLine: {
          show: false
        },
        splitLine: {
          show: false
        },
        axisLabel: {
          show: false
        }
      }
    ],
    yAxis: [
      {
        type: 'category',
        axisTick: {
            show: false
        },
        axisLine: {
            show: true,
            lineStyle: {
                color: 'rgba(121,121,121,0.3)'
            }
        },
        axisLabel: {
          textStyle: {
            fontSize: 15,
            color: "#5D6C8E",
            fontFamily: "SourceHanSansCN-Regular"
          }

        },
        data: [],
      },
      {
        type: "category",
        axisLine: {
          show: false
        },
        axisTick: {
          show: false
        },
        axisLabel: {
          textStyle: {
            fontSize: 18,
            color: "#5D6C8E",
            fontFamily: "SourceHanSansCN-Regular"
          }
        },
        data: []
      }
    ],
    series: [
      {
        name: "流入量",
        type: "bar",
        // 宽度
        barWidth: "16",
        // 堆叠
        stack: "总量",
        showBackground: true,
        // 全部背景
        backgroundStyle: {
          color: "#fff"
        },
        itemStyle: {
          normal: {
            show: true,
            textStyle: {
              fontSize: 16
            },
            color: new echarts.graphic.LinearGradient(
              0, 0, 1, 0,
              [
                {
                  offset: 0,
                  color: "#FFF0A0"
                },
                {
                  offset: 1,
                  color: "#FFD355"
                }
              ],
              false
            )
          }
        }
      },
      {
        name: "流出量",
        type: "bar",
        // 宽度
        barWidth: "16",
        // 堆叠
        stack: "总量",
        showBackground: true,
        // 全部背景
        backgroundStyle: {
          color: "#fff"
        },
        itemStyle: {
          normal: {
            show: true,
            textStyle: {
              fontSize: 16
            },
            color: new echarts.graphic.LinearGradient(
              0, 0, 1, 0,
              [
                {
                  offset: 0,
                  color: "#90BEFF"
                },
                {
                  offset: 1,
                  color: "#5EA1FF"
                }
              ],
              false
            )
          }
        }
      }
    ],
    options: []
};

function setAreaInoutChart(staList, inFlow, outFlow){
    inoutOption.options = [];
    inoutOption.yAxis[0].data = staList;
    for(let i = 0; i < hoursList.length; i++){
        let hours = hoursList[i];
        inoutOption.options.push({
            title:{
                text: hours + "时间段点入点出流量分布",
            },
            series:[
                {
                    data:inFlow[hours]
                },
                {
                    data:outFlow[hours]
                }
            ]
        });
    }
}

