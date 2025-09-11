import uvicorn

def repetition_app1_run():
    # запуск из терменала: python runn_apps.py
    uvicorn.run("REPETITION.APP1.main:app", host="127.0.0.1",port=8000, reload=True)

if __name__ == "__main__":
    repetition_app1_run()