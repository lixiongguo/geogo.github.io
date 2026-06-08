#!/usr/bin/env python3
"""批量上传图片到阿里云 OSS（需设置环境变量 OSS_ACCESS_KEY_ID / OSS_ACCESS_KEY_SECRET）"""
import oss2, sys, time, os
from pathlib import Path

AK = os.environ.get("OSS_ACCESS_KEY_ID", "")
SK = os.environ.get("OSS_ACCESS_KEY_SECRET", "")
ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "scripts" / "oss_upload_manifest.txt"
IMGS = ROOT / "imgs"

CT = {'.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg',
       '.gif':'image/gif','.webp':'image/webp','.svg':'image/svg+xml'}

def main():
    if not AK or not SK:
        print("ERROR: 请设置环境变量 OSS_ACCESS_KEY_ID 和 OSS_ACCESS_KEY_SECRET")
        sys.exit(1)
    
    with open(MANIFEST) as f:
        images = [l.strip() for l in f if l.strip()]
    
    auth = oss2.Auth(AK, SK)
    bucket = oss2.Bucket(auth, 'https://oss-cn-beijing.aliyuncs.com', 'lgximgs')
    
    ok = skip = fail = exist = 0
    total = len(images)
    
    for i, img in enumerate(images):
        lp = IMGS / img
        if not lp.exists():
            print(f"[{i+1}/{total}] SKIP_MISS {img}")
            skip += 1; continue
        
        # 检查是否已在 OSS 上存在
        already_there = False
        for _ in range(2):
            try:
                bucket.head_object('images/' + img)
                already_there = True; break
            except oss2.exceptions.NoSuchKey:
                break
            except: time.sleep(1)
        
        if already_there:
            print(f"[{i+1}/{total}] EXIST {img}")
            exist += 1; continue
        
        ct = CT.get(lp.suffix.lower(), 'application/octet-stream')
        for attempt in range(4):
            try:
                bucket.put_object_from_file('images/' + img, str(lp), headers={'Content-Type': ct})
                print(f"[{i+1}/{total}] OK {img}" + (f" (r{attempt+1})" if attempt else ""))
                ok += 1; break
            except Exception as e:
                if attempt < 3: time.sleep(2 ** attempt)
                else: print(f"[{i+1}/{total}] FAIL {img}: {str(e)[:80]}"); fail += 1
        
        if (i+1) % 20 == 0: time.sleep(0.5)
    
    print(f"\nDone: OK={ok} EXIST={exist} SKIP={skip} FAIL={fail} / {total}")

if __name__ == '__main__':
    main()
