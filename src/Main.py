import os
import connexion

app = connexion.App(__name__, specification_dir='./')
app.add_api('swagger.yml')

if __name__ == '__main__':
    dbg = os.environ.get('APP_DEBUG') == '1'
    app.run(debug=dbg)