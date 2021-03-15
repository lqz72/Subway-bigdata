$(function(){
    $.ajax({
        type:'GET',
        url:'/admin_info',

        success: function(data){
            console.log(typeof(data));
            tag = '<tr> <td>用户名</td> <td>密码</td> <td>备注</td> <td>修改</td> <td>删除</td> </tr>';
            for(var i=0;i<data.length;i++)
            {
                tag += '<tr>'+'<td>'+data[i].name+'</td>'+'<td>'+data[i].pwd+'</td>'+'<td>'+data[i].tips
                +'</td>'+'<td><a href="javascript:;">修改</a></td><td><a href="javascript:;">删除</a></td>'+'</tr>';
            }
            var ct = document.querySelector('#adminlist');
            ct.innerHTML = tag;
        }
    })
})



// var del = document.querySelectorAll(".del");
// for(var i=0;i<del.length;i++){
//     del[i].addEventListener('click',function(){
//         var titem = this.parentNode.parentNode;
//         var pnt = titem.parentNode;
//         pnt.removeChild(titem);
//     })
// }

// var edit = document.querySelectorAll(".edit");
// for(var i=0;i<edit.length;i++){
//     edit[i].addEventListener('click',function(){
//         var titem = this.parentNode.parentNode;
//         var pnt = titem.parentNode;
//         pnt.removeChild(titem);
//     })
// }

//error try
// success: function(data){
//     console.log(data);
//     tag = '';
//     for(var i=0;i<data.length;i++)
//     {
//         tag += '<tr>'+'<td>'+data[i].name+'</td>'+'<td>'+data[i].pwd+'</td>'+'<td>'+data[i].tips
//         +'</td>'+'</tr>';
//     }
//     console.log(tag);
//     var ct = document.querySelector('#adminlist');
//     ct.innerHTML = tag;
// }

// success: function(data) {
//     var ct = document.querySelector('#adminlist');
//     for(var i=0;i<data.length;i++)
//     {
//         var tr = document.createElement('tr');
//         ct.appendChild(tr);
//         for(var j in data[i])
//         {
//             var td = document.createElement('td');
//             td.innerHTML = data[i][j];
//             tr.appendChild(td);
//         }
//         var edit = document.createElement('td');
//         edit.innerHTML = '<a href="javascript:;">修改</a>';
//         tr.appendChild(edit);
//         var del = document.createElement('td');
//         del.innerHTML = '<a href="javascript:;">删除</a>';
//         tr.appendChild(del);
//         $("#adminlist").trigger("create"); 
//     }
// }