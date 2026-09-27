# Build da documentacao em container: nao exige Node na maquina.
#
#   docker build -f docs/Dockerfile -t metalmax-docs docs
#   docker run --rm -p 3000:3000 metalmax-docs
#
# O `npm ci --ignore-scripts` e o ponto: nenhum script de instalacao de
# dependencia roda durante o build. A documentacao nao precisa de nenhum.
FROM node:20-alpine

WORKDIR /site

# Dependencias em camada propria: so reinstala se o lockfile mudar.
COPY package.json package-lock.json* ./
RUN npm ci --ignore-scripts --no-audit --no-fund || npm install --ignore-scripts --no-audit --no-fund

COPY . .
RUN npm run build

# Segunda etapa: serve os arquivos estaticos gerados, sem Node no servidor.
FROM nginx:alpine
COPY --from=builder /site/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
