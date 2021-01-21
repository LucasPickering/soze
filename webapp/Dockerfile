# Used for production build only

FROM node:lts-alpine as js-builder
WORKDIR /app/webapp

# Copy just dependency files first, to leverage layer caching
COPY package.json package-lock.json ./
RUN npm install

# Copy everything else and build
COPY . .
RUN npm run build

# Copy in config and build files
FROM nginx:alpine
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=js-builder /app/webapp/build/ /app/webapp/
