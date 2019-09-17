import os

import connexion

app = connexion.App(__name__, specification_dir='./')
app.add_api('swagger.yml')

if __name__ == '__main__':
    dbg = os.environ.get('APP_DEBUG') == '1'

    if dbg:
        app.run(debug=dbg, port=8000)
    else:
        app.run(debug=dbg)
