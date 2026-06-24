from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    # Render the DevOps-themed index page
    return render_template('index.html')

@app.route('/health')
def health():
    # Return a simple JSON status (HTTP 200 for healthy)
    return jsonify(status='healthy'), 200

if __name__ == '__main__':
    app.run(debug=True)


"""from	flask	import	Flask

app	=	Flask(__name__)
@app.route("/")
def	home():
  return	"Hello	from	the	CI/CD	pipeline!	Version	2.0"

@app.route("/health")
def	health():
  return	{"status":	"healthy"},	200
  
if	__name__	==	"__main__":
  app.run(host="0.0.0.0",	port=5000)
"""
