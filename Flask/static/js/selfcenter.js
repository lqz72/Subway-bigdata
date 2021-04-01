$(function(){
    $.ajax({
        type:'GET',
        url:'/admin_info',
        success: function(data){
            console.log(data)
            var t = {};
            t.list = data;
            var html = template('admindata', t);
            document.getElementById('adminlist').innerHTML = html;

            var ad_list = document.querySelector('#adminlist').children[0];
            for(var i=0;i<data.length;i++)
            {
                var edit = ad_list.children[i+1].children[3].children[0].children[0];
                edit.setAttribute("index",i);
                edit.addEventListener('click',function(){
                    // console.log(this.getAttribute("index"));
                    // 0表示第一个元素
                    //向后台发送编辑index请求
                    var top = this.parentNode.parentNode.parentNode;
                    var v_username = top.children[0].innerHTML;
                    var v_pwd = top.children[1].innerHTML;
                    var v_tips = top.children[2].innerHTML;
                    var past_inf = {};
                    past_inf.username = v_username;
                    past_inf.pwd = v_pwd;
                    past_inf.tips = v_tips;
                    $('#testmodal').on('show.bs.modal', function (event) {
                        var modal = $(this);
                        modal.find('#m-username').val(past_inf.username);
                        modal.find('#m-pwd').val(past_inf.pwd);
                        modal.find('#m-tips').val(past_inf.tips);
                        
                    })
                    $('#testmodal').modal();
                    var data_to_back = {};
                    var username = document.querySelector('#m-username');
                    var pwd = document.querySelector('#m-pwd');
                    var tips = document.querySelector('#m-tips');
                    var inf = {};
                    inf.username = username.value;
                    inf.pwd = pwd.value;
                    inf.tips = tips.value;
                    data_to_back.inf = inf;
                    data_to_back.index = this.getAttribute("index");
                    var confirm = document.querySelector('#confirm_edit');
                    confirm.addEventListener('click',function(){
                        inf.username = username.value;
                        inf.pwd = pwd.value;
                        inf.tips = tips.value;
                        data_to_back.inf = inf;
                        // console.log(data_to_back);
                        //修改用户
                        $.ajax({
                            type:'POST',
                            url:'/update_database',
                            data:JSON.stringify(data_to_back),
                            success: function(data)
                            {
                                if(data)
                                {
                                    alert("修改成功！");
                                    location.href = '/selfcenter';
                                }
                            }
                        })
                    })
                })
                var del = edit.nextElementSibling;
                del.setAttribute("index",i);
                del.addEventListener("click",function(){
                    console.log(this.getAttribute("index"));
                    var index = this.getAttribute("index");
                    //向后台发送删除index请求
                    var r=confirm("你确定要删除吗？")
                    if (r==true)
                        {
                            //删除用户
                            $.ajax({
                                type:'POST',
                                url:'/del_inf',
                                data:String(index),
                                contentType:"application/json",
                                success: function(data)
                                {
                                    if(data)
                                    {
                                        alert("删除成功！");
                                        location.href = '/selfcenter';
                                    }
                                }
                            })
                        }
                    else
                        {
                            
                        }
                    
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
        //新建用户
        $.ajax({
            type:'POST',
            url:'/wirte_to_database',
            data:JSON.stringify(inf),
            // contentType:"application/json",
            // processData:"false",
            success: function(data)
            {
                if(data)
                {
                    alert("创建用户成功！");
                    location.href = '/selfcenter';
                }
            }
        })

    })


})


