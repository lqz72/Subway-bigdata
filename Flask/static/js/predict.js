//收缩框
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
    monthLine.resize();
    weekLine.resize();
    linePie.resize();
    hourLine.resize();
    evalRadar.resize();
    graphChart.resize();
});
var state = 0;//表示未折叠
var monthLine;
var weekLine;
var linePie;
var hourLine;
var evalRadar;
var graphChart;

var data_b = {};
data_b['alg'] = 1;
data_b['choose_wea'] = 3;
data_b['choose_temp'] = 28;
data_b['c_date'] = "2020-07-17";
data_b['inout_s'] = 0;
data_b['graphtaggle'] = 0; //切换进出/断面,0表示进出

var alg; //选择的算法
var choose_wea; //选择的天气
var choose_temp; //选择的温度
var flag = 0;//表示未选择温度,用于解决之前的bug

//向后端传取数据代码写这儿,对象时s_data 为一个字符串（对象转化而来）
function change_data()
{
    //转换成字符串的对象
    s_data = JSON.stringify(data_b);
    //评分图
    var markgraph = echarts.init(document.querySelector("#markpre"));            
    //markgraph.setOption(option_markpre);
    $.ajax({
        url: '/pred/day_eval',
        type: 'POST',
        data: s_data,
        dataType: 'json',
        async: true,
        success: function (data) {
            markpreOption.series[0].data[0].value = data['eval'];
            markgraph.setOption(markpreOption);
            
            let measure_list = [];
            if(data['eval'] > 50){  //小客流
                measure_list =  makeRandomArr(lowLevelMeasures, 4);
            }
            else{  //大客流
                measure_list =  makeRandomArr(highLevelMeasures, 4);
            }

            var measure = $("#measure li");
            for(let i = 0; i < measure.length; i++){
                measure[i].innerHTML = measure_list[i];
            }
        }
    });

    //更新进出站图表信息
    inout_s();
    //更新天气数据
    $.ajax({
        url:"/api/weather_info/week",
        type:"POST",
        async: true,
        data:data_b['c_date'],
        success: function(data){
            // console.log(data);
            var today = document.querySelector("#today");
            today.innerText = data[0].date;
            var today_weather = document.querySelector("#today_weather");
            today_weather.innerHTML = get_icon_words(data[0].weather);
            var today_wea_txt =  document.querySelector("#today_wea_txt");
            today_wea_txt.innerHTML = data[0].weather;
            var today_temp = document.querySelector("#today_temp");
            today_temp.innerHTML = data[0].temp;
            var today_wind = document.querySelector("#today_wind");
            today_wind.innerHTML = data[0].wind;
            for(var i=0;i<=6;i++)
            {
                var str1 = '#d'+i+'_icon';
                document.querySelector(str1).innerHTML = get_icon_words(data[i].weather);
                var str2 = '#d'+i+'_temp';
                document.querySelector(str2).innerHTML = data[i].temp;
                if(i>=3){
                    var str3 = '#d'+i+'_date';
                    document.querySelector(str3).innerHTML = data[i].date.split('-')[2]+'日';
                }
            }
            var t = parseInt(data[0].temp.substr(0,2));
            if(!flag){
                temp_slider.setValue(t+5);
            }
            else flag = 0;
        }
    });

    //更新当日总体预测信息
    $.ajax({
        url: '/pred/day_info',
        type: 'POST',
        data: s_data,
        dataType: 'json',
        async: true,
        success: function (data) {
            // console.log(data);
            change_dayinfomation(data);
        }
    })

    /*------------------pyecharts 图表------------------*/
    monthLine = echarts.init(document.getElementById('month_line'));
    $.ajax({
        url: '/pred/month/line',
        type: 'POST',
        data: s_data,
        dataType: 'json',
        async: true,
        success: function (result) {
            // monthLine.setOption(option);
            option_monthline.xAxis.data = result.xAxis.data;
            option_monthline.series[0].data = result.series[0].data;
            monthLine.setOption(option_monthline);
        }
    })

    weekLine = echarts.init(document.getElementById('week_line'));
    $.ajax({
        url: '/pred/week/line',
        type: 'POST',
        async: true,
        data: s_data,
        dataType: 'json',
        success: function (result) {
            // weekLine.setOption(option);
            option_weekbar.xAxis[0].data = result.xAxis[0].data;
            option_weekbar.series[0].data = result.series[0].data;
            weekLine.setOption(option_weekbar);
        }
    })

    linePie = echarts.init(document.getElementById('line_pie'));
    $.ajax({
        url: '/pred/line/pie',
        type: 'POST',
        async: true,
        data: s_data,
        dataType: 'json',
        success: function (option) {
            option.title = {
                text: '线路流量占比',
                left: 'center',
                textStyle: {
                    fontWeight: 400
                }
            };
            linePie.setOption(option);
        }
    })

    hourLine = echarts.init(document.getElementById('hour_line'));
    $.ajax({
        url: '/pred/hour/line',
        type: 'POST',
        async: true,
        data: s_data,
        dataType: 'json',
        success: function (result) {
            // hourLine.setOption(option);
            option_hourline.xAxis.data = result.xAxis.data;
            option_hourline.series[0].data = result.series[0].data;
            hourLine.setOption(option_hourline);
        }
    })

    evalRadar = echarts.init(document.getElementById('eval_radar'));
    $.ajax({
        url: '/pred/eval/radar',
        type: 'POST',
        async: true,
        data: s_data,
        dataType: 'json',
        success: function (option) {
            evalRadar.setOption(option);
        }
    })
    /*------------------------------------------------*/

}
//更新当日总体客流信息
function change_dayinfomation(data)
{
    var day_flow = document.querySelector("#day_flow");
    var yesstate = document.querySelector("#yesstate");
    var yesper = document.querySelector("#yesper");
    var monthstate = document.querySelector("#monthstate");
    var monthper = document.querySelector("#monthper");
    var yearstate = document.querySelector("#yearstate");
    var yearper = document.querySelector("#yearper");

    day_flow.innerHTML = data.day_flow;
    if(data.cmp_day<0) {
        yesstate.innerHTML = '&#xe607;';
        yesstate.style.color = 'red';
        yesper.innerHTML = -data.cmp_day + '%';
    }
    else {
        yesstate.innerHTML = '&#xe608';
        yesstate.style.color = '#1296DB';
        yesper.innerHTML = data.cmp_day + '%';
    }

    if(data.cmp_month<0) {
        monthstate.innerHTML = '&#xe607;';
        monthstate.style.color = 'red';
        monthper.innerHTML = -data.cmp_month + '%';
    }
    else {
        monthstate.innerHTML = '&#xe608';
        monthstate.style.color = '#1296DB';
        monthper.innerHTML = data.cmp_month + '%';
    }

    if(data.cmp_year<0) {
        yearstate.innerHTML = '&#xe607;';
        yearstate.style.color = 'red';
        yearper.innerHTML = -data.cmp_year + '%';
    }
    else {
        yearstate.innerHTML = '&#xe608';
        yearstate.style.color = '#1296DB';
        yearper.innerHTML = data.cmp_year + '%';
    }
    
    var am_peak = document.querySelector("#am_peak");
    var pm_peak = document.querySelector("#pm_peak");
    am_peak.innerHTML = data.am_peak_flow;
    pm_peak.innerHTML = data.pm_peak_flow;

    var peakper = document.querySelector("#peakper");
    peakper.innerHTML = data.peak_hour_rate + '%';
    var rate = data.peak_hour_rate + '%';
    element.progress('peakrate', rate);
}

//进出站和上行下行改变的代码写这儿
function inout_s()
{
    s_data = JSON.stringify(data_b);
    console.log(s_data);

    /*------------------echarts-----------------------*/
    //初始化图表
    graphChart = echarts.init(document.getElementById('graph'));
    $.ajax({
        type: "POST",
        data: s_data,
        url: 'pred/route_map',
        dataType: 'json',
        async: true,
        success: function (result) {  
            stations = getJsonData('/api/sta/json');

            if(data_b['graphtaggle'] == 0){
                var hourFlowData = getHourFlowData(result, stations);
                if(parseInt(data_b['inout_s']) == 0){
                    graphOption = setGraphOptions(graphOption, hourFlowData, "入站");
                }
                else{
                    graphOption = setGraphOptions(graphOption, hourFlowData, "出站");
                }
                graphChart.setOption(graphOption);
            }
            else{
                var sectionFlowData = getSectionGraphData(stations, links, result);
                sectionGraphOption = setSectionGraphOptions(sectionGraphOption, sectionFlowData);
                graphChart.setOption(sectionGraphOption);
            }
            
        }
    });
    /*------------------------------------------------*/
}

//用户选择控件tailai
var apply = document.querySelector("#apply");
apply.addEventListener('click',function(){
    data_b['alg'] = alg;

    console.log(choose_wea, choose_temp)
    console.log(data_b['choose_wea'],  data_b['choose_temp'])

    data_b['choose_wea'] = choose_wea;
    data_b['choose_temp'] = choose_temp;
    
    change_data();
    flag = 1;
})
//获取select值
layui.use('form', function(){
    form = layui.form;
    
    //各种基于事件的操作，下面会有进一步介绍
    form.on('select(model)', function(data){
    // console.log(data.value); //得到被选中的值
        alg = data.value;
    }); 
    form.on('select(wea)', function(data){
        // console.log(data.value); //得到被选中的值
        choose_wea = data.value;
    }); 
});

//获取输入温度
layui.use('slider', function(){
    var slider = layui.slider;
    
    //渲染
    temp_slider = slider.render({
      elem: '#T'  //绑定元素
      ,theme: '#3196ff'
      ,max:42
      ,min:-5
      ,value:20
      ,input:true
    //   ,range:true
      ,setTips: function(value){ //自定义提示文本
        return value + '℃';
        }
      ,change: function(value){
        // console.log(value) //动态获取滑块数值
        //do something
        choose_temp = value;
        // flag = 1;
      }
    });
  });

// layui.use('form', function(){
//     var form = layui.form;
//     //各种基于事件的操作，下面会有进一步介绍
//     form.on('radio', function(data){
//         data_b['inout_s'] = data.value;
//         // console.log(data_b);
//         inout_s();
//     }); 
// });
// <!-- <div class="layui-form-item bug1">
//                         <!-- <label class="layui-form-label">客流方向</label> -->
//                         <!-- <div class="layui-input-block m-radio bug2">
//                         <input type="radio" name="sex" value="0" title='入站' id='btnin'>
//                         <input type="radio" name="sex" value="1" title="出站" id='btnout' checked>
//                         </div>
//                     </div>
//                     --> -->

//获取自定义tab
var tabsta = document.querySelector("#tabsta");
var tabcut = document.querySelector("#tabcut");

var tabin = document.querySelector("#tabin");
var tabout = document.querySelector("#tabout");
tabsta.addEventListener('click',function()
{
    if(data_b['graphtaggle']==1)
    {
        data_b['graphtaggle'] = 0;
        tabsta.style.backgroundColor = '#6EBACC';
        tabcut.style.backgroundColor = '#fff';
        tabin.innerHTML = '入站';
        tabout.innerHTML = '出站';
        inout_s();
    }
})
tabcut.addEventListener('click',function()
{
    if(data_b['graphtaggle']==0)
    {
        data_b['graphtaggle'] = 1;
        tabsta.style.backgroundColor = '#fff';
        tabcut.style.backgroundColor = '#6EBACC';
        tabin.innerHTML = '上行';
        tabout.innerHTML = '下行';
        inout_s();
    }
})

tabin.addEventListener('click',function()
{
    if(data_b['inout_s']==1)
    {
        data_b['inout_s']=0;
        tabin.style.backgroundColor = '#5FB878';
        tabout.style.backgroundColor = '#fff';
        inout_s();
    }
})
tabout.addEventListener('click',function()
{
    if(data_b['inout_s']==0)
    {
        data_b['inout_s']=1;
        tabin.style.backgroundColor = '#fff';
        tabout.style.backgroundColor = '#5FB878';
        inout_s();
    }
})


//日历控件
layui.use('laydate', function(){
    var laydate = layui.laydate;
    
    //执行一个laydate实例
    laydate.render({
        elem: '#timectrlpre'
        ,position: 'static'
        ,value: '2020-07-17'
        ,showBottom: false
        ,min: '2020-07-17'
        ,max: '2020-10-16'
        ,ready:function(date){//初始化
            change_data();
        }
        ,change:function(value, date){
            data_b['c_date'] = value;
            change_data();            
        }
    });
});

var element;
layui.use('element', function(){
    element = layui.element;
});

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

//评分图设置项
var markpreOption = {
    series: [{
        type: 'gauge',
        axisLine: {
            lineStyle: {
                width: 20,
                color: [
                    [0.2, '#67e0e3'],
                    [0.8, '#37a2da'],
                    [1, '#fd666d']
                ]
            }
        },
        pointer: {
            itemStyle: {
                color: 'auto'
            }
        },
        axisTick: {
            distance: -20,
            length: 8,
            lineStyle: {
                color: '#fff',
                width: 2
            }
        },
        splitLine: {
            distance: -20,
            length: 30,
            lineStyle: {
                color: '#fff',
                width: 4
            }
        },
        axisLabel: {
            color: 'auto',
            distance: 20,
            fontSize: 10
        },
        detail: {
            valueAnimation: true,
            formatter: '{value} 分',
            color: 'auto',
            fontSize: 25
        },
        data: [{
            value: 85
        }]
    }]
};


var stations;
var links = getJsonData('/api/link/json');
    
//获取线路名称列表
var lineNames = ['1号线', '2号线', '3号线', '4号线', '5号线', '10号线', '11号线', '12号线'];

//图例的数据数组 数组中的每一项代表一个系列的name
var legend = [{ data: lineNames, orient: 'vertical', top: '20%', right: '2%'  }];

//获取类目名称数组 用于和 legend 对应以及格式化 tooltip 的内容
var categories = lineNames.map(lineName => { return { name: lineName } });

var alertStations = [];

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
            if (param.value) {
                label = `站点名称: ${param.name} <br> 站点客流: ${param.value[2]}人`;
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

//配置图表属性
function setGraphOptions(option, hourFlowData, type) {
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
    return option;
}

//生成6-21点的客流数据
function getHourFlowData(hourFlow, stations) {
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
    return hourFlowList;
}

//断面客流图表
var sectionGraphOption = {
    timeline: {
        axisType: 'category',
        show: true,
        autoPlay: false,
        playInterval: 1000,
        padding: [0, 150, 0, 150],
        data: ['7-9时段', '16-18时段']
    },
    title: {
        text: '早晚时段断面客流'
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
            console.log(param);
            let label = "";
            if (param.dataType == 'edge') {
                label = `线路断面: ${param.name} <br> 断面客流: ${param.value}人次`;
            }
            else if(param.dataType == 'node'){
                label = `站点名称: ${param.name}`;
            }

            return label;
        }
    },
    visualMap: {
        min: 0,
        max: 300,
        calculable: true,
        text: ['High', 'Low'],
        inRange: {
            color: ['#23c768', '#FDD56A', '#fe0000']

        },
        padding: 5,
        right: "5%",
        bottom: "20%",
        textStyle: {
            color: '#808A87'
        }
    },
    // legend: legend,
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
            label: {
                normal: {
                    show: false,
                }
            },
            lineStyle: {
                normal: {
                    opacity: 0.7, //线条透明度
                    curveness: 0, //站点间连线曲度，0表示直线
                    width: 4, //线条宽度
                }
            }
        },
    ],
    options: []
}

//配置图表属性
function setSectionGraphOptions(option, sectionFlowData) {
    option.options = [];
    var text_list = ['7:00-10:00时', '16:00-19:00时'];
    for (let i = 0; i <= 1; i++){ 
        option.options.push({
            title: {
                text: text_list[i] + '断面客流分布情况',
                textStyle: {
                    color: 'black',
                    fontSize: 20
                },
                x: 'center',
                top: 10
            },
            series: [{
                    type: "graph",
                    data: sectionFlowData['station'][i].staList,
                    links: sectionFlowData['section'][i].linkList,
                },
            ]
        },
        
        )    
    }
    return option;
}

function getSectionGraphData(stations, links, sectionFlow) {
    var hourList = ['7', '16'];
    var staHourList = [];

    for (let i = 0; i <= 1; i++) {
        var hourObj = {};
        hourObj.staList = [];
        stations.forEach(function (station) {
            var staName = station.name;
            var sta = JSON.parse(JSON.stringify(station));

            if (lineNames.indexOf(sta.name) == -1) {
                sta.label.show = false 
                sta.itemStyle.color = '#fff';
                sta.itemStyle.borderColor = '#fff';
                sta.itemStyle.show=false;
                sta.symbolSize = [2, 2];  
            } 
            hourObj.staList.push(sta);
        });
        staHourList.push(hourObj);
    }
    
    var sectionHourList = [{}, {}];
    for(let j = 0; j <= 1; j++){
        sectionHourList[j].linkList = [];
        links.forEach(function (link){
            var sectionItem =JSON.parse(JSON.stringify(link));;
            var target = sectionItem.target;
            var source = sectionItem.source;
            var section = source + '-' + target;
            var revsection = target + '-' + source;
            
            var flow = 0;
            if(sectionFlow[hourList[j]][section]){
                flow = sectionFlow[hourList[j]][section];
            }
            else if(sectionFlow[hourList[j]][revsection]){
                flow = sectionFlow[hourList[j]][revsection];
            }

            sectionItem.value = flow;
            if(flow >= 0 && flow < 50){
                sectionItem.lineStyle.normal.color = '#23c768';
            }
            else if(flow >= 50 && flow < 100){
                sectionItem.lineStyle.normal.color = '#99ff4d';
            }
            else if(flow >= 100 && flow < 150){
                sectionItem.lineStyle.normal.color = '#FDD56A';
            }
            else if(flow >= 150 && flow < 200){
                sectionItem.lineStyle.normal.color = '#ff7e00';
            }
            else if(flow >= 200){
                sectionItem.lineStyle.normal.color = '#fe0000';
            }
       
            sectionHourList[j].linkList.push(sectionItem);
        })
    } 

    return {'station': staHourList, 'section': sectionHourList};

}


//单月客流选项
var option_monthline = {
    title: {
        text: '本月客流波动预测',
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
        // axisLine: {
        //     show:true,
        //     symbol:['none', 'arrow'],
        //     symbolSize:[5,10]
        // }
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
            // markLine: {
            //     symbol: 'none',
            //     data: [
            //         {
            //             type: 'average', 
            //             name: '平均值'
                
            //         }
            //     ],
            //     label: {
            //         show:true,
            //         formatter: '平均值:{c}',
            //         position:'insideEndTop'
            //     }
            // },
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

//小时客流分布预测选项
option_hourline = {
    title: {
        text: '当日小时客流变化预测',
        left: 'center',
        textStyle: {
            fontWeight: 400
        }
    },
    tooltip: {
        trigger: 'axis'
    },
    grid: {
        left: '2%',
        right: '5%',
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
        name: '时',
        data: [],
        axisLine: {
            show:true,
            symbol:['none', 'arrow'],
            symbolSize:[5,10]
        }
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
            markPoint: {
                data: [
                    {type: 'max', name: '最大值'}
                ]
            },
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
            smooth: true,
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
            // areaStyle: { }
        }
    ]
};


var lowLevelMeasures = [
    "采取出入口人员提醒、广播疏导客流、警示牌及警戒线导流等现场疏散措施。",
    "视情况对客流进行限量进入。",
    "开启部分备用通道，疏散客流。",
    "加派安全员现场疏导客流和维护秩序。",
    "加强对站台乘客候车动态及站台屏蔽门工作状态的监控"
];

var highLevelMeasures = [
    "车站应立即组织力量，在事件初期迅速出动，准确施救，控制事态，减少损失。",
    "车站做好临时导向标志、告示牌、临时售票亭等客运设施的准备、设置工作。",
    "紧急情况下各站出入口开、关，各站根据各自的客流特点安排。",
    "接到车站突发大客流报告后，行车调度应对该站进行重点监控，根据实际情况适当延长列车在该站的停站时间，尽快疏运车站客流。",
    "调度部应根据实际情况及时组织备用车上线投入运营，缓解车站客流压力。",
    "客流较多，造成列车在多个车站连续出现延长停站时间的情况时，行车调度根据现场实际情况及时对行车进行调整，减少对乘客的影响。",
    "遇突发大客流，必要时指挥机构总指挥有权下达临时封站命令。"
];

//从数组中随机选择num个元素
function makeRandomArr(arrList, num){
    if(num > arrList.length){
       return;
    }
    
    var tempArr = arrList.slice(0);
    var newArrList = [];    
    for(var i = 0; i < num; i++){
        var random = Math.floor(Math.random() * (tempArr.length - 1));
        var arr = tempArr[random];
        tempArr.splice(random, 1);
        newArrList.push(arr);    
    }
    return newArrList;
}