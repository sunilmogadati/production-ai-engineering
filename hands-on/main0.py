from fastapi import FastAPI


# Demo 0 is the simplest possible FastAPI example in this folder.
app = FastAPI(title="FastAPI Demo 0: Basic Path Parameter")


@app.get("/{id}")
async def welcome(id: int):
    # FastAPI converts the path value to int automatically.
    return {"message": f"Hi, my id is, {id}"}