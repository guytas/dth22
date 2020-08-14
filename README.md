# dth22
DTH22 humidity sensor tiny app

Just copy both files (humidity.py and readtempDTH22.py on the same directory
and execute humidity.py in python.  The Readtemp() argument is the GPIO number
you are using. I was using 18.

I'm fairly new at programming in Python, linux and on a Raspberry Pi.  Not
sure if this is done by the book but it seems to be working.

I wish I could disable the pi interrupt while I read from the DTH22 because
the timing seems to be quite sensitive.

The temp() function could have an argument:

retry=n

by default, it is set to 3

