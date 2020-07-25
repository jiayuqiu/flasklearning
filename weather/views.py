from . import app

@app.route('/weather_clf', subdomain='weather')
def weather_clf():
    return 'weather_clf'
