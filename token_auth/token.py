#导入依赖包
from flask import request,jsonify,current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

def create_token(api_user):
    '''
    生成token
    :param api_user:用户id
    :return: token
    '''
    
    #第一个参数是内部的私钥，这里写在共用的配置信息里了，如果只是测试可以写死
    #第二个参数是有效期(秒)
    s = Serializer(current_app.config["SECRET_KEY"],expires_in=3600)
    #接收用户id转换与编码
    token = s.dumps({"id":api_user}).decode("ascii")
    return token
