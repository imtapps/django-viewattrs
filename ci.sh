#!/bin/bash
#!/bin/bash

# verify user provided a name for the virtualenv
if [ -z "$1" ]; then
    echo "usage: $0 virtual_env_name"
    exit
fi

VIRTUALENV_NAME=$1

virtualenv $VIRTUALENV_NAME
. $VIRTUALENV_NAME/bin/activate

find . -name "*.pyc" -delete
pip install -r requirements/ci.txt

python manage.py test --with-xunit --with-xcover --cover-package=viewattrs
TEST_EXIT=$?
rm -rf jenkins_reports
mkdir jenkins_reports
pep8 viewattrs > jenkins_reports/pep8.report
PEP8_EXIT=$?
pyflakes viewattrs > jenkins_reports/pyflakes.report
PYFLAKES_EXIT=$?
let JENKINS_EXIT="$TEST_EXIT + $PEP8_EXIT + $PYFLAKES_EXIT"
if [ $JENKINS_EXIT -gt 0 ]; then
    echo "Test exit status:" $TEST_EXIT
    echo "PEP8 exit status:" $PEP8_EXIT
    echo "Pyflakes exit status:" $PYFLAKES_EXIT
    echo "Exiting Build with status:" $EXIT
    exit $JENKINS_EXIT
fi
