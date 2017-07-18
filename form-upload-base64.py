#!/usr/bin/python
# -*- coding:utf-8 -*-
import hashlib
import base64
import json
import hashlib
import datetime
import requests
import time
import json

DEFAULT_CHUNKSIZE = 8192

bucket = '' #空间名
secret = '' #表单密钥
expiration = int(time.time())+8000 # 过期时间
uploadfile = '' #上传文件的路径
save_key = '/{year}/{mon}/{day}/upload_{random32}{.suffix}' #在UPYUN空间的保存路径
content_type = "video/mp4" # 文件类型

# md5计算
def make_content_md5(value, chunksize=DEFAULT_CHUNKSIZE):
    if hasattr(value, 'fileno'):
        md5 = hashlib.md5()
        for chunk in iter(lambda: value.read(chunksize), b''):
            md5.update(chunk)
        value.seek(0)
        return md5.hexdigest()
    elif isinstance(value, bytes) or (not PY3 and
                                      isinstance(value, builtin_str)):
        return hashlib.md5(value).hexdigest()
    else:
        raise UpYunClientException('object type error')

# 计算 policy
def make_policy(data):
    policy = json.dumps(data)
    return base64.b64encode(policy)

#上传
def upload():
    data = {'bucket': bucket,
            'expiration': expiration,
            'save-key': save_key,
            'content-type':content_type,
            'b64encoded': 'on',
           }
    policy = make_policy(data)
    signature = make_content_md5(policy + '&' + secret) # 计算签名
    print "---------计算签名完成，准备上传参数----------------"
    with open(uploadfile, 'rb') as value:
        value = base64.b64encode(value.read());
        postdata = {'policy': policy,
                    'signature': signature,
                    'file': value,
                    }
        print "---------准备请求参数完成，开始上传----------------"     
        r = requests.post("http://v0.api.upyun.com/file201503", files=postdata)
        if r.status_code == 200:
            print "---------文件上传成功，正在模拟是否可以访问----------------"
            uploadinfo = json.loads(r.text)
            headurl = "http://"+bucket+".b0.upaiyun.com"+uploadinfo["url"]
            print "---------模拟访问完成，以下是访问结果----------------"
            r = requests.head(headurl)
            if r.status_code == 200:
                print "---------文件可以访问，访问地址是:"
                print headurl
            elif requests == 404:
                print "---------文件访问404,由于 CDN 缓存问题，您可以稍后用浏览器尝试访问，您的地址:"
                print headurl

        else :
            print "文件上传失败" 

if __name__ == "__main__":
    upload()