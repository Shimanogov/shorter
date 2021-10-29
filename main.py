from fastapi import FastAPI

if __name__ == "__main__":

    app = FastAPI()


    @app.get("/")
    def read_root():
        return {"Hello": "World"}
