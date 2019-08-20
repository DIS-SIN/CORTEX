#!/bin/bash

if [ -z "$REQUIREMENTS_PATH" ]; then
    REQUIREMENTS_PATH=features/steps/requirements.txt
fi

if [ -f "$REQUIREMENTS_PATH" ]; then
    pip3 install --no-cache-dir -r $REQUIREMENTS_PATH
fi

### Uncomment if use jUnit reports
# exec behave --junit --junit-directory report
#

### Use this for allure framework report
exec behave -f allure_behave.formatter:AllureFormatter -o report ./features
#