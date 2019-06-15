FROM arm32v6/nginx:alpine

# Copy in config and build files
COPY nginx.conf /etc/nginx/nginx.conf
COPY build/ /app/webapp/
