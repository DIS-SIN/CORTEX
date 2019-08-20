# Loki - a Behaviour Driven Development Test Runner

A `Docker` capable of running both Python `behave` command-line or or headless `Chrome` driven by `Selenium` for BDD tests:

1. Simply create and run the `Docker`:

        docker-compose up

2. Run `loki`:

        run_loki.sh

3. Screenshots of `Chrome` interactions can be viewed in `behave/logs/`

4. `allure` formatted reports can be viewed in `behave/report/` by:
- [install `allure` framework](https://docs.qameta.io/allure/#_installing_a_commandline)

Note: for Linux (e.g. Ubuntu 18.04) you need to download directly from [allure-framework/allure2
](https://dl.bintray.com/qameta/maven/io/qameta/allure/allure-commandline/2.12.1/allure-commandline-2.12.1.zip)

- run `allure` webserver on the `behave/report` directory

        allure serve report

5. Enable `junit`-type report by uncommenting below line in `run_loki.sh`

        exec behave --junit --junit-directory report

- Rebuild the `Docker`

        docker-compose up --build

- The `xml` formatted report is placed in `behave/report/TESTS-google.xml`

### References:
- https://intoli.com/blog/running-selenium-with-headless-chrome/
- https://eshlox.net/2016/11/22/dockerize-behave-selenium-tests
- https://github.com/William-Yeh/docker-behave
