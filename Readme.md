# Chinese Books of Amazon Kindle

## Duplicate

A01100, A01102, A01124, A01129, A01131, A01219, A01220, A01224, A01225, A01229, A01230, A01231, A01233, A01236, A01241, A01245, A01333, A01338, A01339, A01340, A01341, A01342, A01343, A01344, A01345, A01346, A01349, A01350, A01351, A01352, A01353, A01354

## Todo

A00416, A00418, A00646, A04795, A07875, A08970

## Flask Server

I am running this server on Raspberry Pi.

First, use the following command to create library.db from `book_list.txt`:

```sh
cd flask
python create_library.py
```

Then, create and activate the virtual environment:

```sh
mkdir -p ~/venv
python -m venv ~/venv/amazon_kindle
source ~/venv/amazon_kindle/bin/activate
```

Install `Flask` and `gunicorn` and test if the code works:

```sh
pip install Flask gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

If everything works all right, then you can create a Systemd Service file `bookserver.service` in `/etc/systemd/system/`:

```
[Unit]
Description=Gunicorn instance for Flask Book Server
After=network.target

[Service]
User=pi
Group=www-data
WorkingDirectory=/home/pi/book-server/
ExecStart=/home/pi/book-server/venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Finally, enable and start the service:

```sh
sudo systemctl daemon-reload
sudo systemctl start bookserver
sudo systemctl enable bookserver # Enables it to start automatically on boot
```
