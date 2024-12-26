FROM ubuntu:20.04

RUN apt-get update && apt-get install -y \
    ffmpeg \
    nginx \
    libnginx-mod-rtmp

COPY nginx.conf /etc/nginx/nginx.conf

CMD ["nginx", "-g", "daemon off;"]
