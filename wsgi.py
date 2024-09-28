from defiback import getApp

app = getApp()

if __name__ == "__main__":
    app.run(use_reloader=False, threaded=True)