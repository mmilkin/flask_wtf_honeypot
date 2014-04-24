flask-wtf-honeypot
==================

  HoneyPot Flask WTForms extention
  
  To use the HoneyPotField the flask configuration must contain the following unique key 
    WTF_HONEY_POT_PRIVATE_KEY
  
  By default the expires time for a user to complete the form is 300 seconds to configure this set the following key
    WTF_HONEY_POT_TIMEOUT=500


Developing
----------

### Get it running
- git clone https://github.com/mmilkin/flask-wtf-honeypot.git
- virtualenv --system-site-packages venv #  to use a system pygst
- . env/bin/activate
- pip install -r requirements.txt
- pip install -r dev-requirements.txt

### Running tests
- nosetests

