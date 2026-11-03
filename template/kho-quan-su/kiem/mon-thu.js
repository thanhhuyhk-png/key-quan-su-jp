/* Plug-in fixture: loaded only by the checker, never by the review page. */
(function(g){
'use strict';
g.Kho.dangKy({ma:'mon-thu',ten:'Món thử đăng ký độc lập',phe:'thu',thoiKy:'thu',
 kichThuoc:{dai:1,cao:.5},bangMau:{vat:{nen:'#736A50',toi:'#494333',sang:'#AA9B72'}},
 xuong:[{ten:'goc',x:0,y:0}],thamSoMacDinh:{},diemCham:[{x:0,y:0}],
 trangThai:{
  dung:{chuKy:1,lap:true,khung:[{p:0,tuThe:{goc:0},so:{nang:0}},{p:1,tuThe:{goc:0},so:{nang:0}}]},
  nghieng:{chuKy:1,lap:true,khung:[{p:0,tuThe:{goc:170},so:{nang:0}},{p:.5,tuThe:{goc:-170},so:{nang:.1}},{p:1,tuThe:{goc:170},so:{nang:0}}]},
  truot:{chuKy:2,lap:true,tocDo:.2,tuThe:function(p){return {so:{nang:p*.1}};}}
 },
 ve:function(b,tt){b.xuong('goc',function(){b.hop(-.5,-.5-tt.so.nang,1,.5,'vat','nen');b.neo('dinh',0,-.5-tt.so.nang);});}
});
})(typeof window!=='undefined'?window:globalThis);
