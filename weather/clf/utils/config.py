return_dict = {
    "success": {
        "code": 200,
        "message": "SUCCESS"
    },
    # 参数格式错误
    "format_error": {
        "code": 500,
        "message": "PARAM FORMAT ERROR."
    },
    # 缺少参数
    "missing_param": {
        "code": 500,
        "message": "MISSING NECESSARY PRARM."
    }
}