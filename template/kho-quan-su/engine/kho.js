/* Geometry in metres; Canvas coordinates: x right, y down. Classic script. */
(function(g){
'use strict';
var K=g.Kho=g.Kho||{}, registry=new Map();
function finite(v,name){if(typeof v!=='number'||!Number.isFinite(v))throw Error(name+' phải hữu hạn');return v;}
function clamp(v,a,b){return Math.max(a,Math.min(b,v));}
function rng(seed){var s=(Number(seed)>>>0)||0x9e3779b9;return function(){s+=0x6d2b79f5;var v=s;v=Math.imul(v^v>>>15,v|1);v^=v+Math.imul(v^v>>>7,v|61);return ((v^v>>>14)>>>0)/4294967296;};}
function mau(hex,night,tone){
 if(!night)return hex;
 if(tone==='sang')return '#5E6F86';
 var raw=hex.replace('#','');if(raw.length===3)raw=raw.split('').map(function(v){return v+v;}).join('');
 var rgb=[0,2,4].map(function(i){return parseInt(raw.slice(i,i+2),16);});
 var gray=rgb[0]*.2126+rgb[1]*.7152+rgb[2]*.0722, blue=[26,36,51];
 return '#'+rgb.map(function(c,i){return Math.round((c*.4+gray*.6)*.35*.6+blue[i]*.4).toString(16).padStart(2,'0');}).join('');
}
function state(def,name,t){
 var st=def.trangThai[name];if(!st)throw Error('Trạng thái không có: '+name);
 var period=st.chuKy||1, p=st.lap?((t%period)+period)%period/period:clamp(t/period,0,1);
 var value={tuThe:{},so:{}};
 if(st.khung){
  var frames=st.khung;
  var a=frames[0], b=frames[frames.length-1];
  for(var i=0;i<frames.length-1;i++)if(p>=frames[i].p&&p<=frames[i+1].p){a=frames[i];b=frames[i+1];break;}
  if(p<=frames[0].p)b=a=frames[0];
  if(p>=frames[frames.length-1].p)b=a=frames[frames.length-1];
  var u=a===b?0:(p-a.p)/(b.p-a.p);u=u*u*(3-2*u);
  value={tuThe:K.khung.tron(a.tuThe||{},b.tuThe||{},u,true),so:K.khung.tron(a.so||{},b.so||{},u,false)};
 }else if(st.tuThe){
  var v=typeof st.tuThe==='function'?st.tuThe(p,t):st.tuThe;
  value=v.tuThe||v.so?{tuThe:v.tuThe||{},so:v.so||{}}:{tuThe:v,so:{}};
 }
 return {tuThe:value.tuThe,so:value.so,p:p,quangDuong:(st.tocDo||0)*t};
}
function tinh(ma,input){
 var def=registry.get(ma);if(!def)throw Error('Món không có: '+ma);
 var par=Object.assign({t:0,x:0,y:0,pxMoiMet:100,huong:1,dem:false,khongMat:false,doc:0,hat:1,bienThe:{},vien:true,bong:true},input||{});
 ['t','x','y','pxMoiMet','doc','hat'].forEach(function(k){finite(par[k],k);});
 if(par.pxMoiMet<=0)throw Error('pxMoiMet phải dương');
 if(par.huong!==1&&par.huong!==-1)throw Error('huong phải là 1 hoặc -1');
 par.trangThai=par.trangThai||Object.keys(def.trangThai)[0];
 par.nguyTrang=clamp(par.nguyTrang===undefined?(def.trangThai[par.trangThai]||{}).nguyTrang||0:finite(par.nguyTrang,'nguyTrang'),0,1);
 var pose=state(def,par.trangThai,par.t);
 if(par.tron){
  var from=state(def,par.tron.tu,par.t), mix=clamp(finite(par.tron.p,'tron.p'),0,1);mix=mix*mix*(3-2*mix);
  pose.tuThe=K.khung.tron(from.tuThe,pose.tuThe,mix,true);pose.so=K.khung.tron(from.so,pose.so,mix,false);
  pose.quangDuong=from.quangDuong+(pose.quangDuong-from.quangDuong)*mix;
 }
 var tt=Object.assign({},par,pose);tt.so=Object.assign({},def.thamSoMacDinh,pose.so);tt.neo={};tt.bangMau={};
 Object.keys(def.bangMau).forEach(function(k){var c=def.bangMau[k];tt.bangMau[k]={};['nen','toi','sang'].forEach(function(t){tt.bangMau[k][t]=mau(c[t],par.dem,t);});});
 if(def.chuanBi)def.chuanBi(tt);
 tt.xuong=K.khung.tinh(typeof def.xuong==='function'?def.xuong(tt):def.xuong,tt.tuThe,tt.so);
 var contacts=typeof def.diemCham==='function'?def.diemCham(tt):def.diemCham;
 tt.chamDat=(contacts||[]).map(function(c){var p=c.xuong?K.khung.diem(tt.xuong[c.xuong].maTran,c.x||0,c.y||0):[c.x||0,c.y||0];return [p[0],p[1]+(c.r||0)];});
 var low=tt.chamDat.length?Math.max.apply(null,tt.chamDat.map(function(p){return p[1];})):0;
 tt.doDoiY=-low; tt.chamDat=tt.chamDat.map(function(p){return [p[0],p[1]-low];});
 Object.keys(tt.xuong).forEach(function(k){var b=tt.xuong[k];b.maTran[5]-=low;b.y-=low;});
 tt.maTranCanh=[par.huong*Math.cos(par.doc*K.khung.rad),-Math.sin(par.doc*K.khung.rad),par.huong*Math.sin(par.doc*K.khung.rad),Math.cos(par.doc*K.khung.rad),0,0];
 return {def:def,tt:tt};
}
function paint(ctx,ma,params){
 var calculated=tinh(ma,params),tt=calculated.tt,def=calculated.def;
 var painter=K.but.tao(ctx,tt,def);
 if(ctx){
  ctx.save();ctx.translate(tt.x,tt.y);
  var m=tt.maTranCanh,s=tt.pxMoiMet;ctx.transform(m[0]*s,m[1]*s,m[2]*s,m[3]*s,0,0);
  if(tt.bong){ctx.save();ctx.fillStyle=tt.dem?'rgba(0,0,0,.28)':'rgba(30,27,20,.14)';ctx.beginPath();ctx.ellipse(0,.015,(def.kichThuoc.dai||1)*.38,.045,0,0,2*Math.PI);ctx.fill();ctx.restore();}
 }
 try{
  def.ve(painter,tt);
  (def.diemLa||[]).forEach(function(c,i){if(tt.nguyTrang>0)painter.xuong(c.xuong,function(){painter.la(c.x,c.y,c.r,tt.hat+i*131,tt.nguyTrang);});});
 }finally{if(ctx)ctx.restore();}
 if(!Number.isFinite(painter.khung.trai))throw Error('Món không vẽ hình');
 return {tt:tt,bounds:painter.khung};
}
K.dangKy=function(def){
 if(!def||!def.ma||registry.has(def.ma))throw Error('Mã thiếu hoặc trùng');
 if(!def.ve||!def.xuong||!def.bangMau||!def.kichThuoc||!def.trangThai||!Object.keys(def.trangThai).length)throw Error('Định nghĩa thiếu hợp đồng');
 registry.set(def.ma,def);
};
K.danhSach=function(){return Array.from(registry.values(),function(d){return {ma:d.ma,ten:d.ten,phe:d.phe,trangThai:Object.keys(d.trangThai)};});};
K.doKhung=function(ma,p){return paint(null,ma,p).bounds;};
K.ve=function(ctx,ma,p){
 if(!ctx)throw Error('Thiếu Canvas context');
 var result=paint(ctx,ma,p),tt=result.tt;
 function screen(q){var v=K.khung.diem(tt.maTranCanh,q[0],q[1]);return [tt.x+v[0]*tt.pxMoiMet,tt.y+v[1]*tt.pxMoiMet];}
 var neo={};Object.keys(tt.neo).forEach(function(k){neo[k]=screen(tt.neo[k]);});
 var b=result.bounds, corners=[[b.trai,b.tren],[b.phai,b.tren],[b.phai,b.duoi],[b.trai,b.duoi]].map(screen);
 return {neo:neo,khung:{trai:Math.min.apply(null,corners.map(function(v){return v[0];})),phai:Math.max.apply(null,corners.map(function(v){return v[0];})),tren:Math.min.apply(null,corners.map(function(v){return v[1];})),duoi:Math.max.apply(null,corners.map(function(v){return v[1];}))}};
};
K.rng=rng;K.mau=mau;
// Internal diagnostic: tests inspect solved contacts and wheel angles, not declared sizes.
K._tinh=tinh;
})(typeof window!=='undefined'?window:globalThis);
