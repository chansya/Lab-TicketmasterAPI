from flask import Flask, render_template, request

from pprint import pformat
import os
import requests


app = Flask(__name__)
app.secret_key = 'SECRETSECRETSECRET'

# This configuration option makes the Flask interactive debugger
# more useful (you should remove this line in production though)
app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True


API_KEY = os.environ['TICKETMASTER_KEY']


@app.route('/')
def homepage():
    """Show homepage."""

    return render_template('homepage.html')


@app.route('/afterparty')
def show_afterparty_form():
    """Show event search form"""

    return render_template('search-form.html')


@app.route('/afterparty/search')
def find_afterparties():
    """Search for afterparties on Eventbrite"""

    # Use form data from the user to populate any search parameters
    keyword = request.args.get('keyword', '')
    postalcode = request.args.get('zipcode', '')
    radius = request.args.get('radius', '')
    unit = request.args.get('unit', '')
    sort = request.args.get('sort', '')

    # save the URL of the Events Search endpoint in a variable
    url = 'https://app.ticketmaster.com/discovery/v2/events'
    # format parameters to send with the request as a dictionary
    payload = {'apikey': API_KEY,
               'keyword': keyword,
               'postalCode': postalcode,
               'radius': radius,
               'unit': unit,
               'sort': sort
               }
    # make a GET request by requests.get(), pass in url string and payload dict
    # return a Response obj
    res = requests.get(url, params=payload)
    # we can access the URL of the request
    print(res.url)

    # call the Response.json() method to parse any JSON and return as dictionary
    data = res.json()

    # if there are results found, "_embedded" would be a key in data
    # and we can access the list of events
    if '_embedded' in data:
        events = data['_embedded']['events']
    # if no results found, then set events to empty list
    else:
        events = []

    return render_template('search-results.html',
                           pformat=pformat,
                           data=data,
                           results=events)


# ===========================================================================
# FURTHER STUDY
# ===========================================================================


@app.route('/event/<id>')
def get_event_details(id):
    """View the details of an event."""

    url = f"https://app.ticketmaster.com/discovery/v2/events/{id}"

    payload = {'apikey': API_KEY}

    res = requests.get(url, params=payload)

    event = res.json()

    if '_embedded' in event:
        venues = event['_embedded']['venues']
    else:
        venues = []

    return render_template('event-details.html', event=event, venues=venues)


if __name__ == '__main__':
    app.debug = True

    app.run(host='0.0.0.0')
