from flask import render_template
import os
import connexion

app = connexion.App(__name__, specification_dir='./')
app.add_api('swagger.yml')

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    dbg = os.environ.get('APP_DEBUG') == '1'
    app.run(host='0.0.0.0', port=5000, debug=dbg, threaded=True)