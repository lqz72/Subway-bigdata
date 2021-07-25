var btn = document.querySelector("#btn");
var idin = document.querySelector("#idin");
console.log(1);
console.log(test);
btn.addEventListener('click',function()
{
    location.href = '/client';
    userid = idin.value;
    changedata();
})

layui.use('laypage', function(){
    var laypage = layui.laypage;
    
    //执行一个laypage实例
    laypage.render({
    elem: 'pageselector' //注意，这里的 test1 是 ID，不用加 # 号
    ,count: 24782 //数据总数，从服务端得到
    ,limit:15
    ,groups:15
    ,layout:['prev', 'page', 'next','refresh','skip']
    ,jump: function(obj, first){
        //obj包含了当前分页的所有参数，比如：
        // console.log(obj.curr); //得到当前页，以便向服务端请求对应页的数据。
        // console.log(obj.limit); //得到每页显示的条数
        
        $.ajax({
            type:'get',
            url:'/user/users_info/' + obj.curr,
            success: function(data)
            {
                var t = {};
                t.tt = '这是怎么回事';
                t.val = data;
                // console.log(t);
                var html = template('test', t);
                document.getElementById('userlist').innerHTML = html;
                
            }
        })

        //首次不执行
        if(!first){
        //do something
        }
        }
        });
});




