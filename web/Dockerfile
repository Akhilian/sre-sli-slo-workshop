FROM node:22-alpine AS build
WORKDIR /web
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginxinc/nginx-unprivileged:alpine
# Correctif de sécurité de zlib pas encore dans l'image de base (relevé par grype) ; à retirer quand elle le contient.
USER root
RUN apk upgrade --no-cache zlib
USER 101
# L'envsubst intégré à l'image remplace ${API_URL} au démarrage.
ENV API_URL=http://api
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /web/dist /usr/share/nginx/html
EXPOSE 8080
