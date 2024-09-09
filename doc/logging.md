# Logging

All throttling classes accept two additional arguments to log waiting times:

 * `logger`: this must be a callable. Whenever an object evaluates waiting
   time , it will call it with two parameters: a logging message (a string) and
   the waiting time in seconds as a float number.
   `RateAsyncThrottler` and `TaskSpacer` objects log waiting times _before_ 
   the wait starts, while `ConcurrentAsyncThrottler` logs the final waiting 
   time _after_ wait finishes (and, if using the `run()` method, will log 
   _total execution time_)
   
 * `log_msg` allows specification of the string to be sent as the first
   argument to the logging callable. If not specified, a default will be used
   
   
## Standard logging

To use standard Python logging, just send in the `logger` argument a logging
method from ana instantiated logger, e.g.

     log = logging.getLogger()
	 rt  = AsyncThrottler(rate=2, log=log.info)
	 
This will automatically send log messages to that logger, using INFO
level. The default logging message uses "traditional" logging message syntax
(i.e. `%`-strings) to include the waiting time in the message. If another modality
is needed, just define it in `log_msg`


## Custom handling

Since the `log` parameter is assumed to be just a callable, any other custom
object can be used instead, to perform customized handling of waiting time
information (e.g. to compute average waiting times). It just needs to accept
the two arguments it will be called with (a string and a float).
