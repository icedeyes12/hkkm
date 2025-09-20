📦 Install Guide — Hikikimo Life

## Prerequisites
- Python 3.8 or higher  
- `pip` package manager (usually comes with Python)  
- `unzip` and `wget` installed on your system  

---

## Setup

**Update and install requirements**  

```bash
apt update && apt upgrade -y
apt install -y python unzip wget
```
Pull and extract

```bash
wget "https://www.dropbox.com/scl/fi/huj2gdilp7tyoguo5telr/hkkm.zip?rlkey=fd544puue5elgez1dyp6qdhcj&st=24jpt4dx&dl=1" -O hkkm.zip && \
unzip hkkm.zip -d hkkm && \
rm hkkm.zip && \
cd hkkm/hkkm
```
Run the game

```bash
python main.py
```

---

Notes

If python doesn’t work, try python3.

This build is mainly for testing and preview — gameplay is still under development 🛠️.