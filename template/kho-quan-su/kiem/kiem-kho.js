'use strict';
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const crypto=require('node:crypto');
const root=path.resolve(__dirname,'..');
const files=['engine/kho.js','engine/khung.js','engine/but.js','engine/nguoi.js','vat-the/dbp-1954/ta/bo-doi.js','vat-the/dbp-1954/ta/phao-37.js','vat-the/dbp-1954/ta/xe-dap-tho.js'];
const noRandom=Object.create(Math);noRandom.random=()=>{throw Error('Cấm Math.random');};
const sandbox=vm.createContext({Math:noRandom,Date:function(){throw Error('Cấm Date');},requestAnimationFrame(){throw Error('Cấm RAF');}});
const digest=()=>files.slice(0,4).map(f=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,f))).digest('hex'));
function load(f){vm.runInContext(fs.readFileSync(path.join(root,f),'utf8'),sandbox,{filename:f});}
files.forEach(load);
const K=sandbox.Kho, times=[0,.37,1.2,2.5], variants=[{}, {dem:true},{nguyTrang:1},{khongMat:true,dem:true}];
const identity=[1,0,0,1,0,0];
function mul(a,b){return [a[0]*b[0]+a[2]*b[1],a[1]*b[0]+a[3]*b[1],a[0]*b[2]+a[2]*b[3],a[1]*b[2]+a[3]*b[3],a[0]*b[4]+a[2]*b[5]+a[4],a[1]*b[4]+a[3]*b[5]+a[5]];}
class Context{
 constructor(){this.log=[];this.points=[];this.matrix=identity.slice();this.stack=[];this.texts=0;this.lineWidth=1;}
 record(name,args){const a=Array.from(args);a.forEach(v=>{if(typeof v==='number')assert(Number.isFinite(v),name+' có số vô hạn');});this.log.push([name,...a]);}
 save(){this.record('save',[]);this.stack.push({m:this.matrix.slice(),w:this.lineWidth});}
 restore(){this.record('restore',[]);assert(this.stack.length,'Restore lệch save');const s=this.stack.pop();this.matrix=s.m;this.lineWidth=s.w;}
 transform(...a){this.record('transform',a);this.matrix=mul(this.matrix,a);}
 setTransform(...a){this.record('setTransform',a);this.matrix=a;}
 translate(x,y){this.transform(1,0,0,1,x,y);}
 scale(x,y){this.transform(x,0,0,y,0,0);}
 rotate(a){this.transform(Math.cos(a),Math.sin(a),-Math.sin(a),Math.cos(a),0,0);}
 beginPath(){this.record('beginPath',[]);}
 closePath(){this.record('closePath',[]);}
 point(x,y){const m=this.matrix;this.points.push([m[0]*x+m[2]*y+m[4],m[1]*x+m[3]*y+m[5]]);}
 moveTo(x,y){this.record('moveTo',arguments);this.point(x,y);}
 lineTo(x,y){this.record('lineTo',arguments);this.point(x,y);}
 quadraticCurveTo(...a){this.record('quadraticCurveTo',a);this.point(a[0],a[1]);this.point(a[2],a[3]);}
 ellipse(x,y,rx,ry,a,start,end){this.record('ellipse',arguments);assert(rx>=0&&ry>=0);for(let j=0;j<=32;j++){const v=start+(end-start)*j/32;this.point(x+rx*Math.cos(v),y+ry*Math.sin(v));}}
 arc(x,y,r,start,end){this.ellipse(x,y,r,r,0,start,end);}
 fill(...a){this.record('fill',[this.fillStyle,...a]);}
 stroke(){this.record('stroke',[this.strokeStyle,this.lineWidth]);}
 fillText(...a){this.texts++;this.record('fillText',a);}
 strokeText(...a){this.texts++;this.record('strokeText',a);}
}
function ctx(){return new Context();}
function checkRect(b){['trai','phai','tren','duoi'].forEach(k=>assert(Number.isFinite(b[k]),k));assert(b.phai>b.trai&&b.duoi>b.tren);}
let failed=0,totalDraws=0,textCount=0;
function test(n,title,fn){try{const detail=fn();console.log(n+'. ĐẠT | '+title+(detail?' | '+detail:''));}catch(e){failed++;console.log(n+'. KHÔNG ĐẠT | '+title+' | '+e.message);}}
console.log('KIỂM KHO ĐỒ HOẠ QUÂN SỰ');
test(1,'Đăng ký và số trạng thái',()=>{
 const list=K.danhSach();assert.equal(list.length,3);
 for(const [ma,min] of [['bo-doi',5],['phao-37',5],['xe-dap-tho',4]])assert(list.find(d=>d.ma===ma).trangThai.length>=min);
 return '3 món; 5 / 5 / 4 trạng thái';
});
test(2,'Vẽ toàn ma trận, tọa độ và neo hữu hạn',()=>{
 for(const item of K.danhSach())for(const state of item.trangThai)for(const v of variants)for(const t of times){
  const c=ctx(),p={...v,trangThai:state,t,bong:false};
  const result=K.ve(c,item.ma,p);totalDraws++;textCount+=c.texts;checkRect(result.khung);
  assert(c.points.length>50,'Hình quá ít nét');assert.equal(c.stack.length,0);
  for(const point of c.points){assert(point[0]>=result.khung.trai-.01&&point[0]<=result.khung.phai+.01,'Nét vượt khung ngang');assert(point[1]>=result.khung.tren-.01&&point[1]<=result.khung.duoi+.01,'Nét vượt khung dọc');}
  for(const point of Object.values(result.neo))assert(point.every(Number.isFinite),'Neo không hữu hạn');
 }
 for(const ma of ['bo-doi','phao-37','xe-dap-tho'])for(const huong of [-1,1])for(const doc of [-12,12]){
  const c=ctx(),result=K.ve(c,ma,{huong,doc,t:.37,x:173,y:481,pxMoiMet:157,bong:false,tron:{tu:K.danhSach().find(d=>d.ma===ma).trangThai[1],p:.5}});
  checkRect(result.khung);for(const point of c.points)assert(point[0]>=result.khung.trai-.01&&point[0]<=result.khung.phai+.01&&point[1]>=result.khung.tren-.01&&point[1]<=result.khung.duoi+.01);
 }
 assert.throws(()=>K.ve(ctx(),'bo-doi',{t:NaN}));assert.throws(()=>K.ve(ctx(),'bo-doi',{pxMoiMet:0}));
 return totalDraws+' lượt cơ bản + dốc / lật / trộn';
});
test(3,'Tỉ lệ mét từ hình học thực',()=>{
 const h=K.doKhung('bo-doi',{trangThai:'dung'});const height=h.duoi-h.tren;assert(height>=1.62&&height<=1.80,'Người cao '+height);
 const p=K.doKhung('phao-37',{trangThai:'keo'});const length=p.phai-p.trai;assert(Math.abs(length-6.2)<=.3,'Pháo dài '+length);assert(p.duoi-p.tren<=2.6,'Pháo quá cao');
 const b=K.doKhung('xe-dap-tho',{trangThai:'dat'});assert(b.phai-b.trai>=1.7&&b.phai-b.trai<=2,'Xe dài '+(b.phai-b.trai));
 const diam=K._tinh('xe-dap-tho',{}).tt.so.banKinhBanh*2;assert(diam>=.68&&diam<=.74);
 // Verify tyre geometry actually uses the declared radius.
 const original=K.but.tao;let maxRadius=0;
 K.but.tao=function(...args){const painter=original(...args),draw=painter.daGiac,at=painter.tai;let inWheel=false;painter.tai=function(x,y,a,...rest){const old=inWheel;inWheel=Math.abs(Math.abs(x)-.57)<1e-8&&Math.abs(y+.355)<1e-8;try{return at.call(painter,x,y,a,...rest);}finally{inWheel=old;}};painter.daGiac=function(points,...rest){if(inWheel&&rest[0]==='banh')for(const point of points)maxRadius=Math.max(maxRadius,Math.hypot(point[0],point[1]));return draw.call(painter,points,...rest);};return painter;};
 try{K.ve(ctx(),'xe-dap-tho',{});}finally{K.but.tao=original;}
 assert(Math.abs(maxRadius-.355)<.00001,'Bán kính lốp không khớp nét');
 return 'người '+height.toFixed(3)+' m; pháo '+length.toFixed(3)+' m; xe '+(b.phai-b.trai).toFixed(3)+' m; bánh '+diam.toFixed(2)+' m';
});
test(4,'Chạm đất, gồm dốc hai hướng',()=>{
 let gap=0;
 for(const state of ['dung','di','keo-day','day'])for(const t of times)for(const doc of [0,12,-12])for(const huong of [1,-1]){
  const tt=K._tinh('bo-doi',{trangThai:state,t,doc,huong}).tt;
  const distances=tt.chamDat.map(p=>{const q=K.khung.diem(tt.maTranCanh,p[0],p[1]);return q[1]+Math.tan(doc*Math.PI/180)*huong*q[0];});
  const low=Math.max(...distances);gap=Math.max(gap,Math.abs(low));assert(Math.abs(low)<=.01);
  assert(distances.every(d=>d<=.01),'Chân xuyên nền');
 }
 for(const ma of ['phao-37','xe-dap-tho'])for(const state of K.danhSach().find(d=>d.ma===ma).trangThai)for(const t of times){const tt=K._tinh(ma,{trangThai:state,t}).tt;assert(Math.abs(Math.max(...tt.chamDat.map(p=>p[1])))<.01);}
 // Posture checks use solved joints, so a passing ground test cannot hide a crouched standing figure.
 const standing=K._tinh('bo-doi',{trangThai:'dung'}).tt;
 for(const side of ['Gan','Xa'])assert(Math.abs(standing.tuThe['cangChan'+side])<=5,'Đứng còn khuỵu gối');
 // Lean from the rear ankle must dip while the swing foot passes the stance foot, so check the cycle mean,
 // a floor, and that a supporting foot always stays near the hips (no "falling" frame).
 for(const state of ['keo-day','day']){
  let sum=0;
  for(let i=0;i<80;i++){
   const b=K._tinh('bo-doi',{trangThai:state,t:i*.02}).tt.xuong;
   const rear=b.banChanGan.x<b.banChanXa.x?b.banChanGan:b.banChanXa;
   const lean=Math.atan2(b.dau.x-rear.x,rear.y-b.dau.y)*180/Math.PI;
   assert(lean>=15,state+' đổ quá ít '+lean);
   assert(Math.max(b.banChanGan.x,b.banChanXa.x)-b.hong.x>=-.15,state+' hông vượt chân trước quá 0,15 m');
   sum+=lean;
  }
  const mean=sum/80,range=state==='keo-day'?[25,35]:[30,45];
  assert(mean>=range[0]&&mean<=range[1],state+' đổ trung bình '+mean);
 }
 const kneel=K._tinh('bo-doi',{trangThai:'quy-ngam'}).tt.xuong;
 assert(-kneel.cangChanXa.y<=.13,'Quỳ: tâm gối sau quá cao so với đất');
 assert(-kneel.hong.y>=.30&&-kneel.hong.y<=.45,'Quỳ: hông phải ngồi trên gót sau');
 const aiming=K._tinh('bo-doi',{trangThai:'quy-ngam'}).tt.xuong;
 assert(Math.abs(aiming.banChanGan.x-aiming.cangChanGan.x)<.001,'Cẳng chân trước khi quỳ không thẳng đứng');
 assert(Math.abs(aiming.cangChanXa.y-aiming.banChanGan.y)<.01,'Gối sau chưa xuống đất');
 assert(Math.hypot(aiming.cangTayXa.x-aiming.cangChanGan.x,aiming.cangTayXa.y-aiming.cangChanGan.y)<.115,'Khuỷu trước chưa tựa vào đùi');
 // During stance, translating the root at the state speed must pin the heel horizontally.
 for(const [state,speed] of [['di',.65],['keo-day',.30],['day',.28]]){
  const t=.20,dt=.001,a=K._tinh('bo-doi',{trangThai:state,t}).tt.xuong.banChanGan;
  const b=K._tinh('bo-doi',{trangThai:state,t:t+dt}).tt.xuong.banChanGan;
  assert(Math.abs((b.x-a.x)/dt+speed)<.002,state+' trượt chân trụ');
 }
 return 'sai số lớn nhất '+(gap*100).toFixed(6)+' cm; tư thế / chân trụ đạt';
});
test(5,'Món không vẽ chữ',()=>{assert.equal(textCount,0);return 'fillText / strokeText = '+textCount;});
test(6,'Thuần theo t và RNG có hạt giống',()=>{
 for(const item of K.danhSach())for(const state of item.trangThai)for(const t of times){
  const p={trangThai:state,t,hat:73,nguyTrang:1,dem:true,doc:12,huong:-1};const a=ctx(),b=ctx();
  const ra=K.ve(a,item.ma,p),rb=K.ve(b,item.ma,p);assert.equal(JSON.stringify(a.log),JSON.stringify(b.log));assert.equal(JSON.stringify(ra),JSON.stringify(rb));
 }
 const a=K.rng(41),b=K.rng(41),c=K.rng(42);const aa=Array.from({length:8},()=>a()),bb=Array.from({length:8},()=>b()),cc=Array.from({length:8},()=>c());assert.deepEqual(aa,bb);assert.notDeepEqual(aa,cc);
 const m=K.khung.tinh([{ten:'cha',x:1,y:2,goc:90},{ten:'con',cha:'cha',x:1,y:0,lat:-1}],{},{});
 assert(Math.abs(m.con.x-1)<1e-9&&Math.abs(m.con.y-3)<1e-9);const reflected=K.khung.diem(m.con.maTran,1,0);assert(Math.abs(reflected[0]-1)<1e-9&&Math.abs(reflected[1]-2)<1e-9);assert(Math.abs(K.khung.goc(170,-170,.5)-180)<1e-9);
 return '56 cặp nhật ký trùng khớp; cấm random / Date / RAF';
});
test(7,'Thêm món độc lập không sửa engine',()=>{
 const before=digest();load('kiem/mon-thu.js');assert.equal(K.danhSach().length,4);assert.equal(K.danhSach().find(d=>d.ma==='mon-thu').trangThai.length,3);
 for(const state of ['dung','nghieng','truot']){checkRect(K.ve(ctx(),'mon-thu',{trangThai:state,t:.37}).khung);}
 const tween=K._tinh('mon-thu',{trangThai:'nghieng',t:.25}).tt;assert(Math.abs(tween.tuThe.goc-180)<1e-9);assert(Math.abs(tween.so.nang-.05)<1e-9);
 assert.deepEqual(digest(),before);return 'món thử 3 trạng thái; SHA-256 engine giữ nguyên';
});
test(8,'Bánh pháo lăn theo quãng đường',()=>{
 let error=0;
 for(const t of [.37,1.2,2.5]){
  const a=K._tinh('phao-37',{trangThai:'keo',t:0}).tt,b=K._tinh('phao-37',{trangThai:'keo',t}).tt;
  const expected=(b.quangDuong-a.quangDuong)/b.so.banKinhBanh;const actual=b.so.gocBanh-a.so.gocBanh;
  error=Math.max(error,Math.abs(actual-expected)/expected);assert(error<=.01);
  const original=K.but.tao,angles=[];
  K.but.tao=function(...args){const painter=original(...args),draw=painter.tai;painter.tai=function(x,y,angle,...rest){if(Math.abs(Math.abs(x)-1.5)<1e-8&&Math.abs(y+.47)<1e-8)angles.push(angle*Math.PI/180);return draw.call(painter,x,y,angle,...rest);};return painter;};
  try{K.ve(ctx(),'phao-37',{trangThai:'keo',t});}finally{K.but.tao=original;}
  assert.equal(angles.length,2);for(const angle of angles)assert(Math.abs(angle-expected)/expected<=.01,'Góc vẽ bánh khác góc vật lý');
 }
 return 'sai số '+(error*100).toFixed(6)+'%; kiểm cả góc vẽ';
});
console.log('KẾT QUẢ: '+(8-failed)+'/8 ĐẠT');
process.exitCode=failed?1:0;
