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
    week_line.resize();
    hour_line.resize();
    age_pie.resize();
    schedule_line.resize();
    aixin_bar.resize();
});
var state = 0;//表示未折叠
var week_line;
var hour_line;
var age_pie;
var schedule_line;
var aixin_bar;

var c_date = '2020-01-01';
var c_staname = document.getElementById('sta_name').innerText;
function change_data()
{
    var s_date = JSON.stringify(c_date);//得到的字符串
    //评分图
    var markgraph = echarts.init(document.querySelector("#markpre"));
    markgraph.setOption(markOption);

    $.ajax({
        url: '/sta/curr_day_eval',
        type: 'POST',
        data: JSON.stringify({date: c_date, sta: c_staname}),
        dataType: 'json',
        async: true,
        success: function (data) {
            markOption.series[0].data[0].value = data['score'];
            markgraph.setOption(markOption);
        }
    });
    // console.log(s_date)
    // console.log(c_staname);
    //向后端传取数据代码写这儿------------------------------------
    var day_cmp = document.getElementById('day_cmp');
    var month_cmp = document.getElementById('month_cmp');
    var year_cmp = document.getElementById('year_cmp');
    var am_peak_flow = document.getElementById('am_peak_flow');
    var pm_peak_flow = document.getElementById('pm_peak_flow');
    $.ajax({
        type: 'POST',
        data: JSON.stringify({date: c_date, sta: c_staname}),
        url: '/sta/thisday_info',
        dataType: 'json',
        success: function (result) {
            day_cmp.innerHTML = result.day_cmp + '%';
            month_cmp.innerHTML = result.month_cmp + '%';
            year_cmp.innerHTML = result.year_cmp + '%';
            am_peak_flow.innerHTML = result.am_peak_flow;
            pm_peak_flow.innerHTML = result.pm_peak_flow;
        }
    });

    week_line = echarts.init(document.getElementById('week_flow'));
    $.ajax({
        type: 'POST',
        url: '/sta/curr_week_flow',
        data:  JSON.stringify({date: c_date, sta: c_staname}),
        dataType: 'json',
        success: function (result) {
            var in_flow = [];
            var out_flow = [];
            for (let each in result) {
                in_flow.push(parseInt(result[each][0]));
                out_flow.push(parseInt(result[each][1]));
            }
            week_line_opts.series[0].data = in_flow;
            week_line_opts.series[1].data = out_flow;
            week_line.setOption(week_line_opts);
        }
    })
    
    hour_line = echarts.init(document.getElementById('hour_flow'));
    $.ajax({
        type: 'POST',
        url: '/sta/curr_day_flow',
        data:  JSON.stringify({date: c_date, sta: c_staname}),
        dataType: 'json',
        success: function (result) {
            console.log(result);
            var hour_list = Object.keys(result);
            var in_flow = [];
            var out_flow = [];
            
            for (hour in result) {
                in_flow.push(parseInt(result[hour][0]));
                out_flow.push(parseInt(result[hour][1]));
            }
            hour_line_opts.xAxis.data = hour_list;
            hour_line_opts.series[0].data = in_flow;
            hour_line_opts.series[1].data = out_flow;
            hour_line.setOption(hour_line_opts);
        }
    })
    
    age_pie = echarts.init(document.getElementById('age_structure'));
    $.ajax({
        type: 'POST',
        url: '/sta/age/pie',
        data:  JSON.stringify({date: c_date, sta: c_staname}),
        dataType: 'json',
        success: function (result) {
            age_pie.setOption(result);
        }
    })

    schedule_line = echarts.init(document.getElementById('schedule'));
    $.ajax({
        type: 'POST',
        url: '/sta/schedule/line',
        data:  JSON.stringify({date: c_date, sta: c_staname}),
        dataType: 'json',
        success: function (result) {
            schedule_line.setOption(result);
        }
    })

    aixin_bar = echarts.init(document.getElementById('aixin'));
    aixin_bar.setOption(aixin_bar_opts);
}


layui.use('laydate', function(){
    var laydate = layui.laydate;
    //执行一个laydate实例
    laydate.render({
        elem: '#timectrlsta'
        ,position: 'static'
        ,value: '2020-01-01'
        ,showBottom: false
        ,min: '2019-12-22'
        ,max: '2020-07-15'
        ,ready:function(date){//初始化
            change_data();
        }
        ,change:function(value, date){//修改日历
            c_date = value;
            change_data();
        }
    });
});

//使用进度条
layui.use('element', function(){
    var element = layui.element;
  });

// ---------词云
var chart = echarts.init(document.getElementById('wordclouds'));
var option = {
    tooltip: {},
    series: [ {
        type: 'wordCloud',
        gridSize: 2,
        sizeRange: [15, 45],
        // sizeRange: [12, 50],
        rotationRange: [-30,30],
        shape: 'pentagon',
        width: 456,
        height: 220,
        drawOutOfBound: true,
        textStyle: {
            color: function () {
                return 'rgb(' + [
                    Math.round(Math.random() * 160),
                    Math.round(Math.random() * 160),
                    Math.round(Math.random() * 160)
                ].join(',') + ')';
            }
        },
        emphasis: {
            textStyle: {
                shadowBlur: 10,
                shadowColor: '#333'
            }
        },
        data: [
            {
                name: '通勤乘客',
                value: 10000,
                textStyle: {
                    color: 'red'
                },
                emphasis: {
                    textStyle: {
                        color: 'red'
                    }
                }
            },
            {
            name:"剁手党",
            value: 9100
            },
            {
            name:"购物达人",
            value: 3200
            },
            {
            name:"驴友",
            value: 8100
            },
            {
            name:"学生党",
            value: 6000
            },
            {
            name:"远距通勤者",
            value: 5100
            },
            {
            name:"夜行人",
            value: 3100
            },
            {
            name:"学生",
            value: 3100
            },
            {
            name:"女性用户",
            value: 2500
            },
            {
            name:"夜猫子",
            value: 2000
            },
            {
            name:"shopping族",
            value: 3100
            },
            {
            name:"高龄乘客",
            value: 1800
            },
            {
            name:"行动不便者",
            value: 1200
            }
        ]
    } ]
};
chart.setOption(option);

//选项和函数全部写这儿------------------------------------

//评分选项
var markOption = {
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
            value: 70
        }]
    }]
};

//站点本周客流波动
var week_line_opts =  {
    backgroundColor: '#fff',
    title: {
        text: '本周进出站客流分布',
        left: "center",
        // textStyle: {
        //     color: '#999',
        //     fontSize: 14
        // }
    },
    grid: [{bottom: "10%"}],
    legend: {
        show: true,
        icon: 'circle',
        top: '10%',
        itemWidth: 10,
        itemHeight: 10,
        itemGap: 25,
    },
    tooltip: {
        trigger: 'axis'
    },
    xAxis: [{
        type: 'category',
        data:  ['周一', '周二', '周三', '周四', '周五', '周六', '周末'],
        boundaryGap: false
    }],
    yAxis: [{
        name: '客流/人次',
        type: 'value',
        splitLine: {
            show: true
        }
    }],
    series: [{
        name: '进站',
        type: 'line',
        data: [],
        symbolSize: 6,
        symbol: 'circle',
        stack: '1',
        lineStyle: {
            color: '#fe9a8b'
        },
        itemStyle: {
            normal: {
                color: '#fe9a8b',
                borderColor: '#fe9a8b'
            }
        },
        areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                        offset: 0,
                        color: '#fe9a8bb3'
                    },
                    {
                        offset: 1,
                        color: '#fe9a8b03'
                    }
                ])
        },
        emphasis: {
            itemStyle: {
                color: {
                        type: 'radial',
                        x: 0.5,
                        y: 0.5,
                        r: 0.5,
                        colorStops: [{
                                offset: 0,
                                color: '#fe9a8b'
                            },
                            {
                                offset: 0.4,
                                color: '#fe9a8b'
                            },
                            {
                                offset: 0.5,
                                color: '#fff'
                            }, {
                                offset: 0.7,
                                color: '#fff'
                            }, {
                                offset: 0.8,
                                color: '#fff'
                            }, {
                                offset: 1,
                                color: '#fff'
                            }
                        ]
                    },
                    borderColor: '#fe9a8b',
                    borderWidth: 2
            }
        }
    },{
        name: '出站',
        type: 'line',
        data: [],
        symbolSize: 6,
        symbol: 'circle',
        stack:'1',
        lineStyle: {
            color: '#9E87FF'
        },
        itemStyle: {
            normal: {
                color: '#9E87FF',
                borderColor: '#9E87FF'
            }
        },
        areaStyle: {
            color: '#9E87FFb3'
        },
        emphasis: {
            itemStyle: {
                color: {
                        type: 'radial',
                        x: 0.5,
                        y: 0.5,
                        r: 0.5,
                        colorStops: [{
                                offset: 0,
                                color: '#9E87FF'
                            },
                            {
                                offset: 0.4,
                                color: '#9E87FF'
                            },
                            {
                                offset: 0.5,
                                color: '#fff'
                            }, {
                                offset: 0.7,
                                color: '#fff'
                            }, {
                                offset: 0.8,
                                color: '#fff'
                            }, {
                                offset: 1,
                                color: '#fff'
                            }
                        ]
                    },
                    borderColor: '#9E87FF',
                    borderWidth: 2
            }
        }
    }
    ]
};

//站点当日小时客流
const colorList = ["#9E87FF", '#73DDFF', '#fe9a8b', '#F56948', '#9E87FF'];
var hour_line_opts = {
    backgroundColor: '#fff',
    title: {
        text: '本站小时客流分布',
        left: 'center',
        // top: '5%'
    },
    legend: {
        icon: 'circle',
        top: '2%',
        right: '5%',
        itemWidth: 10,
        itemGap: 20,
        textStyle: {
            color: '#556677'
        }
    },
    tooltip: {
        trigger: 'axis',
        axisPointer: {
            label: {
                show: true,
                backgroundColor: '#fff',
                color: '#556677',
                borderColor: 'rgba(0,0,0,0)',
                shadowColor: 'rgba(0,0,0,0)',
                shadowOffsetY: 0
            },
            lineStyle: {
                width: 0
            }
        },
        backgroundColor: '#fff',
        textStyle: {
            color: '#5c6c7c'
        },
        padding: [10, 10],
        extraCssText: 'box-shadow: 1px 0 2px 0 rgba(163,163,163,0.5)'
    },
    grid: {
        bottom: '10%'
    },
    xAxis: [{
        name: "时间/时",
        type: 'category',
        data: ["6","7","8","9","10","11","12","13","14","15", "16", "17", "18", "19", "20", "21"],
        axisLine: {
            lineStyle: {
                color: '#DCE2E8'
            }
        },
        axisTick: {
            show: true
        },
        axisLabel: {
            interval: 0,
            textStyle: {
                color: '#556677'
            },
            // 默认x轴字体大小
            fontSize: 12,
            // margin:文字到x轴的距离
            margin: 15
        },
        axisPointer: {
            label: {
                padding: [0, 0, 10, 0],
                margin: 15,
                fontSize: 12,
                backgroundColor: {
                    type: 'linear',
                    x: 0,
                    y: 0,
                    x2: 0,
                    y2: 1,
                    colorStops: [{
                        offset: 0,
                        color: '#fff' // 0% 处的颜色
                    }, {
                        offset: 0.86,

                        color: '#fff' // 0% 处的颜色
                    }, {
                        offset: 0.86,
                        color: '#33c0cd' // 0% 处的颜色
                    }, {
                        offset: 1,
                        color: '#33c0cd' // 100% 处的颜色
                    }],
                    global: false // 缺省为 false
                }
            }
        },
        boundaryGap: false
    }],
    yAxis: [{
        name: "客流/人次",
        type: 'value',
        // axisTick: {
        //     show: true
        // },
        // axisLine: {
        //     show: true,
        //     lineStyle: {
        //         color: '#DCE2E8'
        //     }
        // },
        // axisLabel: {
        //     textStyle: {
        //         color: '#556677'
        //     }
        // },
        splitLine: {
            show: true
        }
    }, {
        name: "客流/人次",
        type: 'value',
        position: 'right',
        // axisTick: {
        //     show: false
        // },
        // axisLabel: {
        //     textStyle: {
        //         color: '#556677'
        //     },
        //     formatter: '{value}'
        // },
        // axisLine: {
        //     show: true,
        //     lineStyle: {
        //         color: '#DCE2E8'
        //     }
        // },
        splitLine: {
            show: true
        }
    }],
    series: [{
            name: '进站',
            type: 'line',
            data: [],
            symbolSize: 1,
            symbol: 'circle',
            smooth: true,
            yAxisIndex: 0,
            showSymbol: false,
            lineStyle: {
                width: 4,
                color: new echarts.graphic.LinearGradient(0, 1, 0, 0, [{
                        offset: 0,
                        color: '#9effff'
                    },
                    {
                        offset: 1,
                        color: '#9E87FF'
                    }
                ]),
                shadowColor: 'rgba(158,135,255, 0.3)',
                shadowBlur: 10,
                shadowOffsetY: 20
            },
            itemStyle: {
                normal: {
                    color: colorList[0],
                    borderColor: colorList[0]
                }
            }
        }, {
            name: '出站',
            type: 'line',
            data: [],
            symbolSize: 1,
            yAxisIndex: 1,
            symbol: 'circle',
            smooth: true,
            showSymbol: false,
            lineStyle: {
                width: 5,
                color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [{
                        offset: 0,
                        color: '#fe9a'
                    },
                    {
                        offset: 1,
                        color: '#fe9a8b'
                    }
                ]),
                shadowColor: 'rgba(254,154,139, 0.3)',
                shadowBlur: 10,
                shadowOffsetY: 20
            },
            itemStyle: {
                normal: {
                    color: colorList[2],
                    borderColor: colorList[2]
                }
            }
        },
     
    ]
};

var aixin_bar_opts = {
    title: {
        text: '爱心专座比例调整',
        left: 'center'
    },
    grid:[{bottom:"10%"}],
    tooltip: {
        trigger: 'axis'
    },
    calculable: true,
    xAxis: [
        {
            type: 'category',
            data: ["6","7","8","9","10","11","12","13","14","15", "16", "17", "18", "19", "20", "21"]
        }
    ],
    yAxis: [
        {
            type: 'value',
        }
    ],
    series: [
        {
            name: '百分比 %',
            type: 'bar',
            data: [2.0, 4.9, 7.0, 11.2, 12.6, 13.7, 13.6, 12.2, 12.6, 11.0, 8.4, 7.3, 5.2, 4.4, 3.5, 2.1],
            markPoint: {
                data: [
                    {type: 'max', name: '最大值'},
                    {type: 'min', name: '最小值'}
                ]
            },
            markLine: {
                data: [
                    {type: 'average', name: '平均值'}
                ]
            },
            color:['#73ACFF']
        },
    ]
};


//-----------------------模态框部分代码----------------------
(function() {
    /*建立模态框对象*/
    var modalBox = {};

    /*获取模态框*/
    modalBox.modal = document.getElementById("myModal");

    /*获得trigger按钮*/
    modalBox.triggerBtn = document.getElementById("triggerBtn");

    /*获得关闭按钮*/
    modalBox.closeBtn = document.getElementById("closeBtn");

    /*模态框显示*/
    modalBox.show = function() {
        console.log(this.modal);
        this.modal.style.display = "block";
    }

    /*模态框关闭*/
    modalBox.close = function() {
        this.modal.style.display = "none";
    }

    /*当用户点击模态框内容之外的区域，模态框也会关闭*/
    modalBox.outsideClick = function() {
        var modal = this.modal;
        window.onclick = function(event) {
            if(event.target == modal) {
                modal.style.display = "none";
            }
        }
    }

    /*模态框初始化*/
    modalBox.init = function() {
        var that = this;
        this.triggerBtn.onclick = function() {
            that.show();
        }
        this.closeBtn.onclick = function() {
            that.close();
        }
        this.outsideClick();
    }
    modalBox.init();
})();