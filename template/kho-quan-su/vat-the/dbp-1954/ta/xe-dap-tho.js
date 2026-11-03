(function(g){
'use strict';var K=g.Kho,r=.355;
var palette={thep:{nen:'#4E5B40',toi:'#2F392C',sang:'#839072'},sat:{nen:'#737665',toi:'#3A4038',sang:'#A1A38D'},banh:{nen:'#262822',toi:'#121611',sang:'#4A5042'},tre:{nen:'#B39A5B',toi:'#78663B',sang:'#C7B47A'},go:{nen:'#7A5A36',toi:'#493620',sang:'#AC8C5D'},bao:{nen:'#B0A07C',toi:'#7B7158',sang:'#D0BF98'},day:{nen:'#91815B',toi:'#61543A',sang:'#BEAA78'},la:{nen:'#56703A',toi:'#3F5A2A',sang:'#6E7F3E'}};
function openWheel(b,x,angle){
 b.tai(x,-r,angle/K.khung.rad,1,function(){
  // Thin continuous tyre rings leave the interior transparent in scenes.
  var ring=[],inner=[];
  for(var i=0;i<=64;i++){var a=i*Math.PI/32;ring.push([r*Math.cos(a),r*Math.sin(a)]);inner.push([(r-.029)*Math.cos(a),(r-.029)*Math.sin(a)]);}
  for(var j=0;j<64;j++)b.daGiac([ring[j],ring[j+1],inner[j+1],inner[j]],'banh','nen',false);
  b.net(inner,'sat',.012);
  for(var h=0;h<32;h++){
   var q=h*Math.PI/16;
   b.net([[Math.cos(q+.19)*.028,Math.sin(q+.19)*.028],[Math.cos(q)*(r-.038),Math.sin(q)*(r-.038)]],'sat',.0045);
   if(h%2===0)b.net([[Math.cos(q)*(r-.009),Math.sin(q)*(r-.009)],[Math.cos(q+.025)*(r-.026),Math.sin(q+.025)*(r-.026)]],'banh',.006);
  }
  b.tron(0,0,.036,.036,'sat','nen');b.tron(0,0,.014,.014,'banh','toi');
 });
}
function bamboo(b,a,c){
 var dx=c[0]-a[0],dy=c[1]-a[1],len=Math.hypot(dx,dy),ang=Math.atan2(dy,dx)/K.khung.rad;
 b.tai(a[0],a[1],ang,1,function(){
  b.daGiac([[0,-.018],[len,-.015],[len+.01,.011],[0,.02]],'tre','nen');
  b.net([[.01,-.009],[len,-.007]],'tre',.007);
  for(var j=.12;j<len;j+=.17){b.hop(j-.009,-.021,.018,.046,'tre','toi',false);b.net([[j+.013,-.016],[j+.04,-.011]],'tre',.005);}
 });
}
function tie(b,x,y,a){
 b.tai(x,y,a,1,function(){for(var j=0;j<6;j++)b.net([[-.04+j*.014,-.036],[-.036+j*.014,.041]],'day',.009);b.net([[-.04,.025],[.06,-.034]],'day',.009);b.net([[.02,.037],[.055,.09],[.04,.12]],'day',.008);});
}
function sack(b,x,y,far){
 b.tai(x,y,0,1,function(){
  function soft(points,tone,outline){
   var out=[];
   for(var i=0;i<points.length;i++){
    var a=points[(i+points.length-1)%points.length],c=points[i],d=points[(i+1)%points.length],e=points[(i+2)%points.length];
    for(var j=0;j<5;j++){var t=j/5,t2=t*t,t3=t2*t;out.push([0,1].map(function(k){return .5*(2*c[k]+(-a[k]+d[k])*t+(2*a[k]-5*c[k]+4*d[k]-e[k])*t2+(-a[k]+3*c[k]-3*d[k]+e[k])*t3);}));}
   }
   b.daGiac(out,'bao',tone,outline);
  }
  soft([[-.055,-.20],[-.16,-.155],[-.26,-.075],[-.30,.08],[-.29,.29],[-.24,.415],[-.12,.465],[.075,.465],[.22,.424],[.285,.315],[.29,.12],[.25,-.04],[.15,-.14],[.045,-.20]],far?'toi':'nen');
  soft([[-.16,-.12],[-.23,-.02],[-.245,.15],[-.21,.35],[-.16,.42],[-.20,.39],[-.267,.25],[-.271,.06],[-.22,-.065]],far?'nen':'sang',false);
  soft([[.17,-.10],[.25,.025],[.282,.19],[.249,.36],[.19,.42],[.115,.44],[.181,.32],[.19,.16]],'toi',false);
  for(var i=0;i<6;i++){var xx=-.20+i*.072;b.net([[xx*.17,-.187],[xx*.75,-.092],[xx,.02]],'bao',.006,'toi');}
  b.net([[-.252,.31],[-.19,.36],[-.16,.414]],'bao',.007,'toi');
  b.net([[.23,.31],[.15,.38],[.06,.414]],'bao',.007,'toi');
  b.net([[-.09,.436],[-.025,.419],[.032,.435]],'bao',.006,'toi');
  soft([[-.052,-.192],[-.081,-.25],[-.032,-.24],[.022,-.257],[.057,-.246],[.043,-.194]],far?'toi':'nen');
  for(var h=0;h<4;h++)b.net([[-.057,-.194-h*.009],[.048,-.194-h*.009]],'day',.007);
  b.net([[.03,-.216],[.096,-.24],[.099,-.206],[.028,-.212],[.08,-.167]],'day',.007);
  // Sparse weave, not printed markings.
  for(var j=0;j<22;j++){var tx=-.19+(j%5)*.077,ty=.055+Math.floor(j/5)*.067;b.net([[tx,ty],[tx+.017,ty-.004]],'bao',.0027,far?'nen':'toi');b.net([[tx+.008,ty-.008],[tx+.011,ty+.008]],'bao',.0025,far?'nen':'toi');}
 });
}
function stool(b,x,y,a,far,height){
 height=height||.25;
 b.tai(x,y,a||0,1,function(){
  b.net([[-.10,.025],[-.17,height]],'go',.035);b.net([[.10,.025],[.18,height]],'go',.035);b.net([[0,.012],[.025,height-.02]],'go',.031);
  b.net([[-.14,.16],[.14,.16]],'go',.018);
  b.daGiac([[-.15,-.015],[.13,-.028],[.17,.008],[.13,.043],[-.15,.04],[-.18,.014]],'go',far?'toi':'nen');
  b.net([[-.13,.002],[.11,-.006]],'go',.007);
 });
}
function ve(b,tt){
 b.xuong('xe',function(){
  sack(b,-.32,-.88,true);
  openWheel(b,-.57,tt.so.gocBanh);openWheel(b,.57,tt.so.gocBanh);
  // Men's diamond frame, reinforced rack and chain.
  b.net([[-.57,-r],[-.10,-.38],[.35,-.91],[-.23,-.95],[-.57,-r]],'thep',.035);
  b.net([[-.23,-.95],[-.10,-.38],[.35,-.91],[.57,-r]],'thep',.035);
  b.net([[.35,-.91],[.39,-1.035],[.46,-1.08],[.53,-1.04]],'sat',.027);
  b.net([[.40,-1.04],[.49,-1.13],[.57,-1.115],[.58,-1.06]],'banh',.023);
  b.net([[-.25,-1.02],[-.23,-.95]],'sat',.032);
  b.daGiac([[-.36,-1.045],[-.17,-1.055],[-.115,-1.018],[-.17,-.994],[-.36,-1.00]],'banh','nen');
  b.net([[-.73,-1.02],[-.10,-1.02],[-.1,-.95],[-.73,-.95],[-.73,-1.02]],'sat',.022);
  for(var j=0;j<6;j++)b.net([[-.70+j*.105,-1.02],[-.70+j*.105,-.95]],'sat',.012);
  b.net([[-.68,-.96],[-.57,-r],[-.22,-.96]],'thep',.021);
  b.tron(-.10,-.38,.109,.109,'sat','toi');b.tron(-.10,-.38,.077,.077,'thep','nen');
  b.net([[-.57,-.39],[-.10,-.49],[.0,-.40],[-.10,-.275],[-.57,-.33]],'banh',.012);
  for(var k=0;k<21;k++){var xx=-.55+k*.022;b.net([[xx,-.39-(xx+.55)*.20],[xx+.009,-.397-(xx+.55)*.20]],'sat',.004);}
  b.tai(-.10,-.38,tt.so.gocBanh/K.khung.rad*.4,1,function(){
   b.net([[-.11,-.06],[.11,.06]],'sat',.022);b.hop(.08,.048,.10,.026,'banh','nen');
  });
  bamboo(b,[-.53,-.83],[.30,-.84]);tie(b,-.42,-.83,0);tie(b,.20,-.84,0);
  b.net([[-.50,-.48],[.29,-.85]],'sat',.019);
  sack(b,-.40,-.89,false);
  b.net([[-.69,-1.01],[-.61,-.42],[-.28,-.40],[-.12,-1.02]],'day',.018);
  b.net([[-.76,-.76],[-.06,-.81]],'day',.017);
  bamboo(b,[.44,-1.075],[-.55,-1.36]);tie(b,.39,-1.08,5);tie(b,.30,-1.09,5);
  bamboo(b,[-.24,-.99],[-.75,-1.55]);tie(b,-.25,-1.02,84);tie(b,-.26,-1.12,84);
  if(tt.trangThai==='nghi')stool(b,-.10,-.37,0,false,.3525);
  else stool(b,-.61,-.72,-90,false);
  if(tt.trangThai==='xuong-doc')stool(b,1.01+tt.so.chenGhe,-.25,0,false);
  else stool(b,-.31,-.73,-90,true);
  if(tt.trangThai!=='nghi')b.net([[-.66,-.92],[-.61,-.48],[-.38,-.49],[-.34,-.92]],'day',.012);
  if(tt.trangThai!=='xuong-doc')b.net([[-.36,-.92],[-.30,-.51],[-.02,-.51],[-.02,-.91]],'day',.012);
  b.neo('tayNgai',-.55,-1.36);b.neo('treYen',-.75,-1.55);b.neo('dayTruoc',.47,-1.09);
  b.neo('banhSau',-.57,-r);b.neo('banhTruoc',.57,-r);
  if(tt.nguyTrang>0)b.la(-.40,-1.03,.25,tt.hat+83,tt.nguyTrang*.4);
 });
}
var states={};['dat','len-doc','xuong-doc','nghi'].forEach(function(n){
 states[n]={chuKy:1.6,lap:true,tocDo:{dat:.45,'len-doc':.24,'xuong-doc':.18,nghi:0}[n],tuThe:function(p){return {so:{chenGhe:n==='xuong-doc'?.04*(1-Math.cos(p*Math.PI*2)):0}};}};
});
K.dangKy({ma:'xe-dap-tho',ten:'Xe đạp thồ',phe:'ta',thoiKy:'dbp-1954',kichThuoc:{dai:1.85,cao:1.55,duongKinhBanh:.71},bangMau:palette,xuong:[{ten:'xe',x:0,y:0}],
 thamSoMacDinh:{gocBanh:0,chenGhe:0},trangThai:states,
 chuanBi:function(tt){tt.so.gocBanh=tt.quangDuong/r;tt.so.banKinhBanh=r;},
 diemCham:[{x:-.57,y:-r,r:r},{x:.57,y:-r,r:r}],ve:ve});
})(typeof window!=='undefined'?window:globalThis);
