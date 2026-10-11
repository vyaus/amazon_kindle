# Chinese Kindle Book Library

Flask app for searching and downloading Kindle books.

## Build and deploy

Build the image on the target device, or on a machine with the same CPU architecture:

```sh
docker build -t amazon-kindle-library:latest ./flask
```

Save the image and transfer it to the device:

```sh
docker save -o amazon-kindle-library.tar amazon-kindle-library:latest
rsync -av amazon-kindle-library.tar user@device:/tmp/
```

On the device, edit `docker-compose.yml` and change `./Folder` to the host path containing the AZW3 files. The directory is mounted read-only and is not included in the image. Then load and start the image:

```sh
docker load -i /tmp/amazon-kindle-library.tar
docker compose -f docker-compose.yml up -d
```

Open [http://localhost:12345](http://localhost:12345). Stop the app with `docker compose -f docker-compose.yml down`. The image contains `flask/library.db`; rebuild it after changing that database.






