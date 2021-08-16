var nav = document.querySelector(".nav");
var content = document.querySelector(".content");
var taggle = document.querySelector(".mytoggle");
var tohid = document.querySelectorAll(".nav span");
var aa = document.querySelectorAll(".nav ul li a");
var des = document.querySelectorAll("[data-ctt]");
taggle.addEventListener('click',function()
{
    if(!state){
        nav.style.width = '55px';
        content.style.marginLeft = '50px';
        state = 1;
        // console.log(tohid);
        for(var i=0;i<6;i++)
        {
            tohid[i].style.display = 'none';
        }
        for(var i=0;i<5;i++)
        {
            aa[i].dataset.ctt = '';
        }

    }
    else{
        nav.style.width = '250px';
        content.style.marginLeft = '250px';
        content.style.width = '1286px';
        state = 0;
        for(var i=0;i<6;i++)
        {
            tohid[i].style.display = 'inline';
        }
        for(var i=0;i<5;i++)
        {
            aa[i].dataset.ctt = '>';
        }
    }
    
    month_chart.resize();
    week_chart.resize();
    line_pie.resize();
    graphChart.resize();
    inoutChart.resize();
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
var areanum = 1;
function updatewea(data)
{
    // console.log(data);
    var today_weather = document.querySelector("#today_weather");
    today_weather.innerHTML = get_icon_words(data[0].weather);
    var today_wea_txt =  document.querySelector("#today_wea_txt");
    today_wea_txt.innerHTML = data[0].weather;
    var today_temp = document.querySelector("#today_temp");
    today_temp.innerHTML = data[0].temp;
    var today_wind = document.querySelector("#today_wind");
    today_wind.innerHTML = data[0].wind;
}

function updateinfo(data)
{
    var day_flow = document.querySelector("#day_flow");
    var yesstate = document.querySelector("#yesstate");
    var yesper = document.querySelector("#yesper");
    var monthstate = document.querySelector("#monthstate");
    var monthper = document.querySelector("#monthper");
    var yearstate = document.querySelector("#yearstate");
    var yearper = document.querySelector("#yearper");

    day_flow.innerHTML = data.day_flow;
    if(data.day_cmp<0) {
        yesstate.innerHTML = '&#xe607;';
        yesstate.style.color = 'red';
        yesper.innerHTML = -data.day_cmp + '%';
    }
    else {
        yesstate.innerHTML = '&#xe608';
        yesstate.style.color = '#1296DB';
        yesper.innerHTML = parseFloat(data.day_cmp) + '%';
    }

    if(data.month_cmp<0) {
        monthstate.innerHTML = '&#xe607;';
        monthstate.style.color = 'red';
        monthper.innerHTML = -data.month_cmp + '%';
    }
    else {
        monthstate.innerHTML = '&#xe608';
        monthstate.style.color = '#1296DB';
        monthper.innerHTML = parseFloat(data.month_cmp) + '%';
    }

    if(data.year_cmp<0) {
        yearstate.innerHTML = '&#xe607;';
        yearstate.style.color = 'red';
        yearper.innerHTML = -data.year_cmp + '%';
    }
    else {
        yearstate.innerHTML = '&#xe608';
        yearstate.style.color = '#1296DB';
        yearper.innerHTML = parseFloat(data.year_cmp) + '%';
    }
    
    var am_peak = document.querySelector("#am_peak");
    var pm_peak = document.querySelector("#pm_peak");
    am_peak.innerHTML = data.am_peak_flow;
    pm_peak.innerHTML = data.pm_peak_flow;

    var tolpersoncnt = document.querySelector("#tolpersoncnt");
    tolpersoncnt.innerHTML = data.day_pass_num;

    var rest = document.querySelector("#rest");
    if(data.is_hoilday=="是") rest.innerHTML = "休息日";
    else rest.innerHTML = "工作日";
}

function change()
{
    var value = n_date;

    //测试接口
    $.ajax({
        type: 'POST',
        data: value,
        async: true,
        url: ' /history/thisday_info',
        dataType: 'json',
        success: function (data) {
            // console.log(data);
            updateinfo(data);
        }
    });
    $.ajax({
        type: 'POST',
        data: value,
        async: true,
        url: '/api/weather_info/day',
        dataType: 'json',
        success: function (data) {
            // console.log(data);
            updatewea(data);
        }
    });

    //
    month_chart = echarts.init(document.getElementById('month_line'), 'white', {renderer: 'canvas'});
    $.ajax({
        type: 'POST',
        data: value,
        async: true,
        url: 'history/day_flow/line',
        dataType: 'json',
        success: function (result) {
            // month_chart.setOption(result);
            // console.log(result);
            option_monthline.xAxis.data = result.xAxis.data;
            option_monthline.series[0].data = result.series[0].data;
            month_chart.setOption(option_monthline);
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
            // week_chart.setOption(result);
            option_weekbar.xAxis[0].data = result.xAxis[0].data;
            option_weekbar.series[0].data = result.series[0].data;
            week_chart.setOption(option_weekbar);
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

    line_pie = echarts.init(document.getElementById('line_percent'));
    $.ajax({
        type: "POST",
        data: value,
        async: true,
        url: "/history/line/pie",
        dataType: 'json',
        success: function (result) {
            console.log(result);
            result.title = {
                text: '线路流量占比',
                left: 'center',
                textStyle: {
                    fontWeight: 400
                }
            };
            result.color = ['#63b2ee', '#76da91' ,'#f8cb7f' , '#f89588' , '#7cd6cf' , '#9192ab' , '#7898e1' , '#efa666'];
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
            graphOption.title = {
                text: '线路流量占比',
                left: 'center',
                textStyle: {
                    fontWeight: 400
                }
            };
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
            barOption.title = {
                text: '地铁线路断面客流',
                left: 'center',
                textStyle: {
                    fontWeight: 400
                }
            };
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
            ODOption.title = {
                text: '地铁站点OD关系图',
                left: 'center',
                textStyle: {
                    fontWeight: 400
                }
            };
            ODOption.color = ['#63b2ee', '#76da91' ,'#f8cb7f' , '#f89588' , '#7cd6cf' , '#9192ab' , '#7898e1' , '#efa666'];
            ODChart.setOption(ODOption);
        }
    });

    //单站点入点出图表
    inoutChart = echarts.init(document.getElementById('area_inout'));

    $.ajax({
        type: "POST",
        url: '/history/area/inout_flow',
        data: JSON.stringify({date: value, index: areanum}),
        dataType: 'json',
        success: function (param) {
            setAreaInoutChart(param[0], param[1], param[2]);
            inoutOption.title = {
                text: '线路流量占比',
                left: 'center',
                textStyle: {
                    fontWeight: 400
                }
            };
            inoutChart.setOption(inoutOption);
        }
    });
}

//区域点入点出流量分布
var area = document.querySelector('#area').children;
for(var i=0;i<area.length;i++)
{
    // console.log(area[i]);
    thisarea = area[i];
    thisarea.addEventListener('click',function()
    {
        // console.log(this.dataset.index);
        // console.log(area[areanum]);
        area[areanum-1].style.backgroundColor = '#fff';
        areanum = this.dataset.index;
        this.style.backgroundColor = '#37A2DA';

        inoutChart = echarts.init(document.getElementById('area_inout'));

        $.ajax({
            type: "POST",
            url: '/history/area/inout_flow',
            data: JSON.stringify({date: n_date, index: areanum}),
            dataType: 'json',
            success: function (param) {
                setAreaInoutChart(param[0], param[1], param[2]);
                inoutOption.title = {
                    text: '线路流量占比',
                    left: 'center',
                    textStyle: {
                        fontWeight: 400
                    }
                };
                inoutChart.setOption(inoutOption);
            }
        });
    })
}

function get_icon_words(wea){
    if(wea=="晴") return '&#xe8bc;';
    else if(wea=="阴") return '&#xe625;';
    else if(wea=="多云") return '&#xe646;';
    else if(wea=="阵雨") return '&#xe615;';
    else if(wea=="小雨") return '&#xe60c;';
    else if(wea=="中雨") return '&#xe669;';
    else if(wea=="大雨") return '&#xe64c;';
    else if(wea=="暴雨") return '&#xe64f;';
}

//响应控件事件
layui.use('form', function(){
    var form = layui.form;
    
    //各种基于事件的操作，下面会有进一步介绍
    form.on('radio', function(data){
        // console.log(data.value); //被点击的radio的value值
        // console.log(n_date);
    
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
            data: n_date,
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
        // console.log(data.value); //得到被选中的值
        // console.log(n_date);
        //切换线路代码写这儿
        $.ajax({
            type: 'POST',
            url: '/history/split_flow/' + data.value,
            async: true,
            data: n_date,
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
            change();
        }
        ,change: function(value, date){ //改变日期后
            n_date = value;
            change();
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
                text: hours + "时间段区域入站出站流量分布",
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

//单月客流选项
var option_monthline = {
    title: {
        text: '本月客流波动',
        left: 'center',
        textStyle: {
            fontWeight: 400
        }
    },
    color: '#5873C7',
    tooltip: {
        trigger: 'axis'
    },    
    grid: {
        left: '2%',
        right: '9%',
        bottom: '3%',
        containLabel: true
    //     show: true,// 显示边框
    //   borderColor: '#012f4a',// 边框颜色
    },
    xAxis: {
        type: 'category',
        boundaryGap: false,
        axisTick: {
            show: false,
            alignWithLabel: true
        },
        name: '日期',
        
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    },
    yAxis: {
        type: 'value',
        name: '客流量(人次)',
        axisLine: {
            show:true,
            symbol:['none', 'arrow'],
            symbolSize:[5,10]
        }
    },
    series: [
        {
            type: 'line',
            data: [10, 11, 13, 11, 12, 12, 9],
            // markPoint: {
            //     data: [
            //         {type: 'max', name: '最大值'}
            //     ]
            // },
            markLine: {
                symbol: 'none',
                data: [
                    {
                        type: 'average', 
                        name: '平均值'
                
                    }
                ],
                label: {
                    show:true,
                    formatter: '平均值:{c}',
                    position:'insideEndTop'
                }
            },
            // smooth: true,
            // 设置拐点 小圆点
            symbol: "circle",
            // 拐点大小
            symbolSize: 8,
            // 设置拐点颜色以及边框
            itemStyle: {
                // color: "#0184d5",
                borderColor: "rgba(221, 220, 107, .4)",
                borderWidth: 12
            },
            // 开始不显示拐点， 鼠标经过显示
            showSymbol: false,
            // 填充区域
            areaStyle: { }
        }
    ]
};

//本周客流柱形图option
var option_weekbar = {
    color:'#37A2DA',
    title:{
        text:'本周客流柱形图',
        left: 'center',
        textStyle: {
            fontWeight: 400
        }
    },
    tooltip: {
        trigger: 'axis',
        axisPointer: {            // 坐标轴指示器，坐标轴触发有效
            type: 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
        }
    },
    grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
    },
    xAxis: [
        {
            type: 'category',
            data: [],
            axisTick: {
                show: false,
                alignWithLabel: true
            },
            axisLine: {
                show:true,
                symbol:['none', 'arrow'],
                symbolSize:[5,10]
            }
        }
    ],
    yAxis: [
        {
            type: 'value',
            name: '客流量(人次)',
            axisLine: {
                show:true,
                symbol:['none', 'arrow'],
                symbolSize:[5,10]
            }
        }
    ],
    series: [
        {
            name: '',
            type: 'bar',
            barWidth: '40%',
            data: [10, 52, 200, 334, 390]
        }
    ]
};

