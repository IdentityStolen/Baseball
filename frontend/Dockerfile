FROM node:18-alpine

WORKDIR /app

# install dependencies
COPY package.json package-lock.json* ./
RUN npm install --no-audit --no-fund

# copy source
COPY . .

ENV CHOKIDAR_USEPOLLING=true
ENV PORT=3000

EXPOSE 3000

CMD ["npm", "start"]

