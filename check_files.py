import os

required_files = [
    'main.py',
    'config.py',
    'requirements.txt',
    'test_data.json',
    'static/demo.html',
    'Procfile',
    'railway.json',
    'runtime.txt',
    'nixpacks.toml',
    '.gitignore',
    'README.md'
]

print("🔍 Checking project structure for Railway deployment...\n")

all_good = True
for file in required_files:
    if os.path.exists(file):
        print(f"✅ {file}")
    else:
        print(f"❌ {file} - MISSING!")
        all_good = False

if all_good:
    print("\n✨ All files ready for deployment!")
    print("\nNext steps:")
    print("1. Create GitHub repository")
    print("2. Push code to GitHub")
    print("3. Connect to Railway")
else:
    print("\n⚠️ Some files are missing. Please create them before deployment.")