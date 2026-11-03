(function(g){
'use strict';var K=g.Kho;
var palette={
 ao:{nen:'#5B6B3A',toi:'#3D492A',sang:'#82905C'},quan:{nen:'#59613B',toi:'#363D28',sang:'#78815A'},
 da:{nen:'#B98A62',toi:'#805B42',sang:'#C9A17A'},mu:{nen:'#55663A',toi:'#354629',sang:'#899765'},
 caoSu:{nen:'#252822',toi:'#171B17',sang:'#535A49'},cuoi:{nen:'#62513A',toi:'#3D3528',sang:'#93805A'},
 go:{nen:'#7A5A36',toi:'#493620',sang:'#9F7A49'},thep:{nen:'#50584C',toi:'#292F2A',sang:'#8C9580'},
 la:{nen:'#56703A',toi:'#3F5A2A',sang:'#6E7F3E'},tre:{nen:'#B39A5B',toi:'#78663B',sang:'#C7B47A'},
 bongNguoi:{nen:'#252B2A',toi:'#252B2A',sang:'#252B2A'},danSu:{nen:'#4B4B3F',toi:'#30342E',sang:'#747568'}
};
function sung(b,type,aim){
 var k24=type==='k24', wood='go', metal='thep';
 b.daGiac(aim?[[-.34,.12],[-.35,.045],[-.28,.033],[-.18,-.015],[-.08,-.047],[.15,-.035],[.18,.026],[-.17,.042],[-.27,.112]]:[[-.47,.055],[-.43,-.025],[-.18,-.015],[-.08,-.047],[.15,-.035],[.18,.026],[-.17,.042],[-.30,.085]],wood,'nen');
 b.daGiac(aim?[[-.337,.114],[-.28,.104],[-.20,.02],[-.15,.027],[-.27,.112]]:[[-.46,.055],[-.32,.062],[-.20,.02],[-.15,.027],[-.29,.084]],wood,'toi',false);
 for(var i=aim?3:0;i<4;i++)b.net([[-.40+i*.039,.016],[-.36+i*.039,.035],[-.31+i*.026,.028]],wood,.006);
 b.hop(-.17,-.061,.34,.066,metal,'nen');
 b.hop(.15,-.052,k24?.48:.27,.044,metal,'nen');
 b.hop(k24?.60:.40,-.056,.07,.04,metal,'toi');
 b.hop(.39,-.077,.025,.027,metal,'toi');
 if(!k24){
  // Curved box magazine, never a circular drum.
  b.daGiac([[-.016,.009],[.041,.009],[.063,.083],[.105,.171],[.05,.189],[.006,.105]],metal,'toi');
  b.net([[.035,.04],[.052,.108],[.077,.165]],metal,.008);
  for(var j=0;j<7;j++)b.tron(.175+j*.031,-.028,.008,.009,metal,'toi',false);
  b.net([[.16,-.047],[.40,-.047]],metal,.007);
 }else{
  b.daGiac([[-.13,-.035],[.40,-.038],[.41,.008],[-.13,.018]],wood,'nen');
  b.net([[-.09,-.019],[.35,-.018]],wood,.006);
 }
 b.net([[-.13,.039],[-.13,.092],[-.064,.092],[-.045,.037]],metal,.012);
 b.hop(-.14,-.074,.065,.014,metal,'toi');
 b.net([[-.09,-.049],[-.09,-.091],[-.046,-.092]],metal,.010);
}
function ve(b,tt){
 var civil=tt.bienThe.danSu;
 var type=tt.bienThe.sung||'k50';
 // Weapon on the back sits behind the near arm and torso.
 if(type!=='khong'&&!civil&&tt.trangThai!=='quy-ngam')b.xuong('than',function(){
  b.tai(-.08,-.24,-117,1,function(){sung(b,type);});
 });
 K.nguoi.ve(b,tt);
 if((tt.bienThe.tuThe||tt.trangThai)==='keo-day'){
  b.net([tt.neo.vai,tt.neo.tayXa,tt.neo.tayGan],'cuoi',.013,tt.dem?'sang':'nen');
  b.xuong('cangTayGan',function(){b.tron(.018,.262,.019,.015,tt.khongMat?'bongNguoi':'da','nen');});
 }
 if(!civil){
  b.xuong('dau',function(){
   var mat=tt.khongMat?'bongNguoi':'mu';
   b.tai(0,.04,0,1,function(){
   b.daGiac([[-.15,-.206],[-.107,-.307],[.063,-.321],[.125,-.28],[.153,-.205]],mat,'nen');
   b.daGiac([[-.182,-.208],[-.13,-.23],[.142,-.224],[.198,-.197],[.174,-.177],[-.16,-.182]],mat,'nen');
   if(!tt.khongMat){
    b.daGiac([[-.13,-.25],[-.107,-.30],[-.05,-.311],[-.076,-.232]],mat,tt.huong===1?'sang':'toi',false);
    for(var j=0;j<6;j++){
     var xx=-.12+j*.045;
     b.net([[xx,-.218],[xx+.018,-.285]],'tre',.006);
    }
    for(var h=0;h<4;h++){
     var yy=-.237-h*.021;
     b.net([[-.122+h*.009,yy],[.119-h*.013,yy-.008]],mat,.008);
    }
    for(var z=0;z<5;z++){
     var x=-.12+z*.048;
     b.net([[x,-.23],[x+.055,-.292]],'cuoi',.005);
     b.net([[x,-.283],[x+.058,-.226]],'cuoi',.005);
    }
    b.net([[-.08,-.183],[-.057,-.015],[.067,-.025],[.12,-.185]],'cuoi',.011);
    var star=[];for(var v=0;v<10;v++){var a=-Math.PI/2+v*Math.PI/5,r=v%2?.011:.026;star.push([.095+Math.cos(a)*r,-.264+Math.sin(a)*r]);}
    b.daGiac(star,mat,'sang',false);
    b.la(-.087,-.27,.065,tt.hat+307,.16);
   }
   if(tt.nguyTrang>0)b.la(-.008,-.28,.14,tt.hat+18,tt.nguyTrang*.5);
   if(tt.dem&&!tt.bienThe.xa)b.net([[-.16,-.196],[-.135,-.224],[-.108,-.30],[.06,-.314]],'bongNguoi',.014,'sang');
   });
  });
  if(!tt.khongMat)b.xuong('than',function(){b.net([[-.075,-.47],[.07,-.07]],'cuoi',.022);b.net([[-.067,-.47],[.078,-.07]],'go',.006);});
 }
 if(type!=='khong'&&!civil&&tt.trangThai==='quy-ngam')b.xuong('hong',function(){b.tai(.57,-.565,-tt.doc,1,function(){sung(b,type,true);});});
}
var states={};['dung','di','quy-ngam','keo-day','day'].forEach(function(name){
 states[name]={chuKy:1.6,lap:name!=='dung'&&name!=='quy-ngam',tocDo:{di:.65,'keo-day':.30,day:.28}[name]||0,tuThe:function(p,t){return K.nguoi.tuThe(name,p,t);}};
});
K.dangKy({ma:'bo-doi',ten:'Bộ đội chủ lực',phe:'ta',thoiKy:'dbp-1954',
 kichThuoc:{dai:.6,cao:1.62},bangMau:palette,xuong:function(tt){return K.nguoi.xuong(tt.bienThe.cao||1.62);},
 thamSoMacDinh:{},trangThai:states,
 chuanBi:function(tt){
  if(tt.bienThe.tuThe){var pose=K.nguoi.tuThe(tt.bienThe.tuThe,tt.p,tt.t);tt.tuThe=pose.tuThe;tt.so=pose.so;}
  if(tt.trangThai==='quy-ngam'&&tt.bienThe.sung!=='khong')tt.tayDich=function(bones){
   var scale=(tt.bienThe.cao||1.62)/1.62,angle=-tt.doc*Math.PI/180;
   function grip(x,y){return K.khung.diem(bones.hong.maTran,scale*(.57+Math.cos(angle)*x-Math.sin(angle)*y),scale*(-.565+Math.sin(angle)*x+Math.cos(angle)*y));}
   return {Gan:grip(-.11,.07),Xa:grip(.06,.065)};
  };
  K.nguoi.chuanBi(tt);
 },
 diemCham:K.nguoi.diemCham,diemLa:[{xuong:'than',x:-.08,y:-.38,r:.10}],
 ve:ve
});
})(typeof window!=='undefined'?window:globalThis);
