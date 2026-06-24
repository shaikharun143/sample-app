from flask import Flask

app = Flask(__name__)
@app.route("/")
def home():
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DevOps CI/CD Dashboard</title>

    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: linear-gradient(120deg, #0f2027, #203a43, #2c5364);
            color: white;
            text-align: center;
        }

        .container {
            padding: 60px;
        }

        h1 {
            font-size: 42px;
            animation: fadeIn 2s ease-in-out;
        }

        .card {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 12px;
            display: inline-block;
            margin-top: 20px;
            backdrop-filter: blur(10px);
        }

        button {
            padding: 10px 20px;
            margin-top: 15px;
            border: none;
            border-radius: 8px;
            background: #00c6ff;
            color: white;
            cursor: pointer;
            font-size: 16px;
        }

        #box {
            width: 60px;
            height: 60px;
            background: red;
            margin: 30px auto;
            border-radius: 10px;
            position: relative;
        }

        @keyframes fadeIn {
            from {opacity: 0;}
            to {opacity: 1;}
        }

        .glow {
            text-shadow: 0 0 10px #00c6ff, 0 0 20px #00c6ff;
        }
    </style>
</head>

<body>

<div class="container">
    <h1 class="glow">🚀 DevOps CI/CD Pipeline</h1>

    <p>Flask App running inside Docker with CI/CD support</p>

    <div class="card">
        <h2>Version 2.0</h2>
        <p>Docker • GitHub Actions • AWS Ready</p>

        <button onclick="animateBox()">Run Motion</button>

        <div id="box"></div>
    </div>
</div>

<script>
    function animateBox() {
        let box = document.getElementById("box");

        box.style.transition = "all 1s ease";
        box.style.transform = "translateX(200px) rotate(360deg)";

        setTimeout(() => {
            box.style.transform = "translateX(0px) rotate(0deg)";
        }, 1500);
    }

    console.log("DevOps Dashboard Loaded 🚀");
</script>

</body>
</html>
"""
    return Response(html, mimetype="text/html")

@app.route("/health")
def health():
    return {"status": "healthy"}, 200
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
