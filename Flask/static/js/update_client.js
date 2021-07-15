// 点击详细信息
var btn1 = document.querySelector('#btn_show');
btn1.addEventListener('click',
function()
{
    location.href = '/userinf';
})

//点击搜索后
var btn_search = document.getElementById('btn_search');
var user_id = document.getElementById('user_search');
var userRecord;
btn_search.onclick = function () {
    //更改三条基本信息
    $.ajax({
        url: '/user_info',
        type: 'POST',
        data: user_id.value,
        dataType: 'json',
        async: true,
        success: function(result){
            var id = document.getElementById('id');
            var age = document.getElementById('age');
            var trips_num = document.getElementById('trips_num');
            var im = document.querySelector('#user_img');
            im.innerHTML = getCate(result.category).img;
            id.innerHTML = result.id;
            age.innerHTML = result.age;
            trips_num.innerHTML = getCate(result.category).name;
        }
    });

    //更改右侧出行信息图表
    var user_flow_line = echarts.init(document.getElementById('monthout'));
    $.ajax({
        type: 'POST',
        url: '/history/user_flow/line',
        data: user_id.value,
        dataType: 'json',
        async: true,
        success: function (result) {
            user_flow_line.setOption(result);
        }
    });

    //出行记录展示
    $.ajax({
        type:'POST',
        url:'/user_record',
        data: user_id.value,
        async: true,
        success: function(data)
        {
            userRecord = data.reverse();
            test = {title:'用户记录'};
            test['list'] = userRecord;
            test['length'] = data.length;
            var html = template('historyshow', test);
            document.getElementById('outshow1').innerHTML = html;

            var html2 = template('historylist', test);
            document.getElementById('outshow2').innerHTML = html2;

            linesOption.series[1].data = getLinesData(userRecord, stations);
            linesChart.setOption(linesOption);
        }
    });
}

//顶上俩表
var age_bar = echarts.init(document.getElementById('age_bar'));
var age_pie = echarts.init(document.getElementById('age_pie'));

$.ajax({
    type: 'POST',
    url: 'history/age/pie',
    dataType: 'json',
    success: function (result) {
        age_pie.setOption(result);
    }
});

$.ajax({
    type: 'POST',
    url: 'history/age/bar',
    dataType: 'json',
    success: function (result) {
        age_bar.setOption(result);
    }
});

//默认显示
var init_id = "d4ec5a712f2b24ce226970a8d315dfce";
$.ajax({
    url: '/user_info',
    type: 'POST',
    data: init_id,
    dataType: 'json',
    success: function(result){
        var id = document.getElementById('id');
        var age = document.getElementById('age');
        var trips_num = document.getElementById('trips_num');
        var im = document.querySelector('#user_img');
        im.innerHTML = getCate(result.category).img;
        id.innerHTML = result.id;
        age.innerHTML = result.age;
        trips_num.innerHTML = getCate(result.category).name;
    }
});

var user_flow_line = echarts.init(document.getElementById('monthout'));

$.ajax({
    type: 'POST',
    url: '/history/user_flow/line',
    data: init_id,
    dataType: 'json',
    success: function (result) {        
        user_flow_line.setOption(result);
    }
});

$.ajax({
    type:'post',
    url: '/user_record',
    async: false,
    data: init_id,
    success: function(data)
    {
        orgin_data = data;
        userRecord = data.reverse();
        test = {title:'用户记录'};
        test['list'] = data;
        test['length'] = data.length;
        var html = template('historyshow', test);
        document.getElementById('outshow1').innerHTML = html;

        var html2 = template('historylist', test);
        document.getElementById('outshow2').innerHTML = html2;
        
        linesOption.series[1].data = getLinesData(userRecord, stations);
        linesChart.setOption(linesOption);
    }
});

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

var stations = getJsonData('/sta/json');
var links = getJsonData('/link/json');

//初始化图表
var linesChart = echarts.init(document.getElementById('road'));

//获取线路名称列表
var lineNames = ['1号线', '2号线', '3号线', '4号线', '5号线', '10号线', '11号线', '12号线'];

//图例的数据数组 数组中的每一项代表一个系列的name
var legend = [{ data: lineNames, orient: 'vertical', top: '20%', right: '2%'  }];

//获取类目名称数组 用于和 legend 对应以及格式化 tooltip 的内容
var categories = lineNames.map(lineName => { return { name: lineName } });

var linesOption = {
    title: {
        text: '用户出行轨迹'
    },
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
            data: stations,
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
        {
            type: 'lines',
            zlevel: 5,
            draggable: false,
            coordinateSystem: "cartesian2d", //使用二维的直角坐标系（也称笛卡尔坐标系）
            effect: {
                show: true,
                period: 4, //箭头指向速度，值越小速度越快
                trailLength: 0.02, //特效尾迹长度[0,1]值越大，尾迹越长重
                symbol: 'arrow', //箭头图标
                symbolSize: 5, //图标大小
            },
            lineStyle: {
                normal: {
                    width: 1, //尾迹线条宽度
                    opacity: 1, //尾迹线条透明度
                    curveness: .3 //尾迹线条曲直度
                }
            },
            data:[],
        }
    ],
}

function getLinesData(userRecord, stations) {
    var coordsList = [];
    var len = userRecord.length;
    for (let i = 0; i < len; i++){
        var source = userRecord[i][0];
        var target = userRecord[i][2];
        var data = { coords: [0, 0], lineStyle: {color: ""}};
        for (let j = 0; j < stations.length; j++){
            if (stations[j].category == 1)
                continue;
            if (source == stations[j].name) {
                data.coords[0] = stations[j].value;
                data.lineStyle.color = stations[j].itemStyle.borderColor;
            }
            else if (target == stations[j].name) {
                data.coords[1] = stations[j].value;
            }
        }  
        coordsList.push(data);
    }
    return coordsList;
}

linesOption.series[1].data = getLinesData(userRecord, stations);
linesChart.setOption(linesOption);

//获取分类信息 
function getCate(x)
{
    var inf = {};
    if(x==1){
        inf['name'] = '上班族';
        inf['img'] = '&#xe629;';
    }
    else if(x==2){
        inf['name'] = '剁手党';
        inf['img'] = '&#xe657;';
    }
    else if(x==3){
        inf['name'] = '驴友';
        inf['img'] = '&#xe7cb;';
    }
    else if(x==4){
        inf['name'] = '学生党';
        inf['img'] = '&#xe61c;';
    }
    else if(x==5){
        inf['name'] = '远距离通勤者';
        inf['img'] = '&#xe603;';
    }
    else if(x==6){
        inf['name'] = '夜猫子';
        inf['img'] = '&#xe721;';
    }
    return inf;
}