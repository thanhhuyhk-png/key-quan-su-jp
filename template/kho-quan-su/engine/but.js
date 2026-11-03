(function(g){
'use strict';
var K=g.Kho=g.Kho||{}, I=[1,0,0,1,0,0];
function tao(ctx,tt,def) {
 var m=I.slice(), stack=[], bounds={trai:Infinity,phai:-Infinity,tren:Infinity,duoi:-Infinity};
 var width=Math.max(1.2,0.012*tt.pxMoiMet)/tt.pxMoiMet;
 function point(x,y){return K.khung.diem(m,x,y);}
 function mark(p,pad){bounds.trai=Math.min(bounds.trai,p[0]-pad);bounds.phai=Math.max(bounds.phai,p[0]+pad);bounds.tren=Math.min(bounds.tren,p[1]-pad);bounds.duoi=Math.max(bounds.duoi,p[1]+pad);}
 function color(v,tone) {
  var c=tt.bangMau[v]; return c?c[tone||'nen']:K.mau(v,!!tt.dem,tone||'nen');
 }
 function path(points,fill,stroke,lw,close,tone){
  var pts=points.map(function(p){return point(p[0],p[1]);});
  var sw=stroke===false||(tt.vien===false&&close!==false)?0:(lw||width);
  pts.forEach(function(p){mark(p,sw/2);});
  if(!ctx||!pts.length)return;
  ctx.beginPath();ctx.moveTo(pts[0][0],pts[0][1]);
  for(var i=1;i<pts.length;i++)ctx.lineTo(pts[i][0],pts[i][1]);
  if(close!==false)ctx.closePath();
  if(fill){ctx.fillStyle=color(fill,tone);ctx.fill();}
  if(sw){ctx.strokeStyle=stroke&&stroke!==true?color(stroke,tone):K.mau('#1E1B14',tt.dem,'toi');ctx.lineWidth=sw;ctx.lineJoin='round';ctx.lineCap='round';ctx.stroke();}
  // Screen-space upper-left rim stays fixed when an object or branch is mirrored.
  if(fill&&sw&&close!==false&&(!tone||tone==='nen')&&tt.bangMau[fill]){
   var world=pts.map(function(q){return K.khung.diem(tt.maTranCanh,q[0],q[1]);}),area=0;
   for(var z=0;z<world.length;z++){var next=world[(z+1)%world.length];area+=world[z][0]*next[1]-next[0]*world[z][1];}
   ctx.beginPath();
   for(var k=0;k<world.length;k++){var n=(k+1)%world.length,dx=world[n][0]-world[k][0],dy=world[n][1]-world[k][1],sign=area>0?1:-1;
    if(sign*(-.6*dy+dx)>.50*Math.hypot(dx,dy)){ctx.moveTo(pts[k][0],pts[k][1]);ctx.lineTo(pts[n][0],pts[n][1]);}
   }
   ctx.strokeStyle=color(fill,'sang');ctx.lineWidth=sw*.45;ctx.stroke();
  }
 }
 var b={
  ctx:ctx,tt:tt,khung:bounds,
  mau:color,
  daGiac:function(pts,fill,tone,outline){path(pts,fill,outline,undefined,true,tone);},
  net:function(pts,c,w,tone){path(pts,null,c||true,w,false,tone);},
  tron:function(x,y,rx,ry,fill,tone,outline){
   var pts=[];for(var j=0;j<48;j++){var a=j*Math.PI/24;pts.push([x+rx*Math.cos(a),y+ry*Math.sin(a)]);}
   path(pts,fill,outline,undefined,true,tone);
  },
  hop:function(x,y,w,h,fill,tone,outline){b.daGiac([[x,y],[x+w,y],[x+w,y+h],[x,y+h]],fill,tone,outline);},
  tai:function(x,y,a,f,fn){
   var old=m, r=a*K.khung.rad;
   m=K.khung.nhan(m,[Math.cos(r)*(f||1),Math.sin(r)*(f||1),-Math.sin(r),Math.cos(r),x,y]);
   try{fn(b);}finally{m=old;}
  },
  xuong:function(name,fn){
   var bone=tt.xuong[name];if(!bone)throw Error('Không có xương '+name);
   stack.push(m);m=bone.maTran;
   if(tt.tyLeHinh&&tt.tyLeHinh!==1)m=K.khung.nhan(m,[tt.tyLeHinh,0,0,tt.tyLeHinh,0,0]);
   try{fn(b);}finally{m=stack.pop();}
  },
  diem:function(name,x,y){return K.khung.diem(tt.xuong[name].maTran,x||0,y||0);},
  neo:function(name,x,y){tt.neo[name]=point(x,y);},
  la:function(x,y,r,hat,matDo){
   var rng=K.rng(hat),n=Math.floor(13*Math.max(0,Math.min(1,matDo)));
   for(var j=0;j<n;j++){
    var xx=x+(rng()-.5)*r*1.7,yy=y+(rng()-.5)*r*.65,a=(rng()-.5)*115;
    b.tai(xx,yy,a,1,function(){
     var length=r*(.65+rng()*.45);
     b.net([[0,-length*.5],[.04*r,0],[.19*r,length*.55]],'la',Math.max(.003,r*.019),'toi');
     for(var h=0;h<6;h++){
      var side=h%2?-1:1,cy=-length*.43+h*length*.15;
      var base=[.045*r+h*.012*r,cy],tip=[base[0]+side*r*(.24+rng()*.17),cy+r*(.20+rng()*.13)];
      var dx=tip[0]-base[0],dy=tip[1]-base[1],len=Math.hypot(dx,dy),nx=-dy/len,ny=dx/len,w=len*.14,pts=[];
      // Lanceolate leaves: narrow base and tip, widest below the midpoint.
      var stations=[[0,0],[.19,.56],[.45,1],[.72,.66],[1,0]];
      stations.forEach(function(z){pts.push([base[0]+dx*z[0]+nx*w*z[1],base[1]+dy*z[0]+ny*w*z[1]]);});
      stations.slice(1,-1).reverse().forEach(function(z){pts.push([base[0]+dx*z[0]-nx*w*z[1],base[1]+dy*z[0]-ny*w*z[1]]);});
      b.daGiac(pts,'la',['toi','nen','sang'][(j+h)%3],false);
      b.net([base,[base[0]+dx*.84,base[1]+dy*.84]],'la',Math.max(.002,r*.009),'toi');
     }
    });
   }
  }
 };
 return b;
}
function day(ctx,a,b,options){
 options=options||{}; if(!a||!b)throw Error('Dây thiếu neo');
 var sag=options.vong===undefined?8:options.vong, col=options.mau||'#9c936d';
 ctx.save();ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.quadraticCurveTo((a[0]+b[0])/2,(a[1]+b[1])/2+sag,b[0],b[1]);ctx.strokeStyle=col;ctx.lineWidth=options.doDay||2;ctx.lineCap='round';ctx.stroke();ctx.restore();
}
K.but={tao:tao,day:day};
})(typeof window!=='undefined'?window:globalThis);
