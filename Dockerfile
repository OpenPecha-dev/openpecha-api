FROM tiangolo/uvicorn-gunicorn:python3.8

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install calibre deps
RUN : \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    --no-install-recommends \
    libgl1-mesa-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/list/* \
    && :

# install calibre
RUN wget -nv -O- https://download.calibre-ebook.com/linux-installer.sh | sh /dev/stdin
RUN ebook-convert --version

# install monlam fonts
RUN mkdir /usr/share/fonts/truetype/monlam
RUN wget https://github.com/OpenPecha/ebook-template/raw/master/monlam_uni_ouchan2.ttf
RUN mv monlam_uni_ouchan2.ttf /usr/share/fonts/truetype/monlam/


# install python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Copy environment variables
COPY ./.env /app/.env

EXPOSE 80

# add app
COPY ./app /app/app
