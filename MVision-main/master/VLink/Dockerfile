FROM node:lts-bookworm as node
WORKDIR /app
COPY package*.json ./
COPY ./dist ./
COPY ./config.json ./
RUN npm install
CMD ["node", "."]