import json,subprocess,sys,os
out='E:/Goha-JP/output/261111-nihonkai-kaisen-1905/hinh/bd3d-test/'
os.makedirs(out,exist_ok=True)
shots={'hanh-trinh':8,'ba-eo-bien':6,'phat-hien-suong':6,'doi-dau':6,'khoa-dau-15v11':6,'luoi-lua':6,'dem-tau-phong-loi':6,'truy-kich':6,'the-gioi':6,'hoi-chuyen-u':6}
for n,d in shots.items():
    if len(sys.argv)>1 and n not in sys.argv[1:]: continue
    html=open('ban-do-3d.html',encoding='utf-8').read().replace("window.SHOT=window.SHOT||{shot:'hoi-chuyen-u',duration:6};",f"window.SHOT={{shot:'{n}',duration:{d}}};")
    open(f'_t_{n}.html','w',encoding='utf-8').write(html)
    r=subprocess.run(['node','D:/GOHA/GohaKit-JP/tools/kit/dung-trang.mjs',f'_t_{n}.html','--stills',f'0.3,{d*0.5:.2f},{d-0.1:.2f}','--out-dir',out+n],capture_output=True,text=True,encoding='utf-8')
    print(n,'OK' if r.returncode==0 else 'LỖI '+r.stderr[-400:])
