from qr_site import app


app.secret_key = 'i wont a die'
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
    #app.run(debug=True)

