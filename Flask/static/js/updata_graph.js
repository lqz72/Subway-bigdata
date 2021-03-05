var d = new DateJs({
    inputEl: '#inputdate',
    el: '#date'
})
console.log(d);
console.log(d.choiceDate.date);
//初始化代码写这儿
$(
    function(){
        var month_chart = echarts.init(document.getElementById('month_line'), 'white', {renderer: 'canvas'});
        $.ajax({
            type: 'POST',
            data: JSON.stringify(d.choiceDate.date),
            async: false,
            url: 'history/day_flow/line',
            dataType: 'json',
            success: function (result) {
                month_chart.setOption(result);
            }
        });

        var week_chart = echarts.init(document.getElementById('curr_week_line'), 'white', {renderer: 'canvas'});
        $.ajax({
            type: "POST",
            data: JSON.stringify(d.choiceDate.date),
            async : false,
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
            data: JSON.stringify(d.choiceDate.date),
            async: false,
            url: '/other_info',
            dataType: 'json',
            success: function (result) {
                console.log(result);
                weather_info.innerHTML = result.weather;
                is_hoilday.innerHTML = result.is_hoilday;
                day_flow.innerHTML = result.day_flow;
            }
        });

    },

)


var bt = document.querySelectorAll('.bts>.bt')[1];
console.log(bt);
bt.addEventListener('click',function(){

    console.log(d.choiceDate);
    console.log((d.choiceDate.date));
    console.log(JSON.stringify(d.choiceDate.date))

    var month_chart = echarts.init(document.getElementById('month_line'), 'white', {renderer: 'canvas'});
    $.ajax({
        type: 'POST',
        data: JSON.stringify(d.choiceDate.date),
        async: false,
        url: 'history/day_flow/line',
        dataType: 'json',
        success: function (result) {
            month_chart.setOption(result);
        }
    });

    var week_chart = echarts.init(document.getElementById('curr_week_line'), 'white', {renderer: 'canvas'});
    $.ajax({
        type: "POST",
        data: JSON.stringify(d.choiceDate.date),
        async : false,
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
        data: JSON.stringify(d.choiceDate.date),
        async: false,
        url: '/other_info',
        dataType: 'json',
        success: function (result) {
            console.log(result);
            weather_info.innerHTML = result.weather;
            is_hoilday.innerHTML = result.is_hoilday;
            day_flow.innerHTML = result.day_flow;
        }
    });

  
});