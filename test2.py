import sanic
import pydantic

app = sanic.Sanic("backend")

@app.post("/first")
async def first():
    ...

if __name__ == "__main__":
    app.run("localhost", "8080", dev=True)