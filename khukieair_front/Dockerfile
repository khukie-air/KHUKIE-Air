FROM node:10

# Create app directory
WORKDIR /app
ADD . /app/

# global install & update
RUN npm install

ENV HOST 0.0.0.0
EXPOSE 3000

# start command
CMD ["npm", "run", "start"]

# FROM node:lts-alpine as build-stage

# WORKDIR /app

# COPY package*.json ./
# RUN npm install

# COPY . .
# RUN npm run build

# FROM nginx:stable-alpine as production-stage
# RUN rm /etc/nginx/conf.d/default.conf
# COPY ./nginx/homepage.conf /etc/nginx/conf.d/homepage.conf

# COPY --from=build-stage /app/.nuxt /usr/share/nginx/html/homepage
# EXPOSE 80
# CMD ["nginx", "-g", "daemon off;"]