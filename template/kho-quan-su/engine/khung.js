(function (g) {
'use strict';
var K = g.Kho = g.Kho || {};
var rad = Math.PI / 180;
function nhan(a,b) {
 return [a[0]*b[0]+a[2]*b[1],a[1]*b[0]+a[3]*b[1],
 a[0]*b[2]+a[2]*b[3],a[1]*b[2]+a[3]*b[3],
 a[0]*b[4]+a[2]*b[5]+a[4],a[1]*b[4]+a[3]*b[5]+a[5]];
}
function diem(m,x,y) { return [m[0]*x+m[2]*y+m[4],m[1]*x+m[3]*y+m[5]]; }
function goc(a,b,p) { var d=((b-a+180)%360+360)%360-180; return a+d*p; }
function tron(a,b,p,angle) {
 var out={}; Object.keys(Object.assign({},a,b)).forEach(function(k) {
 var x=a[k]===undefined?0:a[k], y=b[k]===undefined?0:b[k];
 out[k]=angle?goc(x,y,p):x+(y-x)*p;
 }); return out;
}
function tinh(ds,pose,so) {
 var out={}, visiting={};
 var by={}; ds.forEach(function(b){if(by[b.ten])throw Error('Trùng xương '+b.ten);by[b.ten]=b;});
 function visit(name) {
  if(out[name])return out[name];
  var b=by[name]; if(!b)throw Error('Thiếu xương '+name);
  if(visiting[name])throw Error('Chu trình xương '+name); visiting[name]=true;
  var a=((b.goc||0)+(pose[name]||0))*rad, f=b.lat===-1?-1:1;
  var m=[Math.cos(a)*f,Math.sin(a)*f,-Math.sin(a),Math.cos(a),b.x||0,b.y||0];
  if(so && so[name+'Y']!==undefined)m[5]+=so[name+'Y'];
  if(so && so[name+'X']!==undefined)m[4]+=so[name+'X'];
  if(b.cha)m=nhan(visit(b.cha).maTran,m);
  var v={maTran:m,x:m[4],y:m[5],goc:Math.atan2(m[1],m[0])/rad};
  out[name]=v; delete visiting[name]; return v;
 }
 ds.forEach(function(b){visit(b.ten);}); return out;
}
K.khung={nhan:nhan,diem:diem,goc:goc,tron:tron,tinh:tinh,rad:rad};
})(typeof window!=='undefined'?window:globalThis);
