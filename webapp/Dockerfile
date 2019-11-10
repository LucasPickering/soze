# Used for production build only

FROM node:10-alpine as js-builder
WORKDIR /app/webapp
COPY . .
RUN npm install && npm run build && rm build/static/js/*.map

# Copy in config and build files
FROM arm32v6/nginx:alpine
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=js-builder /app/webapp/build/ /app/webapp/
