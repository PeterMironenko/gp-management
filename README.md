# This document describes GP management Flask backend system

## Installation on local host

**1. Prerequisites:**
- Windows 10 or higher, Linux, or macOS
- Python 3.8 or higher
- Git

**2. Clone the repository**
```bash
git clone https://github.com/PeterMironenko/gp-management.git
```
**3. Got to the project directory**

```bash
cd gp-management
```

**4. Create a virtual environment and activate it**
```bash
python3 -m venv .venv
```
Activate the virtual environment

***On Windows:***
```Powershell
.venv\Scripts\activate
```
***On Linux or macOS:***
```bash
source .venv/bin/activate
```
**5. Install the required dependencies**
```bash
pip install -r requirements.txt
```
**6. Start the Flask application**

***Development mode:***
---

On development mode, you can create sample database with test data by running the following command:

```bash
python seed_random_data.py 
```

**On Windows:**

```Powershell
.\statrt_api_debug.bat 5001
```
**On Linux or macOS:**
```bash
./start_api_debug.sh 5001
```

***Release mode:***
---

**On Windows:**
```Powershell
.\start_api_release.bat 5001
```
**On Linux or macOS:**
```bash
./start_api_release.sh 5001
```

***IMPORTANT:*** 5001 is the port number, if it's not specified, it will be set to default 5000.

### Running Docker container

**1. Prerequisites:**
- Windows 10 or higher, Linux, or macOS
- Git
- Docker

**2. Clone the repository**
```bash
git clone https://github.com/PeterMironenko/gp-management.git
```
Got to the project directory

```bash
cd gp-management
```

**3. Build the Docker image**

```bash
docker compose build
```

**4. Run the Docker container**

```bash
docker compose up -d
```
**5. Check the container is running**

```bash
docker ps
```

You should see the output like this:

```
CONTAINER ID   IMAGE                           COMMAND                  CREATED      STATUS      PORTS                                         NAMES
4bdb3b942a4f   simple-store-app-flask:latest   "flask --app app run…"   6 days ago   Up 6 days   0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp   container-store-app-flask
```