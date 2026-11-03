(function(g){
'use strict';
var K=g.Kho, R=Math.PI/180;
function xuong(cao){
 var s=(cao||1.62)/1.62;
 return [
  {ten:'hong',x:0,y:-.82},{ten:'than',cha:'hong',x:0,y:0},
  {ten:'co',cha:'than',x:0,y:-.50},{ten:'dau',cha:'co',x:0,y:-.06},
  {ten:'tayXa',cha:'than',x:-.035,y:-.46},{ten:'cangTayXa',cha:'tayXa',x:0,y:.29},
  {ten:'tayGan',cha:'than',x:.025,y:-.46},{ten:'cangTayGan',cha:'tayGan',x:0,y:.29},
  {ten:'duiXa',cha:'hong',x:-.035,y:0},{ten:'cangChanXa',cha:'duiXa',x:0,y:.42},{ten:'banChanXa',cha:'cangChanXa',x:0,y:.42},
  {ten:'duiGan',cha:'hong',x:.035,y:0},{ten:'cangChanGan',cha:'duiGan',x:0,y:.42},{ten:'banChanGan',cha:'cangChanGan',x:0,y:.42}
 ].map(function(b){return Object.assign({},b,{x:b.x*s,y:b.y*s});});
}
// Angles from downward vertical. The second angle is relative to the first link.
function ik(x,y,a,b,bend){
 var d=Math.min(a+b-.0001,Math.max(.02,Math.hypot(x,y))), sign=bend||1;
 var q=Math.acos(Math.max(-1,Math.min(1,(a*a+d*d-b*b)/(2*a*d))));
 return [(Math.atan2(-x,y)+sign*q)/R,sign*(Math.acos(Math.max(-1,Math.min(1,(a*a+b*b-d*d)/(2*a*b))))-Math.PI)/R];
}
function tuThe(name,p,t){
 var q={},so={}, moving=['di','chay','keo-day','day','dat-xe','ghi'].indexOf(name)>=0;
 var speed={di:.65,chay:1.25,'keo-day':.30,day:.28,'dat-xe':.34,ghi:.20}[name]||0;
 var cycle=name==='chay'?.74:1.6, phase=moving?((t/cycle)%1+1)%1:0;
 var effort=name==='keo-day'||name==='day', feet=[];
 q.than=name==='keo-day'?34:name==='day'?50:name==='dat-xe'?12:name==='ghi'?-24:name==='quy-ngam'?35:0;
 so.hongX=name==='keo-day'?.30:name==='day'?.40:0;
 for(var i=0;i<2;i++){
  var u=(phase+i*.5)%1,step=speed*cycle,x=i?-.025:.025,lift=0;
  if(moving){
   if(u<.60)x=step*(.30-u);
   else {var w=(u-.60)/.40;x=-step*.30+step*.60*(w*w*(3-2*w));lift=-.085*Math.sin(Math.PI*w);}
   if(effort)x+=i?-.11:.14;
  }
  feet.push({x:x,lift:lift,u:u});
 }
 // Keep the stance foot moving backward at speed, while setting the whole lean from the rear ankle.
 if(effort){
  var rear=feet[0].x<feet[1].x?0:1,lo=feet[rear].x-.05,hi=feet[rear].x+.78,desired=name==='day'?40:30;
  for(var j=0;j<20;j++){
   var hx=(lo+hi)/2,reach=Math.max.apply(null,feet.map(function(f,i){return Math.abs(f.x-(i?-.035:.035)-hx);}));
   var ly=Math.sqrt(Math.max(.01,.8396*.8396-reach*reach));
   var lean=Math.atan2(hx+.56*Math.sin(q.than*R)-feet[rear].x,ly+feet[rear].lift+.56*Math.cos(q.than*R))/R;
   if(lean<desired)lo=hx;else hi=hx;
  }
  // The rope carries some weight, but hips far past the leading foot read as falling when the swing foot passes; cap it.
  var lead=Math.max(feet[0].x-.035,feet[1].x+.035);
  so.hongX=Math.min((lo+hi)/2,lead+.12);
 }
 var maxX=Math.max.apply(null,feet.map(function(f,i){return Math.abs(f.x-(i?-.035:.035)-(so.hongX||0));}));
 var legY=Math.sqrt(Math.max(.01,.8396*.8396-maxX*maxX));
 so.hongY=.82-legY;
 ['Gan','Xa'].forEach(function(side,i){
  var f=feet[i],v=ik(f.x-(i?-.035:.035)-(so.hongX||0),legY+f.lift,.42,.42,-1);
  // Kneel: rear knee on the ground ahead of the hips, shin folded back so the hips sit on the tucked heel; front elbow rests near the front knee.
  if(name==='quy-ngam'){v=i?[-52,149]:[-113,113];so.hongY=.47;so.hongX=0;}
  q['dui'+side]=v[0];q['cangChan'+side]=v[1];q['banChan'+side]=-v[0]-v[1];
  if(name==='quy-ngam'&&i)q['banChan'+side]=-27;
  // Heel strike, then a small toe-off; planted soles stay flat through mid-stance.
  if(name==='di'||name==='chay')q['banChan'+side]+=f.u<.12?-12*(1-f.u/.12):f.u>.48&&f.u<.6?15*(f.u-.48)/.12:0;
  q['tay'+side]=moving?f.x*75:-3;
  q['cangTay'+side]=-7;
  if(name==='keo-day'){q['tay'+side]=-6-q.than+(i?6:0);q['cangTay'+side]=-124+(i?8:0);}
  if(name==='day'||name==='dat-xe'){q['tay'+side]=-84-q.than+(i?3:0);q['cangTay'+side]=-5;}
  if(name==='ghi'){q['tay'+side]=-72-q.than;q['cangTay'+side]=-8;}
 });
 q.dau=name==='keo-day'?0:name==='quy-ngam'?-14:-(q.than||0)*.45;
 // The cheek stays close to the horizontal stock in the aiming pose.
 return {tuThe:q,so:so};
}
function chuanBi(tt){
 var height=tt.bienThe.cao===undefined?1.62:tt.bienThe.cao;
 if(!Number.isFinite(height)||height<=0)throw Error('Chiều cao người phải dương, hữu hạn');
 tt.tyLeHinh=height/1.62;
 ['hongY','hongX','coY','dauY'].forEach(function(n){tt.so[n]=(tt.so[n]||0)*tt.tyLeHinh;});
 tt.tuThe.than=(tt.tuThe.than||0)+tt.doc*.85;
 tt.tuThe.dau=(tt.tuThe.dau||0)-tt.doc*.25;
 var targets=tt.bienThe.tay||tt.tayDich||{};
 if(typeof targets==='function')targets=targets(K.khung.tinh(xuong(height),tt.tuThe,tt.so));
 Object.keys(targets).forEach(function(side){
  var m=K.khung.tinh(xuong(height),tt.tuThe,tt.so),shoulder=m['tay'+side],a=m.than.goc*R;
  var dx=targets[side][0]-shoulder.x,dy=targets[side][1]-shoulder.y;
  var v=ik(Math.cos(a)*dx+Math.sin(a)*dy,-Math.sin(a)*dx+Math.cos(a)*dy,.29*tt.tyLeHinh,.285*tt.tyLeHinh,dx<0?-1:1);
  tt.tuThe['tay'+side]=v[0];tt.tuThe['cangTay'+side]=v[1];
 });
}
function cham(tt){
 var s=tt&&tt.tyLeHinh||1,bare=tt&&((tt.trangPhuc&&tt.trangPhuc.chan)||tt.bienThe.chan)==='tran';
 return ['Gan','Xa'].flatMap(function(side){return [{xuong:'banChan'+side,x:(bare?-.06:-.065)*s,y:(bare?.043:.052)*s},{xuong:'banChan'+side,x:(bare?.156:.132)*s,y:(bare?.043:.062)*s}];});
}
// Sample a closed contour: modest curvature leaves the deliberate carved facets.
function mem(b,pts,mat,tone,outline){
 var out=[];
 for(var i=0;i<pts.length;i++){
  var a=pts[(i+pts.length-1)%pts.length],c=pts[i],d=pts[(i+1)%pts.length],e=pts[(i+2)%pts.length];
  for(var j=0;j<4;j++){var t=j/4,t2=t*t,t3=t2*t;out.push([0,1].map(function(k){return .5*((2*c[k])+(-a[k]+d[k])*t+(2*a[k]-5*c[k]+4*d[k]-e[k])*t2+(-a[k]+3*c[k]-3*d[k]+e[k])*t3);}));}
 }
 b.daGiac(out,mat,tone,outline);
}
// One continuous tapered outline for both links; there is no seam at a rotating joint.
function sleeve(b,points,radii,mat,tone){
 var angles=[0,1].map(function(i){return Math.atan2(points[i+1][1]-points[i][1],points[i+1][0]-points[i][0]);});
 var turn=((angles[1]-angles[0]+Math.PI*3)%(Math.PI*2))-Math.PI,out=[];
 function arc(p,r,a,z,n){for(var j=0;j<=n;j++){var v=a+(z-a)*j/n;out.push([p[0]+Math.cos(v)*r,p[1]+Math.sin(v)*r]);}}
 for(var side of [1,-1]){
  var k=side===1?0:2,ang=angles[k===0?0:1]+side*Math.PI/2;
  out.push([points[k][0]+Math.cos(ang)*radii[k],points[k][1]+Math.sin(ang)*radii[k]]);
  var a=angles[side===1?0:1]+side*Math.PI/2,z=angles[side===1?1:0]+side*Math.PI/2;
  if(turn*side<0){if(side===1)z=a+turn;else z=a-turn;arc(points[1],radii[1],a,z,8);}
  else {var middle=angles[0]+turn/2+side*Math.PI/2,rr=radii[1]/Math.max(.42,Math.cos(turn/2));out.push([points[1][0]+Math.cos(middle)*rr,points[1][1]+Math.sin(middle)*rr]);}
  k=side===1?2:0;ang=angles[k===0?0:1]+side*Math.PI/2;
  out.push([points[k][0]+Math.cos(ang)*radii[k],points[k][1]+Math.sin(ang)*radii[k]]);
  arc(points[k],radii[k],ang,ang-Math.PI,8);
 }
 b.daGiac(out,mat,tone);
}
function ve(b,tt,clothes){
 clothes=clothes||tt.trangPhuc||{};
 var footwear=clothes.chan||tt.bienThe.chan||'dep',civil=!!tt.bienThe.danSu||clothes.ao==='dan-su',shadow=tt.khongMat,s=tt.tyLeHinh||1;
 var cloth=shadow?'bongNguoi':civil?'danSu':clothes.mauAo||'ao',trouser=shadow?'bongNguoi':civil?'danSu':clothes.quan||'quan',skin=shadow?'bongNguoi':clothes.da||'da';
 var gripping=['keo-day','day','quy-ngam','dat-xe','ghi'].indexOf(tt.bienThe.tuThe||tt.trangThai)>=0;
 function point(name,x,y){return K.khung.diem(tt.xuong[name].maTran,x*s,y*s);}
 function moon(pts,w){if(tt.dem&&!tt.bienThe.xa)b.net(pts,'bongNguoi',w||.012,'sang');}
 function leg(side,far){
  var p=[point('dui'+side,0,0),point('cangChan'+side,0,0),point('cangChan'+side,0,.375)];
  sleeve(b,p,[.085*s,.065*s,.046*s],trouser,far?'toi':'nen');
  b.xuong('dui'+side,function(){
   if(!shadow){mem(b,[[-.061,.02],[-.025,.055],[-.035,.23],[-.043,.35],[-.060,.36],[-.066,.17]],trouser,far?'nen':'sang',false);b.net([[.048,.27],[.006,.32],[.044,.34]],trouser,.007,'toi');}
   moon([[-.073,.035],[-.072,.19],[-.057,.35]],far?.007:.012);
  });
  b.xuong('cangChan'+side,function(){
   if(!shadow){mem(b,[[-.043,.03],[-.024,.08],[-.029,.23],[-.039,.34],[-.051,.33],[-.056,.16]],trouser,far?'nen':'sang',false);b.net([[.035,.018],[-.02,.035],[.027,.064]],trouser,.008,'toi');b.net([[-.045,.348],[.033,.357]],trouser,.009,'toi');}
   moon([[-.054,.045],[-.061,.17],[-.045,.35]],far?.007:.011);
  });
  b.xuong('banChan'+side,function(){
   mem(b,[[-.047,-.057],[.028,-.056],[.048,-.015],[.116,.003],[.155,.019],[.156,.043],[-.06,.043],[-.058,.007]],skin,far?'toi':'nen');
   if(footwear!=='tran')mem(b,[[-.065,.028],[.10,.032],[.166,.025],[.169,.048],[.132,.062],[-.065,.052]],shadow?'bongNguoi':'caoSu',far?'toi':'nen');
   if(footwear==='giay-vai')mem(b,[[-.055,-.065],[.03,-.065],[.06,-.02],[.14,-.005],[.166,.025],[-.06,.027]],cloth,far?'toi':'nen');
   if(!shadow&&footwear==='dep'){b.net([[-.032,-.010],[.061,.025],[.115,.008]],'caoSu',.017);b.net([[.007,.013],[.070,-.012]],'caoSu',.017);b.net([[-.044,-.017],[-.042,.026]],'caoSu',.012);}
   moon([[-.056,-.025],[-.06,.022],[.01,.027]],.009);
  });
 }
 function arm(side,far){
  var p=[point('tay'+side,0,0),point('cangTay'+side,0,0),point('cangTay'+side,0,.225)];
  sleeve(b,p,[.064*s,.047*s,.031*s],cloth,far?'toi':'nen');
  b.xuong('tay'+side,function(){
   if(!shadow){mem(b,[[-.046,.01],[-.025,.03],[-.024,.15],[-.035,.24],[-.045,.24],[-.051,.12]],cloth,far?'nen':'sang',false);b.net([[.036,.21],[-.015,.24],[.03,.26]],cloth,.007,'toi');}
   moon([[-.052,.015],[-.05,.14],[-.039,.24]],far?.007:.012);
  });
  b.xuong('cangTay'+side,function(){
   if(!shadow){b.net([[.028,.01],[-.016,.035],[.022,.060]],cloth,.007,'toi');b.net([[-.031,.203],[.031,.203]],cloth,.009,'toi');b.net([[-.028,.216],[.029,.216]],cloth,.005,'sang');}
   if(gripping){
    mem(b,[[-.028,.215],[.023,.211],[.038,.234],[.037,.272],[.022,.298],[-.012,.304],[-.034,.281],[-.035,.245]],skin,far?'toi':'nen');
    mem(b,[[.012,.24],[.045,.243],[.053,.263],[.033,.276],[.009,.27]],skin,far?'toi':'nen');
    if(!shadow){b.net([[-.018,.270],[.008,.278],[.029,.271]],skin,.006,'toi');b.net([[-.014,.286],[.012,.292]],skin,.005,'toi');}
   }else{
    mem(b,[[-.026,.213],[.026,.214],[.030,.246],[.038,.267],[.024,.296],[.002,.305],[-.019,.299],[-.028,.268]],skin,far?'toi':'nen');
    if(!shadow)b.net([[.007,.257],[.010,.285]],skin,.005,'toi');
   }
   moon([[-.037,.045],[-.032,.18]],.009);b.neo('tay'+side,0,.285);
  });
 }
 leg('Xa',true);arm('Xa',true);
 b.xuong('than',function(){
  mem(b,[[-.092,.015],[.084,.015],[.091,-.12],[.125,-.29],[.13,-.42],[.077,-.49],[-.052,-.501],[-.115,-.458],[-.13,-.36],[-.115,-.19],[-.098,-.065]],cloth,'nen');
  if(!shadow){
   mem(b,[[-.113,-.425],[-.072,-.464],[-.054,-.36],[-.061,-.23],[-.055,-.07],[-.084,-.016],[-.098,-.15]],cloth,tt.huong===1?'sang':'toi',false);
   mem(b,[[.073,-.463],[.116,-.408],[.112,-.31],[.087,-.15],[.080,-.017],[.052,-.021],[.064,-.26]],cloth,tt.huong===1?'toi':'sang',false);
   b.net([[.012,-.45],[.024,-.25],[.016,-.05]],cloth,.006,'toi');
   for(var by=-.39;by<-.07;by+=.095)b.tron(.018,by,.004,.005,'cuoi','toi',false);
   if(!civil){
    [-.083,.025].forEach(function(x){
     b.daGiac([[x,-.365],[x+.074,-.365],[x+.070,-.267],[x+.004,-.265]],cloth,'nen');
     b.daGiac([[x-.002,-.372],[x+.077,-.372],[x+.070,-.34],[x+.036,-.327],[x+.001,-.340]],cloth,'sang');
     b.tron(x+.037,-.349,.005,.005,'cuoi','toi',false);b.net([[x+.008,-.28],[x+.061,-.28]],cloth,.004,'toi');
    });
   }
   b.net([[-.088,-.10],[-.032,-.073],[.013,-.089]],cloth,.007,'toi');b.net([[.083,-.119],[.041,-.069],[.074,-.056]],cloth,.006,'toi');
   if((clothes.ao||tt.bienThe.ao)==='tran-thu'){
    for(var yy=-.40;yy<-.04;yy+=.065)b.net([[-.10,yy],[.10,yy+.02]],cloth,.007,'toi');
    for(var xx=-.07;xx<.10;xx+=.055)b.net([[xx,-.44],[xx+.016,-.04]],cloth,.007,'toi');
   }
  }
  moon([[-.095,-.025],[-.113,-.21],[-.125,-.365],[-.104,-.45],[-.06,-.49]],.014);b.neo('vai',.025,-.46);
 });
 leg('Gan',false);
 b.xuong('co',function(){mem(b,[[-.037,-.062],[.032,-.06],[.038,.001],[.017,.026],[-.034,.015]],skin,shadow?'nen':'toi');});
 b.xuong('dau',function(){
  var head=shadow?[[-.085,-.13],[-.077,-.187],[-.039,-.216],[.012,-.22],[.061,-.195],[.085,-.146],[.083,-.074],[.056,-.021],[.013,-.009],[-.043,-.036],[-.074,-.08]]:
   [[-.085,-.13],[-.077,-.187],[-.039,-.216],[.012,-.22],[.061,-.195],[.081,-.164],[.080,-.136],[.098,-.113],[.116,-.102],[.101,-.092],[.085,-.093],[.084,-.074],[.092,-.057],[.078,-.032],[.047,-.013],[.016,-.011],[-.039,-.034],[-.074,-.08]];
  mem(b,head,skin,'nen');
  if(!shadow){
   mem(b,[[-.079,-.15],[-.052,-.184],[-.044,-.136],[-.045,-.080],[-.013,-.036],[.014,-.021],[-.029,-.034],[-.063,-.065]],skin,'toi',false);
   mem(b,[[-.037,-.133],[-.014,-.137],[-.006,-.116],[-.019,-.085],[-.035,-.094]],skin,'nen');b.net([[-.025,-.116],[-.017,-.121],[-.021,-.101]],skin,.004,'toi');
   b.net([[.063,-.133],[.078,-.130]],'caoSu',.006,'toi');b.net([[.073,-.060],[.087,-.057]],skin,.004,'toi');
  }
  moon([[-.081,-.12],[-.075,-.178],[-.043,-.209]],.011);
 });
 b.xuong('than',function(){
  if(!civil){
   mem(b,[[-.096,-.043],[.089,-.045],[.094,-.006],[-.097,-.002]],shadow?'bongNguoi':'cuoi','nen');
   if(!shadow)b.hop(.015,-.041,.036,.034,'thep','nen');
  }
  if(!shadow){b.daGiac([[-.055,-.498],[.009,-.46],[-.026,-.425],[-.070,-.474]],cloth,'sang');b.daGiac([[.044,-.498],[.009,-.46],[.045,-.427],[.075,-.475]],cloth,'nen');}
 });
 arm('Gan',false);
}
K.nguoi={xuong:xuong,ik:ik,tuThe:tuThe,chuanBi:chuanBi,diemCham:cham,ve:ve};
})(typeof window!=='undefined'?window:globalThis);
