from flask import Flask, render_template
#import flask
import datetime
app = Flask(__name__)
@app.route("/")
def hello():
   now = datetime.datetime.now()
   timeString = now.strftime("%Y-%m-%d %H:%M%S")
   templateData = {
      'title' : 'HELLO!',
      'time': timeString
      }
   return render_template('webdata.html', **templateData)
if __name__ == "__main__":
   app.run(host='192.168.207.123', port=80, debug=True)
