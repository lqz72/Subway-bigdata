$(function(){
    $.ajax({
        type:'GET',
        url:'/admin_info',

        success: function(data){
            var t = {};
            t.list = data;
            var html = template('admindata', t);
            document.getElementById('adminlist').innerHTML = html;

            var ad_list = document.querySelector('#adminlist').children[0];
            console.log(data.length);
            for(var i=0;i<data.length;i++)
            {
                // console.log(ad_list.children[0].children[1]);
                ad_list.children[i+1].children[3].children[0].children[0].addEventListener('click',function(){
                    console.log(this.parentNode.parentNode.parentNode.children[0].innerText);
                })
            }
        }
    })

    var save = document.querySelector('#saveitem');
    
    save.addEventListener('click',function(){
        var username = document.querySelector('#username');
        var pwd = document.querySelector('#pwd');
        var tips = document.querySelector('#tips');
        var inf = {};
        inf.username = username.value;
        inf.pwd = pwd.value;
        inf.tips = tips.value;
        $.ajax({
            type:'GET',
            url:'',
            data:inf,
            success: function()
            {
                alert("创建用户成功！");
                location.href = '/selfcenter';
            }
        })

    })


})


