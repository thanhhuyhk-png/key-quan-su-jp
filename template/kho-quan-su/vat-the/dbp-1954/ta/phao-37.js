(function(g){
'use strict';var K=g.Kho,R=K.khung.rad,r=.47;
var palette={thep:{nen:'#4E5B31',toi:'#303C24',sang:'#7C8955'},banh:{nen:'#1F1F1C',toi:'#111310',sang:'#464B3F'},sat:{nen:'#686F5B',toi:'#32392D',sang:'#959C7A'},go:{nen:'#7A5A36',toi:'#493A28',sang:'#A38A56'},la:{nen:'#56703A',toi:'#3F5A2A',sang:'#6E7F3E'},dat:{nen:'#786D4C',toi:'#443E31',sang:'#9C8C62'},lua:{nen:'#DCAB63',toi:'#B4763F',sang:'#E4D2A0'}};
function banh(b,x,y,far,angle){
 b.tai(x,y,angle/R,1,function(){
  b.tron(0,0,r,r,'banh',far?'toi':'nen');
  for(var j=0;j<30;j++){
   b.tai(0,0,j*12,1,function(){b.daGiac([[-.024,-.462],[.025,-.46],[.034,-.418],[-.015,-.425]],'banh',far?'nen':'sang',false);});
  }
  b.tron(0,0,.349,.349,'thep',far?'toi':'nen');
  b.tron(0,0,.309,.309,'sat',far?'toi':'nen');
  b.tron(0,0,.275,.275,'thep',far?'toi':'nen');
  for(var i=0;i<6;i++){
   var a=i*Math.PI/3;b.tron(Math.cos(a)*.22,Math.sin(a)*.22,.029,.039,'banh','toi');
   b.tron(Math.cos(a)*.118,Math.sin(a)*.118,.011,.011,'sat',far?'nen':'sang',false);
  }
  b.tron(0,0,.086,.086,'sat',far?'toi':'nen');b.tron(0,0,.042,.042,'thep','toi');
  b.net([[-.24,-.19],[-.18,-.25],[-.095,-.28]],'sat',.012);
 });
}
function chan(b,x,far,down){
 var y=down?-.10:-.42;
 b.net([[x*.66,-.62],[x,y]],'thep',far?.075:.11);
 b.hop(x-.038,y-.10,.076,down?.20:.09,'sat',far?'toi':'nen');
 for(var j=0;j<5;j++)b.net([[x-.033,y-.08+j*.024],[x+.032,y-.08+j*.024]],'sat',.008);
 b.daGiac([[x-.16,down?-.045:y+.07],[x+.17,down?-.045:y+.07],[x+.20,down?0:y+.10],[x-.18,down?0:y+.10]],'thep',far?'toi':'nen');
}
function ve(b,tt){
 var fire=tt.so.chanKich>0, wy=-r-(tt.so.banhNhac||0),turret='be';
 b.xuong('xe',function(){
  banh(b,-1.37,wy-.10,true,tt.so.gocBanh);banh(b,1.60,wy-.10,true,tt.so.gocBanh);
  chan(b,-1.88,true,fire);chan(b,1.88,true,fire);
  b.daGiac([[-2.06,-.77],[1.98,-.77],[2.25,-.68],[2.25,-.54],[-2.08,-.54]],'thep','nen');
  b.daGiac([[-2.03,-.76],[1.99,-.76],[2.18,-.68],[-2.03,-.68]],'thep','sang',false);
  b.daGiac([[1.65,-.67],[2.05,-.72],[3.02,-.35],[3.04,-.25],[2.92,-.25],[1.7,-.52]],'thep','nen');
  b.tron(3.045,-.30,.055,.055,'sat','nen');b.tron(3.045,-.30,.025,.025,'banh','toi',false);b.neo('mocKeo',3.045,-.30);
  b.net([[-1.5,-.57],[-1.5,wy],[1.5,wy],[1.5,-.58]],'sat',.10);
  for(var j=0;j<19;j++)b.tron(-1.95+j*.216,-.60,.013,.013,'sat','sang',false);
  b.tron(-.12,-.83,.66,.14,'thep','toi');
  b.hop(-.47,-1.18,.73,.37,'thep','nen');b.tron(-.12,-1.18,.48,.08,'sat','nen');
  b.net([[-1.83,-.75],[-1.85,-1.55],[-1.66,-1.55]],'thep',.048);
  b.daGiac([[-1.98,-1.62],[-1.77,-1.65],[-1.60,-1.6],[-1.76,-1.51],[-1.97,-1.54]],'thep','nen');
 });
 b.xuong(turret,function(){
  // Far shield edge and far seat remain distinct from the near plate.
  b.daGiac([[.30,-.84],[.46,-.79],[.62,.49],[.45,.57],[.22,-.34]],'thep','toi');
  b.net([[-.68,.30],[-.87,-.03]],'sat',.045);
  b.daGiac([[-1.05,-.09],[-.73,-.12],[-.60,-.04],[-.76,.025],[-1.04,.018]],'thep','toi');
  b.daGiac([[-.51,.43],[-.43,-.25],[-.23,-.51],[.17,-.49],[.38,.37],[.24,.49]],'thep','nen');
  b.tron(-.06,-.06,.235,.235,'sat','nen');b.tron(-.06,-.06,.15,.15,'thep','toi');
  for(var j=0;j<12;j++){var a=j*Math.PI/6;b.tron(-.06+Math.cos(a)*.192,-.06+Math.sin(a)*.192,.012,.012,'sat','sang',false);}
  b.net([[-.54,.12],[-.82,.41],[-1.0,.41]],'sat',.045);
  b.daGiac([[-1.16,.34],[-.84,.31],[-.71,.35],[-.76,.42],[-1.14,.43]],'thep','nen');
  b.net([[-.87,.38],[-.90,.09],[-1.02,-.09]],'thep',.041);
  b.tron(-.48,.015,.13,.13,'sat','nen');b.tron(-.48,.015,.095,.095,'thep','toi');
  for(var z=0;z<3;z++){var aa=z*Math.PI*2/3;b.net([[-.48,.015],[-.48+Math.cos(aa)*.102,.015+Math.sin(aa)*.102]],'sat',.013);}
  b.net([[-.49,.015],[-.62,.14],[-.72,.14]],'sat',.022);
  // Upright shield immediately in front of the seats, independent of barrel elevation.
  b.daGiac([[.13,-.91],[.39,-.90],[.50,-.75],[.53,-.25],[.72,.47],[.18,.49],[.03,-.19]],'thep','nen');
  b.daGiac([[.13,-.91],[.20,-.91],[.31,.35],[.23,.43],[.10,-.21]],'thep',tt.huong===1?'sang':'toi',false);
  b.net([[.39,-.85],[.45,-.68],[.49,-.25],[.65,.40]],'sat',.012);
  for(var h=0;h<9;h++)b.tron(.20+h*.045,.42,.010,.010,'sat','sang',false);
  b.net([[-.21,-.27],[-.35,-.61],[-.53,-.65]],'sat',.028);
  b.hop(-.61,-.70,.18,.06,'sat','nen');b.tron(-.61,-.67,.041,.041,'banh','toi');
 });
 b.xuong('nong',function(){
  var recoil=tt.so.giatLui;
  b.tai(-recoil,0,0,1,function(){
   b.daGiac([[-.39,-.15],[.16,-.15],[.28,-.092],[.28,.10],[-.32,.12],[-.43,.04]],'sat','nen');
   b.hop(-.30,-.22,.43,.065,'thep','toi');
   b.daGiac([[-.29,-.25],[.16,-.25],[.20,-.20],[-.30,-.19]],'sat','nen');
   for(var k=0;k<5;k++){
    b.daGiac([[-.25+k*.073,-.23],[-.25+k*.073,-.36],[-.232+k*.073,-.405],[-.213+k*.073,-.36],[-.213+k*.073,-.23]],'go','sang');
    b.hop(-.251+k*.073,-.31,.04,.055,'sat','nen');
   }
   b.hop(.17,-.084,.78,.15,'thep','nen');
   for(var u=0;u<12;u++)b.hop(.21+u*.06,-.09,.018,.162,'sat',u%2?'toi':'nen',false);
   b.daGiac([[.90,-.047],[2.94,-.032],[3.00,-.021],[3.00,.021],[.9,.042]],'sat','nen');
   b.net([[.99,-.029],[2.93,-.02]],'sat',.011);
   b.hop(2.94,-.042,.065,.079,'sat','toi');
   b.neo('dauNong',3,0);
   if(tt.trangThai==='ban'&&tt.p<.20){
    b.daGiac([[3.0,-.028],[3.16,-.09],[3.12,-.025],[3.29,0],[3.12,.028],[3.18,.09],[3.0,.025]],'lua','nen',false);
    b.daGiac([[3.0,-.017],[3.17,0],[3.0,.018]],'lua','sang',false);
   }
  });
 });
 b.xuong('xe',function(){
  banh(b,-1.50,wy,false,tt.so.gocBanh);b.neo('banhSau',-1.50,wy);
  banh(b,1.50,wy,false,tt.so.gocBanh);b.neo('banhTruoc',1.50,wy);
  chan(b,-2.16,false,fire);chan(b,2.16,false,fire);
  if(tt.trangThai==='chen-banh')[-1.5,1.5].forEach(function(x){
   b.daGiac([[x-.62,0],[x-.52,-.18],[x-.32,-.12],[x-.30,0]],'go','nen');b.net([[x-.56,-.03],[x-.48,-.11],[x-.37,-.065]],'go',.016);
  });
  if(tt.trangThai==='u-dat'){
   b.daGiac([[-2.55,.02],[-2.46,-.38],[-2.17,-.70],[-1.72,-.85],[-1.37,-.65],[-.8,-.72],[-.3,-.61],[.35,-.72],[1.0,-.67],[1.6,-.82],[2.12,-.69],[2.54,-.32],[2.6,.02]],'dat','nen');
   var rng=K.rng(tt.hat+810);for(var i=0;i<48;i++){var x=-2.3+rng()*4.6,y=-.08-rng()*.47;b.net([[x,y],[x+.09,y-.025],[x+.16,y+.012]],'dat',.012);}
   b.net([[-2.2,-.67],[-1.75,-.77],[-1.42,-.61],[-.85,-.66]],'dat',.027);
  }
 });
 if(tt.nguyTrang>0){
  var sites=[[-1.1,-.7,.54],[-.45,-1.3,.58],[.25,-1.6,.60],[.45,-.95,.66],[1.05,-.65,.45],[-1.65,-.6,.38]];
  sites.forEach(function(v,i){b.la(v[0],v[1]+tt.doDoiY,v[2],tt.hat+i*179,tt.nguyTrang);});
  b.xuong('nong',function(){[.55,1.10,1.65,2.20].forEach(function(x,i){b.tai(x,.035,-tt.xuong.nong.goc,1,function(){b.la(0,0,.30-i*.035,tt.hat+811+i*97,tt.nguyTrang);});});});
 }
}
function pose(name){return function(p){
 var firing=name==='ban',deploy=['ban','u-dat','nguy-trang'].indexOf(name)>=0;
 return {tuThe:{nong:deploy?-55:2},so:{banhNhac:deploy?.18:0,chanKich:deploy?1:0,giatLui:firing?.11*Math.exp(-p*16)*Math.sin(Math.PI*Math.min(1,p*6)):0}};
};}
var states={};['keo','chen-banh','ban','u-dat','nguy-trang'].forEach(function(n){states[n]={chuKy:n==='ban'?.35:1.6,lap:true,tocDo:n==='keo'?.6:0,nguyTrang:n==='nguy-trang'?1:0,tuThe:pose(n)};});
K.dangKy({ma:'phao-37',ten:'Pháo cao xạ 37 mm',phe:'ta',thoiKy:'dbp-1954',kichThuoc:{dai:6.2,cao:2.5,rong:1.78},bangMau:palette,
 xuong:function(tt){var tow=['keo','chen-banh'].indexOf(tt.trangThai)>=0;return [{ten:'xe',x:0,y:0},{ten:'be',cha:'xe',x:-.10,y:-1.42,lat:tow?-1:1},{ten:'nong',cha:'be',x:0,y:0}];},
 thamSoMacDinh:{banhNhac:0,chanKich:0,giatLui:0,gocBanh:0},trangThai:states,
 chuanBi:function(tt){tt.so.gocBanh=tt.quangDuong/r;tt.so.banKinhBanh=r;},
 diemCham:function(tt){return tt.so.chanKich?[{x:-2.16,y:0},{x:2.16,y:0},{x:-1.88,y:0},{x:1.88,y:0}]:[{x:-1.5,y:-r,r:r},{x:1.5,y:-r,r:r}];},
 ve:ve
});
})(typeof window!=='undefined'?window:globalThis);
