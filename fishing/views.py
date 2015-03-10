import os
import jinja2
import json
import hashlib
import dateutil.parser
import urllib

from flask import (
    Flask,
    request,
    redirect,
    render_template,
    url_for,
    session,
    flash,
    abort,
    current_app
)

from flask.json import JSONEncoder
from flask_oauthlib.client import OAuth, OAuthException

from fishing.forms import LicenceTypeForm, PaymentForm
from fishing.order import Order

from fishing import (
    app,
    oauth,
    locator
)


registry = oauth.remote_app(
    'registry',
    consumer_key=app.config['REGISTRY_CONSUMER_KEY'],
    consumer_secret=app.config['REGISTRY_CONSUMER_SECRET'],
    request_token_params={'scope': 'person:view licence:view licence:add'},
    base_url=app.config['REGISTRY_BASE_URL'],
    request_token_url=None,
    access_token_method='POST',
    access_token_url='%s/oauth/token' % app.config['REGISTRY_BASE_URL'],
    authorize_url='%s/oauth/authorize' % app.config['REGISTRY_BASE_URL']
)

#filters
@app.template_filter('reference_number')
def reference_number_filter(s):
    split = s.split('/')
    return split[-1].upper()

@app.template_filter('format_money')
def format_money_filter(value):
    return "{:,.2f}".format(value)

@app.template_filter('format_date_time')
def format_date_time_filter(value):
    date = dateutil.parser.parse(value)
    return date.strftime('%A %d %B %Y %H:%M')


@app.template_filter('pad_reference')
def pad_reference(s):
    n = 4
    result = [s[i:i+n] for i in range(0, len(s), n)]
    return " ".join(result)

#auth helper
@registry.tokengetter
def get_registers_oauth_token():
    return session.get('registry_token')

#views
@app.route("/")
def index():
    return redirect("%s/fishing" % app.config['WWW_BASE_URL'])

@app.route("/buy")
def buy():
    session.clear()
    return redirect(url_for('choose_type'))

@app.route("/choose-type", methods=['GET', 'POST'])
def choose_type():

    if not session.get('registry_token', False):
        session['resume_url'] = 'choose_type'
        return redirect(url_for('verify'))

    locator.send_message({"active": "fishing"})

    order = None
    order_data = session.get('order', None)
    if order_data:
        order = Order.from_dict(order_data)
    else:
        #get the person associated with this token
        about = registry.get('/about').data
        person = registry.get(about['person'].replace(registry.base_url, '')).data
        #existing_licences = registry.get('/licences').data
        existing_licences = None
        disabled = False
        order = Order(dateutil.parser.parse(person['born_at']), existing_licences, disabled, app.config['BASE_URL'])
        session['order'] = order.to_dict()

    form = LicenceTypeForm(request.form)

    if request.method == 'POST':
        if form.validate():
            order.licence_type = form.licence_type.data
            order.duration = form.duration.data
            order.starts_at = None
            session['order'] = order.to_dict()
            return_uri = '%s%s' % (app.config['BASE_URL'], url_for('complete_order'))
            payment_url = '%s/start?%s' % (
                app.config['PAYMENT_URL'],
                urllib.parse.urlencode(
                    {'total': order.calculate_total(),
                    'description': '%s licence - %s' % (order.licence_name(), order.duration),
                    'service': 'Fishing service - Department for the Environment',
                    'return_uri': return_uri}))  # ouch

            return redirect(payment_url)

    return render_template('buy.html', order=order, form=form)

@app.route("/pay", methods=["GET", "POST"])
def pay():

    order_data = session.get('order', None)
    if order_data:
        order = Order.from_dict(order_data)
    else:
        return redirect(url_for('index'))

    #form
    form = PaymentForm(request.form)

    if request.method == 'POST':
        if form.validate():
            data = {
                'type_uri': order.licence_type_uri(),
                'licence_type': order.licence_type,
                'starts_at': '2013-01-01',
                'ends_at': '2015-01-01'
                }

            current_app.logger.debug('posting to registry %s' % data)

            response = registry.post('/licences', data=data, format='json')
            if response.status == 201:
                flash('Your new licence has been granted', 'success')
                session.pop('order', None)
                return redirect(url_for('your_licences'))
            else:
                flash('Something went wrong', 'error')
    return render_template('pay.html', order=order, form=form)



@app.route("/complete-order", methods=["GET"])
def complete_order():
    order_data = session.get('order', None)
    if order_data:
        order = Order.from_dict(order_data)
    else:
        return redirect(url_for('index'))

    data = {
        'type_uri': order.licence_type_uri(),
        'licence_type': order.licence_type,
        'starts_at': '2013-01-01',
        'ends_at': '2015-01-01'
    }

    response = registry.post('/licences', data=data, format='json')
    if response.status == 201:
        flash('Your new licence has been granted', 'success')
        session.pop('order', None)
    else:
        flash('Something went wrong', 'error')

    return redirect(url_for('your_licences'))


@app.route("/your-licences")
def your_licences():

    if not session.get('registry_token', False):
        session['resume_url'] = 'your_licences'
        return redirect(url_for('verify'))

    locator.send_message({"active": "fishing"})

    licences = registry.get('/licences').data
    return render_template('your-licences.html', licences=licences)

@app.route("/licences")
def licences():
    return render_template('licences.html')

@app.route("/licences/salmon-trout")
def licence_salmon_trout():
    return render_template('salmon-trout.html')

@app.route("/licences/coarse")
def coarse():
    return render_template('coarse.html')

@app.route("/licences/thames")
def thames():
    return render_template('thames.html')

@app.route("/check")
def check():
    return render_template('check.html')

@app.route("/check/result")
def check_result():
    if not session.get('registry_token', False):
        return redirect(url_for('verify'))

    search = request.args.get('q', False)
    if not search:
        abort(404)

    result = registry.get('/licences/%s' % search.replace(' ', ''))
    licence = None
    if not result.status == 200 and result.status != 404:
        abort(result.status)
    if result.status == 200:
        licence = result.data

    return render_template('check-result.html', licence=licence)

@app.route('/verify')
def verify():
    _scheme = 'https'
    if os.environ.get('OAUTHLIB_INSECURE_TRANSPORT', False) == 'true':
        _scheme = 'http'

    return registry.authorize(callback=url_for('verified', _scheme=_scheme, _external=True))

@app.route('/verified')
def verified():
    resp = registry.authorized_response()

    if resp is None or isinstance(resp, OAuthException):
        return 'Access denied: reason=%s error=%s' % (
        request.args['error_reason'],
        request.args['error_description']
        )

    session['registry_token'] = (resp['access_token'], '')
    session['refresh_token'] = resp['refresh_token']
    if session.get('resume_url'):
        return redirect(url_for(session.get('resume_url')))
    else:
        return redirect(url_for('index'))


