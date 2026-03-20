# Comandos Esenciales para Desarrolladores

## Indice

1. [Linux/Ubuntu: Sistema](#1-linuxubuntu-sistema)
2. [Linux/Ubuntu: Archivos y directorios](#2-linuxubuntu-archivos-y-directorios)
3. [Linux/Ubuntu: Permisos y usuarios](#3-linuxubuntu-permisos-y-usuarios)
4. [Linux/Ubuntu: Procesos y red](#4-linuxubuntu-procesos-y-red)
5. [Linux/Ubuntu: Paquetes](#5-linuxubuntu-paquetes)
6. [Git: Lo basico](#6-git-lo-basico)
7. [Git: Ramas y colaboracion](#7-git-ramas-y-colaboracion)
8. [Git: Avanzado](#8-git-avanzado)
9. [Docker: Contenedores](#9-docker-contenedores)
10. [Docker: Imagenes](#10-docker-imagenes)
11. [Docker Compose](#11-docker-compose)
12. [Python y pip](#12-python-y-pip)
13. [SSH y servidores remotos](#13-ssh-y-servidores-remotos)
14. [curl y APIs](#14-curl-y-apis)
15. [jq: procesar JSON](#15-jq-procesar-json)
16. [tmux: multiples terminales](#16-tmux)
17. [Herramientas utiles](#17-herramientas-utiles)
18. [Kubernetes (kubectl)](#18-kubernetes)
19. [GitHub CLI (gh)](#19-github-cli)

---

## 1. Linux/Ubuntu: Sistema

```bash
# Info del sistema
uname -a                    # kernel y arquitectura
lsb_release -a              # version de Ubuntu
hostname                    # nombre del equipo
whoami                      # usuario actual
uptime                      # tiempo encendido
date                        # fecha y hora
cal                         # calendario

# Recursos
free -h                     # RAM usada/libre (human-readable)
df -h                       # disco usado/libre
du -sh carpeta/             # tamano de una carpeta
du -sh * | sort -rh | head  # top 10 archivos/carpetas mas grandes
htop                        # monitor interactivo (CPU, RAM, procesos)
top                         # igual pero mas basico

# Variables de entorno
echo $PATH                  # directorios donde se buscan ejecutables
echo $HOME                  # directorio home
env                         # todas las variables de entorno
export MI_VAR="valor"       # definir variable (solo esta sesion)
# Para permanente, anadir al ~/.bashrc o ~/.zshrc

# Historial
history                     # comandos anteriores
history | grep docker       # buscar en historial
Ctrl+R                      # busqueda inversa (escribes y busca)
!!                          # repetir ultimo comando
sudo !!                     # repetir ultimo comando con sudo
```

---

## 2. Linux/Ubuntu: Archivos y directorios

```bash
# Navegar
pwd                         # donde estoy
cd /ruta/absoluta            # ir a ruta absoluta
cd carpeta/                  # ir a subcarpeta
cd ..                        # subir un nivel
cd ~                         # ir a home
cd -                         # ir al directorio anterior

# Listar
ls                           # listar
ls -la                       # listar todo (ocultos, permisos, tamano)
ls -lh                       # tamanos legibles (KB, MB, GB)
ls -lt                       # ordenar por fecha (mas reciente primero)
ls *.py                      # solo archivos .py

# Crear
mkdir carpeta                # crear directorio
mkdir -p a/b/c               # crear directorios anidados
touch archivo.txt            # crear archivo vacio

# Copiar, mover, borrar
cp archivo.txt copia.txt     # copiar archivo
cp -r carpeta/ backup/       # copiar carpeta (recursivo)
mv archivo.txt nueva_ruta/   # mover (tambien sirve para renombrar)
mv viejo.txt nuevo.txt       # renombrar
rm archivo.txt               # borrar archivo
rm -r carpeta/               # borrar carpeta y contenido
rm -rf carpeta/              # borrar forzado (CUIDADO, sin confirmacion)

# Buscar archivos
find . -name "*.py"              # buscar archivos .py desde aqui
find . -name "*.py" -mtime -7    # modificados en los ultimos 7 dias
find . -size +100M               # archivos mayores a 100MB
find . -type d -name "node_*"    # buscar directorios

# Buscar contenido dentro de archivos
grep "palabra" archivo.txt       # buscar en un archivo
grep -r "palabra" carpeta/       # buscar recursivamente
grep -rn "TODO" src/             # buscar con numero de linea
grep -ri "error" logs/           # case insensitive
grep -rl "import pandas" src/    # solo nombres de archivos que contienen

# Ver contenido
cat archivo.txt              # ver archivo completo
head -20 archivo.txt         # primeras 20 lineas
tail -20 archivo.txt         # ultimas 20 lineas
tail -f log.txt              # seguir archivo en tiempo real (logs)
less archivo.txt             # ver con scroll (q para salir)
wc -l archivo.txt            # contar lineas

# Redirecciones
comando > archivo.txt        # guardar output en archivo (sobreescribe)
comando >> archivo.txt       # guardar output (anade al final)
comando 2> errores.txt       # guardar solo errores
comando > output.txt 2>&1    # guardar todo (output + errores)
comando | otro_comando       # pipe: output de uno como input de otro
ls | wc -l                   # contar archivos en directorio

# Comprimir
tar -czf backup.tar.gz carpeta/       # comprimir
tar -xzf backup.tar.gz                # descomprimir
zip -r backup.zip carpeta/            # crear zip
unzip backup.zip                      # descomprimir zip
```

---

## 3. Linux/Ubuntu: Permisos y usuarios

```bash
# Ver permisos
ls -la
# -rw-r--r-- 1 daniel daniel 1234 Mar 14 12:00 archivo.txt
# drwxr-xr-x 2 daniel daniel 4096 Mar 14 12:00 carpeta/
#
# Formato: [tipo][owner][group][others]
# r=read(4) w=write(2) x=execute(1)
# rw-r--r-- = 644 (owner lee/escribe, otros solo leen)
# rwxr-xr-x = 755 (owner todo, otros leen/ejecutan)

# Cambiar permisos
chmod 755 script.sh          # rwxr-xr-x
chmod 644 config.txt         # rw-r--r--
chmod +x script.sh           # hacer ejecutable
chmod -R 755 carpeta/        # recursivo

# Cambiar propietario
sudo chown daniel:daniel archivo.txt
sudo chown -R daniel:daniel carpeta/

# Ejecutar como admin
sudo comando                 # ejecutar con permisos de root
sudo -i                      # abrir shell como root (salir con exit)
sudo su - usuario            # cambiar a otro usuario
```

---

## 4. Linux/Ubuntu: Procesos y red

```bash
# Procesos
ps aux                       # todos los procesos
ps aux | grep python         # buscar procesos Python
kill 1234                    # matar proceso por PID
kill -9 1234                 # matar forzado
killall python3              # matar todos los procesos python3
jobs                         # procesos en background
bg                           # enviar proceso a background
fg                           # traer proceso a foreground
comando &                    # lanzar en background directamente
nohup comando &              # sigue corriendo aunque cierres terminal

# Red
ip addr                      # ver IPs de tus interfaces
curl ifconfig.me             # tu IP publica
ping google.com              # probar conectividad
ping -c 3 google.com         # solo 3 pings
traceroute google.com        # ruta de red hasta destino

# Puertos
ss -tlnp                     # puertos abiertos (TCP, listening)
sudo lsof -i :8080           # que proceso usa el puerto 8080
sudo netstat -tlnp           # alternativa a ss (mas antiguo)

# Descargar
wget https://url/archivo     # descargar archivo
curl -O https://url/archivo  # descargar archivo con curl
curl -L -o nombre.zip https://url  # descargar con nombre custom

# DNS
nslookup dominio.com         # resolver DNS
dig dominio.com              # info DNS detallada
```

---

## 5. Linux/Ubuntu: Paquetes

```bash
# APT (Ubuntu/Debian)
sudo apt update              # actualizar lista de paquetes
sudo apt upgrade             # actualizar paquetes instalados
sudo apt install paquete     # instalar
sudo apt remove paquete      # desinstalar
sudo apt autoremove          # limpiar paquetes huerfanos
apt search nombre            # buscar paquete
apt list --installed         # listar instalados
dpkg -l | grep nombre        # buscar paquete instalado

# Snap
sudo snap install nombre     # instalar snap
snap list                    # listar snaps instalados

# Utiles que instalar
sudo apt install htop tree jq curl wget net-tools git vim
```

---

## 6. Git: Lo basico

```bash
# Configurar (solo la primera vez)
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
git config --global init.defaultBranch main

# Iniciar
git init                     # iniciar repo nuevo
git clone url                # clonar repo existente
git clone url carpeta        # clonar en carpeta especifica

# Flujo basico
git status                   # ver estado (que cambio)
git add archivo.py           # agregar archivo al staging
git add .                    # agregar todo
git add -p                   # agregar interactivamente (por trozos)
git commit -m "mensaje"      # crear commit
git push                     # subir al remoto
git pull                     # bajar cambios del remoto

# Ver historial
git log                      # historial completo
git log --oneline            # historial compacto (1 linea por commit)
git log --oneline -10        # ultimos 10 commits
git log --graph --oneline    # historial con ramas visuales
git log --author="nombre"    # commits de un autor
git log -p archivo.py        # historial de cambios de un archivo

# Ver cambios
git diff                     # cambios no staged
git diff --staged            # cambios staged (listos para commit)
git diff HEAD~3              # cambios respecto a hace 3 commits
git diff main..feature       # diferencia entre ramas
git show abc1234             # ver un commit especifico

# Deshacer (con cuidado)
git restore archivo.py       # descartar cambios locales de un archivo
git restore --staged arch.py # quitar del staging (unstage)
git commit --amend           # modificar ultimo commit (mensaje o contenido)
git revert abc1234           # crear commit que revierte otro (seguro)
git stash                    # guardar cambios temporalmente
git stash pop                # recuperar cambios guardados
git stash list               # ver stashes guardados
```

---

## 7. Git: Ramas y colaboracion

```bash
# Ramas
git branch                   # listar ramas locales
git branch -a                # listar todas (locales + remotas)
git branch feature-nueva     # crear rama
git checkout feature-nueva   # cambiar a rama
git checkout -b feature-nueva # crear y cambiar (atajo)
git switch feature-nueva     # cambiar (comando moderno)
git switch -c feature-nueva  # crear y cambiar (moderno)
git branch -d rama           # borrar rama (solo si ya fue merged)
git branch -D rama           # borrar rama forzado

# Merge
git checkout main            # ir a la rama destino
git merge feature-nueva      # traer cambios de feature a main
git merge --no-ff feature    # merge con commit (siempre crea merge commit)

# Rebase (reescribir historial)
git checkout feature
git rebase main              # poner commits de feature encima de main
# Resultado: historial lineal (mas limpio)

# Remoto
git remote -v                # ver remotos configurados
git remote add origin url    # anadir remoto
git fetch                    # descargar cambios sin aplicar
git pull                     # fetch + merge
git pull --rebase            # fetch + rebase (historial mas limpio)
git push -u origin feature   # push rama nueva y configurar tracking
git push origin --delete rama # borrar rama remota

# Pull Requests (desde terminal con gh)
gh pr create --title "titulo" --body "descripcion"
gh pr list                   # listar PRs abiertas
gh pr checkout 123           # bajar una PR para revisarla
gh pr merge 123              # mergear PR

# Tags (versiones)
git tag v1.0.0               # crear tag
git tag -a v1.0.0 -m "msg"   # tag con mensaje
git push origin v1.0.0       # subir tag
git tag -l                   # listar tags
```

---

## 8. Git: Avanzado

```bash
# Blame (quien escribio cada linea)
git blame archivo.py         # ver autor de cada linea
git blame -L 10,20 archivo.py # solo lineas 10-20

# Bisect (encontrar que commit introdujo un bug)
git bisect start
git bisect bad               # commit actual tiene el bug
git bisect good abc1234      # este commit estaba bien
# Git va haciendo checkout y tu dices good/bad hasta encontrar el culpable
git bisect reset             # terminar bisect

# Cherry-pick (traer un commit especifico de otra rama)
git cherry-pick abc1234

# Reflog (historial de TODO lo que hiciste, incluso lo "borrado")
git reflog                   # ver historial
git checkout HEAD@{5}        # volver a un estado anterior

# Clean (borrar archivos no trackeados)
git clean -n                 # preview de que se borraria
git clean -fd                # borrar archivos y directorios no trackeados

# .gitignore
echo "*.pyc" >> .gitignore
echo "__pycache__/" >> .gitignore
echo ".env" >> .gitignore
echo "node_modules/" >> .gitignore
echo "*.log" >> .gitignore
```

---

## 9. Docker: Contenedores

```bash
# Ciclo de vida
docker run imagen                 # crear y arrancar contenedor
docker run -d imagen              # en background (detached)
docker run -it imagen bash        # interactivo con terminal
docker run --name mi-app imagen   # con nombre custom
docker run -p 8080:80 imagen      # mapear puerto host:contenedor
docker run -v /local:/container imagen  # montar volumen
docker run -e VAR=valor imagen    # variable de entorno
docker run --rm imagen            # borrar al parar

# Ejemplo completo
docker run -d \
  --name mi-postgres \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=secret \
  -v pg_data:/var/lib/postgresql/data \
  postgres:16

# Gestionar contenedores
docker ps                    # contenedores corriendo
docker ps -a                 # todos (incluyendo parados)
docker stop nombre           # parar
docker start nombre          # arrancar (ya creado)
docker restart nombre        # reiniciar
docker rm nombre             # borrar (debe estar parado)
docker rm -f nombre          # parar y borrar

# Logs
docker logs nombre           # ver logs
docker logs -f nombre        # seguir logs en tiempo real
docker logs --tail 50 nombre # ultimas 50 lineas
docker logs --since 1h nombre # ultima hora

# Ejecutar comandos dentro
docker exec -it nombre bash         # abrir shell
docker exec nombre ls /app          # ejecutar comando
docker exec -it nombre psql -U user # abrir psql

# Inspeccionar
docker inspect nombre        # toda la info del contenedor (JSON)
docker stats                 # CPU/RAM en tiempo real
docker top nombre            # procesos dentro del contenedor

# Copiar archivos
docker cp nombre:/ruta/archivo ./local    # contenedor → host
docker cp ./local nombre:/ruta/destino    # host → contenedor
```

---

## 10. Docker: Imagenes

```bash
# Listar y buscar
docker images                # imagenes locales
docker search postgres       # buscar en Docker Hub
docker pull imagen:tag       # descargar imagen

# Construir
docker build -t mi-app .                # construir desde Dockerfile
docker build -t mi-app:v2 .             # con tag de version
docker build -t mi-app -f Dockerfile.dev .  # Dockerfile alternativo
docker build --no-cache -t mi-app .     # sin cache

# Dockerfile ejemplo
# FROM python:3.12-slim
# WORKDIR /app
# COPY requirements.txt .
# RUN pip install -r requirements.txt
# COPY . .
# EXPOSE 8000
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Subir a registry
docker login                              # login a Docker Hub
docker tag mi-app usuario/mi-app:v1       # etiquetar
docker push usuario/mi-app:v1             # subir

# Limpiar
docker image rm imagen       # borrar imagen
docker image prune           # borrar imagenes sin usar
docker system prune          # borrar TODO sin usar (imagenes, contenedores, redes)
docker system prune -a       # borrar TODO incluyendo imagenes no usadas
docker system df             # ver espacio usado por Docker
```

---

## 11. Docker Compose

```bash
# Arrancar
docker compose up            # arrancar (con logs en terminal)
docker compose up -d         # arrancar en background
docker compose up -d --build # reconstruir imagenes y arrancar
docker compose up -d servicio # arrancar solo un servicio

# Parar
docker compose down          # parar y borrar contenedores
docker compose down -v       # + borrar volumenes (datos)
docker compose down --rmi all # + borrar imagenes
docker compose stop          # parar sin borrar
docker compose start         # arrancar (previamente parados)
docker compose restart       # reiniciar todo

# Escalar
docker compose up -d --scale worker=5    # 5 instancias de worker

# Logs
docker compose logs          # logs de todos
docker compose logs -f       # seguir en tiempo real
docker compose logs servicio # logs de un servicio
docker compose logs --tail 20 servicio   # ultimas 20 lineas

# Estado
docker compose ps            # estado de servicios
docker compose top           # procesos de cada servicio

# Ejecutar comandos
docker compose exec servicio bash           # shell en servicio
docker compose exec db psql -U user         # comando en servicio
docker compose run --rm servicio comando    # ejecutar en contenedor temporal

# Reconstruir
docker compose build                  # construir imagenes
docker compose build --no-cache       # sin cache
docker compose pull                   # descargar imagenes actualizadas
```

---

## 12. Python y pip

```bash
# Entorno virtual
python3 -m venv .venv              # crear
source .venv/bin/activate          # activar (Linux/Mac)
deactivate                         # desactivar

# pip
pip install paquete                # instalar
pip install paquete==2.1.0         # version especifica
pip install -r requirements.txt    # instalar desde archivo
pip install -e .                   # instalar en modo editable (desarrollo)
pip uninstall paquete              # desinstalar
pip list                           # listar instalados
pip freeze > requirements.txt      # exportar dependencias
pip show paquete                   # info de un paquete
pip install --upgrade paquete      # actualizar

# Ejecutar
python3 script.py                  # ejecutar script
python3 -m modulo                  # ejecutar como modulo
python3 -c "print('hola')"        # ejecutar inline
python3 -m http.server 8000       # servidor web rapido

# Jupyter
jupyter lab                        # abrir Jupyter Lab
jupyter lab --port 9999            # puerto especifico
jupyter notebook                   # Jupyter clasico
jupyter kernelspec list            # kernels disponibles

# Testing
pytest                             # ejecutar tests
pytest -v                          # verbose
pytest tests/test_api.py           # archivo especifico
pytest -k "test_login"             # tests que contengan "login"
pytest --cov=src                   # con cobertura

# Formateo y linting
black archivo.py                   # formatear codigo
ruff check .                       # linter rapido
mypy archivo.py                    # type checking
```

---

## 13. SSH y servidores remotos

```bash
# Conectar
ssh usuario@servidor               # conexion basica
ssh -p 2222 usuario@servidor       # puerto no estandar
ssh -i ~/.ssh/mi_clave usuario@srv # con clave especifica

# Claves SSH
ssh-keygen -t ed25519              # generar par de claves
ssh-copy-id usuario@servidor       # copiar clave publica al servidor
cat ~/.ssh/id_ed25519.pub          # ver tu clave publica

# Copiar archivos
scp archivo.txt usuario@srv:/ruta/ # subir archivo
scp usuario@srv:/ruta/archivo .    # descargar archivo
scp -r carpeta/ usuario@srv:/ruta/ # subir carpeta
rsync -avz carpeta/ usuario@srv:/ruta/  # sincronizar (mas eficiente)

# Tuneles SSH (port forwarding)
ssh -L 8080:localhost:80 usuario@srv   # acceder al puerto 80 del servidor
                                        # como si fuera localhost:8080
ssh -L 5432:db-server:5432 usuario@srv # tunel a una BD a traves del servidor

# Config SSH (~/.ssh/config)
# Host mi-servidor
#   HostName 192.168.1.100
#   User daniel
#   Port 22
#   IdentityFile ~/.ssh/id_ed25519
#
# Luego solo: ssh mi-servidor
```

---

## 14. curl y APIs

```bash
# GET
curl https://api.example.com/users           # GET basico
curl -s https://api.example.com/users        # silencioso (sin progreso)
curl -v https://api.example.com/users        # verbose (headers)
curl -o output.json https://api.example.com  # guardar en archivo

# POST
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Daniel", "email": "d@mail.com"}'

# Con autenticacion
curl -H "Authorization: Bearer TOKEN123" https://api.example.com/me
curl -u usuario:password https://api.example.com/private

# PUT, PATCH, DELETE
curl -X PUT https://api.example.com/users/1 -d '{"name":"Nuevo"}'
curl -X PATCH https://api.example.com/users/1 -d '{"name":"Otro"}'
curl -X DELETE https://api.example.com/users/1

# Subir archivo
curl -X POST https://api.example.com/upload \
  -F "file=@foto.jpg"

# Ver solo headers
curl -I https://google.com

# Seguir redirects
curl -L https://short.url/abc

# Timeout
curl --connect-timeout 5 --max-time 10 https://api.example.com

# Combinacion tipica (API + jq para formatear)
curl -s https://api.example.com/users | jq '.'
```

---

## 15. jq: procesar JSON

```bash
# Instalar
sudo apt install jq

# Formatear JSON
echo '{"a":1,"b":2}' | jq '.'
cat data.json | jq '.'

# Acceder a campos
echo '{"name":"Daniel","age":25}' | jq '.name'        # "Daniel"
echo '{"name":"Daniel","age":25}' | jq '.age'          # 25

# Arrays
echo '[1,2,3]' | jq '.[0]'                             # 1
echo '[1,2,3]' | jq '.[-1]'                            # 3 (ultimo)
echo '[1,2,3]' | jq '. | length'                       # 3

# Objetos en arrays
echo '[{"id":1,"name":"A"},{"id":2,"name":"B"}]' | jq '.[0].name'  # "A"
echo '[{"id":1,"name":"A"},{"id":2,"name":"B"}]' | jq '.[].name'   # todos

# Filtrar
echo '[{"id":1,"active":true},{"id":2,"active":false}]' | \
  jq '.[] | select(.active == true)'

# Transformar
echo '[{"id":1,"name":"A"},{"id":2,"name":"B"}]' | \
  jq '[.[] | {id, nombre: .name}]'

# Uso real con APIs
curl -s https://api.github.com/repos/python/cpython | jq '.stargazers_count'
curl -s https://api.github.com/users/torvalds/repos | jq '.[].name'
```

---

## 16. tmux

```bash
# tmux permite tener multiples terminales en una sesion
# Si se desconecta el SSH, tmux sigue corriendo

# Instalar
sudo apt install tmux

# Sesiones
tmux                          # nueva sesion
tmux new -s nombre            # nueva sesion con nombre
tmux ls                       # listar sesiones
tmux attach -t nombre         # reconectar a sesion
tmux kill-session -t nombre   # matar sesion

# Dentro de tmux (prefijo: Ctrl+B, luego la tecla)
Ctrl+B, D                    # desconectar (detach) sin cerrar
Ctrl+B, C                    # nueva ventana
Ctrl+B, N                    # siguiente ventana
Ctrl+B, P                    # ventana anterior
Ctrl+B, %                    # dividir verticalmente
Ctrl+B, "                    # dividir horizontalmente
Ctrl+B, flecha               # moverse entre paneles
Ctrl+B, X                    # cerrar panel actual
Ctrl+B, [                    # modo scroll (q para salir)

# Uso tipico en servidor remoto:
# 1. ssh servidor
# 2. tmux new -s trabajo
# 3. Lanzar proceso largo
# 4. Ctrl+B, D (desconectar)
# 5. Cerrar SSH tranquilo
# 6. Despues: ssh servidor → tmux attach -t trabajo
# El proceso sigue corriendo
```

---

## 17. Herramientas utiles

```bash
# tree: ver estructura de directorios
sudo apt install tree
tree                          # arbol desde aqui
tree -L 2                     # solo 2 niveles de profundidad
tree -I "node_modules|.venv"  # ignorar carpetas
tree --dirsfirst              # carpetas primero

# watch: ejecutar comando repetidamente
watch -n 2 docker ps          # cada 2 segundos
watch -n 5 "curl -s localhost:8001/metrics | grep total"

# xargs: pasar output como argumentos
find . -name "*.pyc" | xargs rm    # borrar todos los .pyc
cat urls.txt | xargs -I {} curl {} # curl a cada URL

# sed: reemplazar texto
sed -i 's/viejo/nuevo/g' archivo.txt    # reemplazar en archivo
sed -n '10,20p' archivo.txt             # mostrar lineas 10-20

# awk: procesar texto por columnas
ps aux | awk '{print $1, $11}'          # usuario y comando
df -h | awk 'NR>1 {print $5, $6}'      # uso% y mount point

# sort y uniq
cat log.txt | sort | uniq -c | sort -rn  # contar ocurrencias

# tee: escribir a archivo y stdout
comando | tee output.txt     # ver output Y guardarlo

# alias (atajos, poner en ~/.bashrc)
alias ll='ls -lah'
alias gs='git status'
alias dc='docker compose'
alias activate='source .venv/bin/activate'

# Para que los alias persistan:
echo "alias dc='docker compose'" >> ~/.bashrc
source ~/.bashrc
```

---

## 18. Kubernetes (kubectl)

```bash
# Contexto
kubectl config get-contexts          # ver clusters configurados
kubectl config use-context mi-cluster # cambiar de cluster

# Pods (contenedores corriendo)
kubectl get pods                     # listar pods
kubectl get pods -o wide             # con mas info (nodo, IP)
kubectl get pods --all-namespaces    # todos los namespaces
kubectl describe pod nombre          # detalle de un pod
kubectl logs nombre                  # logs de un pod
kubectl logs -f nombre               # seguir logs
kubectl exec -it nombre -- bash      # shell dentro del pod
kubectl delete pod nombre            # borrar pod

# Deployments
kubectl get deployments              # listar deployments
kubectl describe deployment nombre   # detalle
kubectl scale deployment nombre --replicas=5  # escalar
kubectl rollout status deployment nombre      # estado del rollout
kubectl rollout undo deployment nombre        # rollback

# Servicios
kubectl get services                 # listar servicios
kubectl get svc                      # atajo
kubectl port-forward svc/nombre 8080:80  # acceder localmente

# Aplicar configuracion
kubectl apply -f archivo.yaml        # aplicar/actualizar
kubectl delete -f archivo.yaml       # borrar
kubectl get all                      # ver todo
```

---

## 19. GitHub CLI (gh)

```bash
# Instalar
sudo apt install gh
gh auth login                        # autenticarse

# Repos
gh repo create nombre                # crear repo
gh repo clone usuario/repo           # clonar
gh repo view                         # ver info del repo actual

# Issues
gh issue list                        # listar issues
gh issue create --title "Bug"        # crear issue
gh issue view 123                    # ver issue

# Pull Requests
gh pr create --title "Feature X"     # crear PR
gh pr list                           # listar PRs
gh pr checkout 123                   # bajar PR para revisar
gh pr review 123 --approve           # aprobar PR
gh pr merge 123                      # mergear PR
gh pr diff 123                       # ver diff de PR

# Actions (CI/CD)
gh run list                          # ver ejecuciones de CI
gh run view 123                      # detalle de una ejecucion
gh run watch 123                     # seguir en tiempo real

# Releases
gh release create v1.0.0             # crear release
gh release list                      # listar releases
```
