# 📦 Install Guide — Hikikimo Life

## Prerequisites
- Python 3.8 or higher
- `pip` package manager (usually comes with Python)
- `git` for cloning the repository
- `unzip` and `wget` (for alternative installation)

---

## 🚀 Recommended Installation (Using Git)

### 1. Update System & Install Dependencies
```bash
apt update && apt upgrade -y
apt install -y python git wget unzip
```

### 2. Clone the Repository

```bash
git clone https://github.com/icedeyes12/hkkm.git
cd hkkm
```

### 3. Install Python Requirements

```bash
# Install pip if not already installed
apt install -y python-pip

# Install required Python packages
pip install requests colorama
```

### 4. Run the Game

```bash
python main.py
```

---

# 📥 Alternative Installation (Direct Download)

## 1. Download and Extract

```bash
wget https://github.com/icedeyes12/hkkm/archive/refs/heads/main.zip -O hkkm.zip
unzip hkkm.zip
cd hkkm-main
```

## 2. Install Python Requirements

```bash
pip install requests colorama
```

## 3. Run the Game

```bash
python main.py
```

---

# 🔧 Troubleshooting

If python doesn't work:

```bash
python3 main.py
```

If pip is not found:

```bash
apt install -y python-pip
```
## or

```bash
apt install -y python3-pip
```

## Permission Issues:

```bash
# Make scripts executable if needed
chmod +x main.py
```

## Missing Dependencies:

```bash
# Install additional requirements if any errors occur
pip install --upgrade pip
```
---

# 📋 Verification

After installation, verify everything works:

```bash
python --version
pip --version
git --version
```

---

# 🆘 Need Help?

Check the [README.md](README.md] for more details or open an issue on the [GitHub Issues page](https://github.com/icedeyes12/hkkm/issues)

---

> Note: This build is mainly for testing and preview — gameplay is still under development 🛠️.
