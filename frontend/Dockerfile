FROM node:22
WORKDIR /app
# copy package.json from build context (frontend directory) and install deps
COPY package.json ./package.json
RUN npm install
# copy the rest of the frontend source into the image
COPY . ./
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
