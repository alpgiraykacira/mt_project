# --- Aşama 1: Build ---
FROM node:20-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# Build sırasında API URL'i göm (Vite build-time env variable)
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# --- Aşama 2: Serve ---
FROM nginx:1.25-alpine

# Nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Build çıktısını kopyala
COPY --from=builder /app/dist /usr/share/nginx/html

# OpenShift non-root uyumluluk: nginx kullanıcısına yetki ver
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    touch /var/run/nginx.pid && chown nginx:nginx /var/run/nginx.pid

USER nginx

EXPOSE 8081

CMD ["nginx", "-g", "daemon off;"]
