# frontend Dockerfile placeholder
FROM node:18-alpine
WORKDIR /app
COPY . /app
RUN npm ci && npm run build
CMD ["npm","run","preview"]
