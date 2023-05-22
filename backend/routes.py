from api import index

routes_v1 = [
    "v1", ## route prefix
    [
        ["/", [("GET", "POST"), index.index_route]]
    ]
]