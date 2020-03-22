FlasQuiz!
=========

This is a small but elegant quiz application written in
[Python](https://python.org/) that uses
[Flask](https://palletsprojects.com/p/flask/).
It is meant to be easy to understand for new users of Flask, but not
necessarily optimized for performance or security. It is intended to serve as a
starting point for your own application or it can be used as-is behind a
reverse proxy such as nginx configured to enforce SSL and an access control
list.

It has the following features:
* Define any number of quizzes in [YAML](https://yaml.org/) files
* Identify submitters by e-mail address (without authentication)
* Save submission data in YAML files
* Send submission data via e-mail for submissions with passing scores
* Back button and ability to jump to previously answered questions or return to
  the end of the quiz
* Reset and start a different quiz at any time
* Resume a quiz at any time just by returning to the application (using Flask's
  built-in session feature)
* View score and any incorrect answers on a quiz end screen, with ability to
  display hints and links back to questions answered incorrectly and change the
  user's answer
* Less than 350 lines of Python and less than 200 lines of HTML! (at time of
  writing)

Written by Ryan Helinski <rhelins@sandia.gov>
based loosely on [miniquiz](https://github.com/dldhdz/miniquiz/).

Getting Started
---------------

With a copy of the source code, install the requirements by running
```
pip install -r requirements.txt
```

Then, edit the `config.py` file to suit your needs. If desired, specify the
configuration for sending e-mails from the application.

Next, create a subdirectory called `quizzes` and create one or more `.yml` files
inside it. You may copy one of the files from the `examples` directory to get
started.

Finally, run the application using
```
python app.py
```

If everything is in order, a Flask server should not be running on your computer
and you should be able to point your browser to `http://localhost:5000/`.

License
-------

This software is licensed under the GPL v3.0 license.
See [LICENSE.md](LICENSE.md) for details.  If this file was not included, see
<https://www.gnu.org/licenses/>.

Copyright
---------

Copyright 2020 National Technology & Engineering Solutions of Sandia, LLC
(NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
Government retains certain rights in this software.

SCR#: 2477.0

Disclaimer
----------

Flasquiz is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Flasquiz is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

