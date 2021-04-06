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
            var markgraph = echarts.init(document.querySelector("#markpre"));
            var option = {
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
            markgraph.setOption(option);
        }
        ,change:function(value, date){

        }
    });
});