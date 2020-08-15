return_dict = {
    "sucess": {
        "code": 200, 
        "message": "SUCCESS",
    },
    # 参数格式有误
    "format_error": {
        "code": 500,
        "message": "PARAM FORMATE ERROR.",
        "Warning": ["参数格式有误"]
    },
    # 缺少参数
    "missing_para": {
        "code": 500,
        "message": "MISSING PARAM.",
        "Warning": ["缺少必要参数"]
    }
}