# (c) 2016 Douglas Roark (joroark@vt.edu)
# Copy far and wide, intrepid coder.
#
# The following is a simple web server that uses Flask. The user uses the POST
# method to submit a JSON string. The string is then stored in a database
# alongside the SHA-256 hash value of the string. The user can then use the GET
# function to retrieve the string from the DB using the SHA-256 hash value.
#
# There are various assumptions, explicit and implicit. See README.md for more
# info.

# Kick me off, and kill me with <CTRL+C> when you're ready.
from webFiles import app, SERVER_PORT
app.run(debug=True, port=SERVER_PORT)
