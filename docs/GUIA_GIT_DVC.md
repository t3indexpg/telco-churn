# Guía paso a paso: Git (código) + DVC (datos)

Todo en **PowerShell dentro de VSCode** (Terminal → New Terminal). Cada 📸 es un pantallazo para los soportes del reporte.
Usuario de GitHub de ejemplo: `t3indexpg`. Cada integrante usa el suyo.

---

## 0. Preparar la carpeta

1. Descomprime `telco-churn.zip` en `C:\Users\PC\Documents\telco-churn`.
2. En VSCode: **File → Open Folder** y elige `telco-churn`.
3. Instala las dependencias (incluye DVC y el conector S3):
```powershell
cd C:\Users\PC\Documents\telco-churn
pip install -r requirements.txt
dvc --version
```
> El CSV de `data/raw` es el mismo de Kaggle (7.043 filas × 21 columnas). Si prefieren descargarlo directo de Kaggle, reemplácenlo con el mismo nombre antes del paso 2.

---

## 1. Inicializar Git y DVC

```powershell
git init
dvc init
git status
git commit -m "Inicializa repositorio Git y DVC"
```
`dvc init` crea la carpeta `.dvc/` y la deja lista en el staging de Git.
📸 **1. Carpeta con `.git` y `.dvc`**: en el Explorador de Windows, Vista → Mostrar → Elementos ocultos.

---

## 2. Versionar los datos crudos con DVC

```powershell
dvc add data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv
git add data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv.dvc data/raw/.gitignore
git commit -m "Versiona datos crudos con DVC"
```
- Git **no** guarda el CSV. Guarda un archivo `.csv.dvc` con su hash MD5 (`3b0bfab2…`).
- `data/raw/.gitignore` impide que el CSV se suba a GitHub.

📸 **2. Contenido del archivo `.csv.dvc`** (ábrelo en VSCode).

---

## 3. Versionar el código del pipeline

```powershell
git add .gitignore README.md requirements.txt params.yaml dvc.yaml src
git commit -m "Agrega pipeline de preparacion y particion de datos"
```

---

## 4. Ejecutar el pipeline DVC (datos procesados v1)

```powershell
dvc repro
dvc dag
git add dvc.lock data/processed/.gitignore
git commit -m "Ejecuta pipeline DVC: datos limpios y particion 80/20"
```
- `dvc repro` corre `preparar` (limpieza) y `particion` (train/test), y genera `dvc.lock` con los hashes de cada salida.

📸 **3. Salida de `dvc repro` y `dvc dag`**

---

## 5. Configurar el remoto DVC (dónde viven los datos)

Escojan **una** opción.

### Opción A: AWS S3 (recomendada; el curso usa AWS)
1. Entra a **AWS Academy → Learner Lab → Start Lab** y espera a que el punto se ponga verde.
2. Ve a **AWS Details → AWS CLI → Show** y copia el bloque completo de credenciales.
3. Pega el bloque en `C:\Users\PC\.aws\credentials` (si no existe, créalo sin extensión):
```
[default]
aws_access_key_id=...
aws_secret_access_key=...
aws_session_token=...
```
4. En la consola de AWS: **S3 → Create bucket**, nombre único (p. ej. `telco-churn-dvc-t3indexpg`), región `us-east-1`.
5. Configura el remoto y sube los datos:
```powershell
dvc remote add -d s3remote s3://telco-churn-dvc-t3indexpg/dvcstore
git add .dvc/config
git commit -m "Configura remoto DVC en S3"
dvc push
```
> Las credenciales del Learner Lab expiran a las 4 horas. Si `dvc push` responde *ExpiredToken*, vuelve a copiarlas (pasos 2 y 3).

### Opción B: carpeta compartida (Google Drive para escritorio / OneDrive)
```powershell
dvc remote add -d drive "G:\Mi unidad\dvc-telco-churn"
git add .dvc/config
git commit -m "Configura remoto DVC"
dvc push
```
Cada compañero que tenga la carpeta en otra ruta la ajusta sin afectar el repositorio:
`dvc remote modify --local drive url "D:\ruta\de\el\dvc-telco-churn"`

📸 **4. Salida de `dvc push` (`4 files pushed`)** y bucket S3 / carpeta con la estructura `files/md5/...`.

---

## 6. Versionar la exploración de datos

```powershell
git add notebooks reports docs
git commit -m "Exploracion de datos y planteamiento del problema"
git log --oneline
```
📸 **5. `git log --oneline` con todos los commits**

---

## 7. Publicar en GitHub

**Con VSCode (como en el taller 2):** Source Control → **Publish Branch** → **Publish to GitHub public repository** → nombre `telco-churn`.

**Por consola:** crea un repositorio vacío `telco-churn` en github.com (sin README) y luego:
```powershell
git remote add origin https://github.com/t3indexpg/telco-churn.git
git push -u origin main
```
📸 **6. Repositorio en GitHub**: deben aparecer los `.dvc`, `dvc.yaml` y `dvc.lock`, y **no** los CSV.

---

## 8. Demostrar el versionamiento de datos (v2 y regreso a v1)

1. Abre `params.yaml` y cambia `test_size: 0.2` por `test_size: 0.25`. Guarda.
2. Ejecuta:
```powershell
dvc repro
dvc params diff
git add params.yaml dvc.lock
git commit -m "v2: particion 75/25"
dvc push
dvc diff HEAD~1
```
📸 **7. `dvc params diff` y `dvc diff HEAD~1`**: muestran que train/test cambiaron.

3. Regresa a la versión 1 de los datos:
```powershell
git checkout HEAD~1 -- params.yaml dvc.lock
dvc checkout
git commit -m "Regresa a particion 80/20 (v1)"
git push
```
📸 **8. `dvc checkout` restaurando los archivos**

---

## 9. Trabajo en equipo (cada integrante debe tener commits)

**Dueño del repo:** GitHub → Settings → Collaborators → **Add people** (agrega a cada compañero).
Si usan S3, entrégale a cada compañero el nombre del bucket. Cada uno usa sus propias credenciales del Learner Lab, o el dueño comparte las suyas en privado.

**Cada compañero:**
```powershell
git clone https://github.com/t3indexpg/telco-churn.git
cd telco-churn
pip install -r requirements.txt
dvc pull
dvc status
git checkout -b nombre-tarea      # ej. ana-maqueta, juan-eda-servicios
# ... trabajar, luego:
git add .
git commit -m "Descripcion del aporte"
git push -u origin nombre-tarea
```
Luego, en GitHub: **Compare & pull request → Create → Merge**.
📸 **9. `dvc pull` en el equipo de un compañero** y **10. Pull Request aprobado**.

Reparto sugerido de ramas: `eda-demograficas`, `eda-servicios-facturacion`, `maqueta-tablero`, `documento-problema`.

---

## Comandos de referencia

| Acción | Comando |
|---|---|
| Ver estado de datos | `dvc status` |
| Ver pipeline | `dvc dag` |
| Re-ejecutar lo que cambió | `dvc repro` |
| Subir datos | `dvc push` |
| Bajar datos | `dvc pull` |
| Ver remotos | `dvc remote list` |
| Restaurar datos de un commit | `git checkout <commit> -- dvc.lock` y luego `dvc checkout` |
