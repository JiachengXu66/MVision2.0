FROM node:lts-bookworm as node
RUN mkdir -p /app
WORKDIR /app
COPY package-lock.json /app/
COPY package.json /app/
RUN npm install --verbose
COPY . /app
EXPOSE 4200/tcp
CMD ["npm", "start", "--", "--host", "0.0.0.0", "--poll", "500"]