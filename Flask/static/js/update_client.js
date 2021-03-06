$(
    function chart() {
        var age_bar = echarts.init(document.getElementById('age_bar'));
        var age_pie = echarts.init(document.getElementById('age_pie'));

        $.ajax({
            type: 'POST',
            url: 'history/age/pie',
            async: false,
            dataType: 'json',
            success: function (result) {
                age_pie.setOption(result);
            }
        });

        $.ajax({
            type: 'POST',
            url: 'history/age/bar',
            async: false,
            dataType: 'json',
            success: function (result) {
                age_bar.setOption(result);
            }
        });

        var user_id = "d4ec5a712f2b24ce226970a8d315dfce"
        $.ajax({
            url: '/user_info',
            type: 'POST',
            data: user_id,
            dataType: 'json',
            success: function(result){
                console.log(result)
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
            data: user_id,
            dataType: 'json',
            success: function (result) {        
                user_flow_line.setOption(result);
            }
        });

    },

    

)