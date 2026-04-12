# Стадия сборки (нужен для npm install)
FROM node:20-alpine AS builder

WORKDIR /app

COPY ./package*.json ./

RUN npm install

COPY . .

RUN npm run build

# Стадия запуска (минимальный образ)
FROM nginx:stable-alpine

# Копируем только результат сборки (build) из предыдущей стадии
COPY --from=builder /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]