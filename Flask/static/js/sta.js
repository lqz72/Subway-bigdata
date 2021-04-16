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
            var markgraph = echarts.init(document.querySelector("#markpre"));
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

// ---------词云
var chart = echarts.init(document.getElementById('wordclouds'));

      var option = {
          tooltip: {},
          series: [ {
              type: 'wordCloud',
              gridSize: 2,
              sizeRange: [6, 30],
              // sizeRange: [12, 50],
              rotationRange: [-90, 90],
              shape: 'pentagon',
              width: 226,
              height: 190,
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
                          color: 'black'
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