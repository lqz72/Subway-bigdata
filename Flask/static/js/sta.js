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
            var markgraph = echarts.init(document.querySelector("#marksta"));
            markgraph.setOption(option_marksta);

        }
        ,change:function(value, date){//修改日历

        }
    });
});
var option_marksta = {
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