# flaskapi

## 当前开发情况

### 1. 运行命令

```bash
$ python run.py

out: 
# *** token for john: eyJhbGciOiJIUzUxMiIsImlhdCI6MTU5NTQ5NjUzOCwiZXhwIjoxNTk1NTAwMTM4fQ.eyJ1c2VybmFtZSI6ImpvaG4ifQ.A4TTcv01JXrUUF2DBX4ppZfFZN4EwOR6krWeOHJEqiQDrRh0LUjIZEZcv26gX6prDckh5HE6LbaSa9W6Mvx6ZQ

# *** token for susan: eyJhbGciOiJIUzUxMiIsImlhdCI6MTU5NTQ5NjUzOCwiZXhwIjoxNTk1NTAwMTM4fQ.eyJ1c2VybmFtZSI6InN1c2FuIn0.8Pk5N2Vc0FZdlKqvSRaS3vbWg7XSk0EQn_zeWFPZ-skI_gjXnFZlriN5GcOT5zo4c8rsvbSHUD3JpQyYivG16g

#  * Serving Flask app "run" (lazy loading)
#  * Environment: production
#    WARNING: This is a development server. Do not use it in a production deployment.
#    Use a production WSGI server instead.
#  * Debug mode: on
#  * Running on http://0.0.0.0:8888/ (Press CTRL+C to quit)
#  * Restarting with stat
# *** token for john: eyJhbGciOiJIUzUxMiIsImlhdCI6MTU5NTQ5NjUzOSwiZXhwIjoxNTk1NTAwMTM5fQ.eyJ1c2VybmFtZSI6ImpvaG4ifQ.uduzf3tgSYTAnD0nYByBp_qyVh3L9QrndjDptOsOuy9HMqGS_-2Msxz340cYVvQH03BgC2PgO3uYzg-EtoBl2Q

# *** token for susan: eyJhbGciOiJIUzUxMiIsImlhdCI6MTU5NTQ5NjUzOSwiZXhwIjoxNTk1NTAwMTM5fQ.eyJ1c2VybmFtZSI6InN1c2FuIn0.-vK1HJ4jskJtC1HZGppCF6Gq_LyyMvrhY8yv9BzS__LWE3d_PyzWIY_vR-1ciqK8GPrYxzSKu90CdjXcOx6h_A

#  * Debugger is active!
#  * Debugger PIN: 147-356-990
```

```bash
$ (base) macs@qiujiayudeMBP PycharmProjects % curl -X GET -H "Authorization: Bearer eyJhbGciOiJIUzUxMiIsImlhdCI6MTU5NTQ5NjUzOSwiZXhwIjoxNTk1NTAwMTM5fQ.eyJ1c2VybmFtZSI6InN1c2FuIn0.-vK1HJ4jskJtC1HZGppCF6Gq_LyyMvrhY8yv9BzS__LWE3d_PyzWIY_vR-1ciqK8GPrYxzSKu90CdjXcOx6h_A" http://localhost:8888/
Hello, susan!%

# 对http://localhost:8888/ 跟路径进行get有正常返回
```

### 2. 现在的问题

无法将token验证加入weather.clf模块中，没有找到好的办法。但是，找到了一个相关的文章：https://www.jianshu.com/p/6088c36f2c88