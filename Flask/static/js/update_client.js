$(function(){
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
    btn_search.onclick = function(){
        $.ajax({
            url: '/user_info',
            type: 'POST',
            data: user_id.value,
            dataType: 'json',
            success: function(result){
                var id = document.getElementById('id');
                var age = document.getElementById('age');
                var trips_num = document.getElementById('trips_num');
                id.innerHTML = result.id;
                age.innerHTML = result.age;
                trips_num.innerHTML = result.trips_num;
            }
        });

        var user_flow_line = echarts.init(document.getElementById('monthout'));
        $.ajax({
            type: 'POST',
            url: '/history/user_flow/line',
            data: user_id.value,
            dataType: 'json',
            success: function (result) {        
                user_flow_line.setOption(result);
            }
        });

        //出行记录展示
        $.ajax({
            type:'post',
            url:'/user_record',
            data: user_id.value,
            success: function(data)
            {
                test = {title:'用户记录'};
                test['list'] = data.reverse();
                test['length'] = data.length;
                console.log(test);
                var html = template('historyshow', test);
                document.getElementById('outshow1').innerHTML = html;

                var html2 = template('historylist', test);
                document.getElementById('outshow2').innerHTML = html2;
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
            // console.log(result);
            var id = document.getElementById('id');
            var age = document.getElementById('age');
            var trips_num = document.getElementById('trips_num');
            id.innerHTML = result.id;
            age.innerHTML = result.age;
            trips_num.innerHTML = result.trips_num;
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
        url:'/user_record',
        data: init_id,
        success: function(data)
        {
            test = {title:'用户记录'};
            test['list'] = data.reverse();
            test['length'] = data.length;
            var html = template('historyshow', test);
            document.getElementById('outshow1').innerHTML = html;

            var html2 = template('historylist', test);
            document.getElementById('outshow2').innerHTML = html2;
        }
    });
}
)