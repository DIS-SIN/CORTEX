FROM python:3.7-slim-stretch

ENV CHROME_DRIVER_VERSION 2.42
ENV CHROME_DRIVER_TARBALL http://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip

RUN apt-get update \
    && apt-get install -y --no-install-recommends gnupg dirmngr wget ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && wget -q -O- https://dl.google.com/linux/linux_signing_key.pub | apt-key add -  \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends python3-dev python3-pip xvfb libfontconfig libfreetype6 xfonts-scalable fonts-liberation fonts-noto-cjk google-chrome-stable \
    && wget -qO- $CHROME_DRIVER_TARBALL | zcat > /usr/local/bin/chromedriver \
    && chown root:root /usr/local/bin/chromedriver \
    && chmod 0755 /usr/local/bin/chromedriver \
    && pip3 install --no-cache-dir six==1.11.0 requests unittest-xml-reporting nose mockito pyshould behave selenium==2.48.0 elementium capybara-py xvfbwrapper allure-behave\
    && rm -rf /var/lib/apt/lists/*

ENV PATH /usr/lib/chromium/:$PATH

WORKDIR    /behave
ENV        REQUIREMENTS_PATH  /behave/features/steps/requirements.txt

COPY       run_loki.sh  /bin
ENTRYPOINT ["/bin/run_loki.sh"]
