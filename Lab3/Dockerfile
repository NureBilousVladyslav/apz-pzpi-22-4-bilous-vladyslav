# Используем официальный образ Node.js для сборки
FROM node:22 AS build

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем package.json и package-lock.json
COPY package.json package-lock.json ./

# Устанавливаем зависимости
RUN npm install --legacy-peer-deps

# Копируем остальной код приложения
COPY . .

# Собираем приложение для продакшена
RUN npm run build

# Используем Nginx для раздачи собранного приложения
FROM nginx:alpine

# Копируем собранные файлы из предыдущего этапа
COPY --from=build /app/build /usr/share/nginx/html

# Открываем порт 80
EXPOSE 80

# nginx конфигурация
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Запускаем Nginx
CMD ["nginx", "-g", "daemon off;"]