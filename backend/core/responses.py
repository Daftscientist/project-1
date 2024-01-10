from sanic import json



async def Success(request, data=None, code=200):
    response = json({
        "success": True,
        "result": data,
        "code": code,
        "request_id": str(request.id)
    }, status=code)
    return response

async def DataResponse(request, data=None, code=200):
    response = json({
        "success": True,
        "result": data,
        "code": code,
        "request_id": str(request.id)
    }, status=code)
    return response