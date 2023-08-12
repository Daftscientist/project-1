from sanic import json



async def Success(request, data=None, code=200):
    response = json({
        "success": True,
        "message": data,
        "code": code,
        "request_id": str(request.id)
    }, status=code)
    return response

async def BadRequest(request, data=None, code=400):
    response = json({
        "success": False,
        "message": data,
        "code": code,
        "request_id": str(request.id)
    }, status=code)
    return response