"""
This script runs the FlaskWebProject application using a development server.
"""
# modified by C. Pigiotis
import ssl
from os import environ
from FlaskWebProject import app

# context is contained the ssl certificates
# ssl certificates are stored in the same directory
# as this file. Certificates are self signed by me.
# Might cause authentication problems
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain('ssl.cert', 'ssl.key')


if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT, threaded=True, ssl_context=context)
