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
        url: '/pred/day/eval',
        type: 'POST',
        data: s_data,
        dataType: 'json',
        async: true,
        success: function (data) {
            markpreOption.series[0].data[0].value = data['eval'];
            markgraph.setOption(markpreOption);
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
        url: '/pred/day/info',
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
        success: function (option) {
            monthLine.setOption(option);
        }
    })

    weekLine = echarts.init(document.getElementById('week_line'));
    $.ajax({
        url: '/pred/week/line',
        type: 'POST',
        async: true,
        data: s_data,
        dataType: 'json',
        success: function (option) {
            weekLine.setOption(option);
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
        success: function (option) {
            hourLine.setOption(option);
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

//进出站改变的代码写这儿
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
        url: 'pred/hour_flow',
        dataType: 'json',
        async: true,
        success: function (result) {
            var hourFlow = result;
            console.log(result);
            stations = getJsonData('/api/sta/json')
            var hourFlowData = getHourFlowData(hourFlow, stations);
            graphOption = setGraphOptions(graphOption, hourFlowData);
            graphChart.setOption(graphOption);
        }
    });
    /*------------------------------------------------*/
}

//用户选择控件
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
function setGraphOptions(option, hourFlowData, type = "出站") {
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