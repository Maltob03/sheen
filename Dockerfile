# Sheen: a static web app served by nginx running as a non-root user.
FROM nginxinc/nginx-unprivileged:1.27-alpine

LABEL org.opencontainers.image.title="Sheen" \
      org.opencontainers.image.description="Beautiful code images in the color themes that ship with Xcode." \
      org.opencontainers.image.source="https://github.com/Maltob03/sheen" \
      org.opencontainers.image.licenses="MIT"

COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY nginx/headers.conf /etc/nginx/snippets/headers.conf
COPY app/ /usr/share/nginx/html/

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD wget -q -O /dev/null http://127.0.0.1:8080/healthz || exit 1
