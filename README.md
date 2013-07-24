Clockwork-Python
================

A simple unofficial python interface to the [ClockworkSMS](http://www.clockworksms.com/) HTTP API.

Does not support callbacks, so is for sending and balance checking only.

Currently **ALPHA** standard code, do not use for production etc

## Documentation
See ``>>>help(clockwork)` for full details``

## Usage

### Send an SMS message to one number

    from clockwork import Clockwork
    c = Clockwork('API_KEY')
    c.send('number','your message')

### Send the same SMS message to multiple numbers

    from clockwork import Clockwork
    c = Clockwork('API_KEY')
    numbers = ["111111","222222","333333"]
    c.send(numbers,'your message')

### Check your current balance

    from clockwork import Clockwork
    c = Clockwork('API_KEY')
    balance = c.check_balance()
    balance.amount 		##>>Decimal(8.39)
    balance.currency		##'GBP'

##License
This project is licensed under the MIT open source license.
See LICENSE for details.
