# Manual Setup Instructions

## Prerequisites
- **Python**: Ensure that you have Python version 3.10.11 installed. You can download it from the [official Python website](https://www.python.org/downloads/release/python-31011/).

- **Git**: You'll need Git installed to clone the repository. You can download it from [Git's official website](https://git-scm.com/).

## Step 1: Clone the Repository
```bash
git clone https://github.com/himanshumahajan138/ReVocalize.git
cd ReVocalize
```

## Step 2: Create a Virtual Environment
We will use `virtualenv` to create an isolated environment for the project. This step ensures consistency across different devices and operating systems.

1. **Install virtualenv**:
   ```bash
   pip install virtualenv
   ```

2. **Create a virtual environment**:
   ```bash
   virtualenv venv -p python3.10
   ```

3. **Activate the virtual environment**:

   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```

   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

## Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 4: Install the Audio Cloner Package
1. Navigate to the audio cloner code directory:
   ```bash
   cd code/audio_cloner
   ```

2. Install the package in editable mode:
   ```bash
   pip install -e .
   ```

## Step 5: Run the Main Script
Navigate back to the root project directory:
```bash
cd ../../
```

Run the main script:
```bash
python code/main.py
```

## Additional Resources
- [Python Installation Guide](https://www.python.org/downloads/)
- [Git Installation Guide](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [Virtualenv Documentation](https://virtualenv.pypa.io/)

---

If you encounter any issues, please consult the respective official documentation for the tools or feel free to raise an issue in the repository.
