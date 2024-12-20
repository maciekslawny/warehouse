FROM python:3.10

# Ustaw katalog roboczy w kontenerze
WORKDIR /app

# Skopiuj pliki projektu do katalogu roboczego kontenera
COPY . /app/


COPY ./nginx/nginx.conf /etc/nginx/nginx.conf

# Ustaw zmienną środowiskową dla Chrome
ENV CHROME_BIN=/usr/bin/google-chrome

# Pobierz i zainstaluj Chrome w wersji 122
# Skopiuj plik .deb do kontenera
#COPY google-chrome-stable_119.0.6045.199-1_amd64.deb /tmp/

# Zainstaluj Chrome z lokalnego pliku .deb
#RUN apt-get update && apt-get install -y /tmp/google-chrome-stable_119.0.6045.199-1_amd64.deb \
#    && rm /tmp/google-chrome-stable_119.0.6045.199-1_amd64.deb

# Pobierz i zainstaluj ChromeDriver
#RUN LATEST_CHROMEDRIVER=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE) \
#    && wget -q -O /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/119.0.6045.105/linux64/chromedriver-linux64.zip \
#    && unzip /tmp/chromedriver.zip -d /usr/bin/ \
#    && mv /usr/bin/chromedriver-linux64 /usr/bin/chromedriver \
#    && rm /tmp/chromedriver.zip

# Zainstaluj zależności projektu
RUN pip install -r requirements.txt

# Dodaj ścieżkę do ChromeDrivera do zmiennej PATH
#ENV PATH="/usr/bin/chromedriver:${PATH}"

# Dodaj ścieżkę do ChromeDrivera do zmiennej PATH
#ENV PATH="/usr/bin:${PATH}"

# Tworzymy dowiązanie symboliczne do chromedriver-linux64 jako chromedriver
#RUN ln -s /usr/bin/chromedriver-linux64 /usr/bin/chromedriver

# Usuń starszą wersję ChromeDrivera
#RUN rm -rf /root/.cache/selenium/chromedriver/linux64/114.0.5735.90/chromedriver

# Uruchom serwer Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]