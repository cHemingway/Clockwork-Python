#! /usr/bin/python
'''
clockwork.py
A simple API to ClockworkSMS
requires Requests
'''

import requests
from decimal import Decimal
import collections

class ClockworkException(Exception):
    '''
    Exception for invalid API calls to ClockworkSMS
    
    fields:
        errstring: The error string returned from the HTTP API
        errno:     The error number
        msg:       The error message
    '''
    def __init__(self, errmsg):
        self.errstring = errmsg.rstrip() #Remove trailing newline 
        parts = errmsg.split(":") #Seperate into parts
        self.errno = parts[0].split()[1] #Errno is number in first half
        self.msg = parts[1].lstrip() #msg is the string after the colon

    def __str__(self):
        return self.errstring

class ClockworkMessageException(ClockworkException):
    '''
    Exception for invalid number, message etc.
    Inherits from ClockworkException

    fields:
        number:     The number that message delivery failed to (string)
        Other fields are inherited from Clockwork Exception
    '''
    def __init__(self, errmsg):
        #Add the number variable as well
        #This is ugly, as we cant rely on it actually being a number
        i = errmsg.index(":") #This is straight after to
        self.number = errmsg.split(":")[1].split()[0]
        #Now, remove the phone number and "To:"
        i = errmsg.index("Error")
        super(ClockworkMessageException,self).__init__(errmsg[i:])
        self.errstring = errmsg #Hack to get the full error string back
        

class Clockwork(object):
	
    '''Clockwork(): An interface to the ClockworkSMS API'''

    def __init__(self,apikey,timeout=None):
        '''Creates a new Clockwork object 

        parameters:
            apikey:     Your API Key for ClockworkSMS
            timeout:    Timeout value in seconds (optional)
        '''
        self.apikey = apikey
        self.r = requests.Response()
        if timeout:
            self.timeout = timeout
        else:
            self.timeout = 1 #1 second seems alright


    def send(self,to,message,_from=None,_long=0):
        '''Send a message to given international number/s.
        
        parameters:
            to:         Either a string or iteration for multiple numbers
            message:    The message to send.
            _from:      A string of the "From" section. (optional)
            _long:      If the message is greater than 160 characters (optional)

        exceptions:
            ClockworkException
            ClockworkNumberException
        '''
        #Try and unpack list of "to" numbers, if we are given them
        if not isinstance(to, basestring):
            to = ",".join(to)
        payload = {
                'key':self.apikey,
                'to' :to,
                'content':unicode(message),
                'long':_long,
                }

        if _from:
            payload['from']=_from
        self.r = requests.get("https://api.clockworksms.com/http/send.aspx",
                              params=payload,
                              timeout=self.timeout)

        #Raise an error if failed HTTP request
        self.r.raise_for_status()
        #Raise an error on API failure
        for line  in self.r.text.splitlines():
            if "Error" in line:
                if "To:" in line:
                    raise ClockworkMessageException(line)
                else:
                    raise ClockworkException(line)
                

    def check_balance(self):
        '''Function to return balance amount and 3 letter currency code
        
        returns :
            Balance, a namedtuple() with fields:
            amount:     The decimal value of the balance
            currency:   A string of the name of currency, e.g. "GBP" or "USD"

        exceptions:
            ClockworkException
        '''
        payload= {'key':self.apikey}
        self.r = requests.get("https://api.clockworksms.com/http/balance",
                               params=payload,
                               timeout=self.timeout)
       
        self.r.raise_for_status()
        if "Error" in self.r.text:
            raise ClockworkException(self.r.text)

        #Now parse the response for the number, and get it
        _, amount, cur = [t(s) for t,s in zip(
                                (str,Decimal,str),
                                self.r.text.split()
                                )]
        #Strip brackets from currency field
        cur = cur.strip("()")
        balance = collections.namedtuple('Balance', ['amount','currency'])
        return balance(amount,cur)
