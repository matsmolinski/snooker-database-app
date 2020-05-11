 
FROM terrillo/python3flask:latest

ENV STATIC_URL /static
ENV STATIC_PATH /webapp/static

# Place your flask application on the server
COPY ./webapp /webapp
WORKDIR /webapp

# Install requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# NGINX setup
COPY ./webapp/nginx.sh /webapp/nginx.sh
RUN chmod +x /webapp/nginx.sh

ENV PYTHONPATH=/webapp

ENTRYPOINT ["/webapp/nginx.sh"]

# Start Server
CMD ["/start.sh"]

EXPOSE 80 443