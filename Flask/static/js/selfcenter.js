

var del = document.querySelectorAll(".del");
for(var i=0;i<del.length;i++){
    del[i].addEventListener('click',function(){
        var titem = this.parentNode.parentNode;
        var pnt = titem.parentNode;
        pnt.removeChild(titem);
    })
}

var edit = document.querySelectorAll(".edit");
for(var i=0;i<edit.length;i++){
    edit[i].addEventListener('click',function(){
        var titem = this.parentNode.parentNode;
        var pnt = titem.parentNode;
        pnt.removeChild(titem);
    })
}