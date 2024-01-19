import subprocess


def install_missing_libraries():
    libraries = [
        'multiprocessing',
        'numpy',
        'tqdm',
        'configparser',
        'pickle',
        'os',
        'shutil',
        'sys',
        'time'
    ]

    for library in libraries:
        try:
            __import__(library)
        except ImportError:
            print(f"{library} kütüphanesi eksik. Yükleniyor...")
            subprocess.call(['pip', 'install', library])
            print(f"{library} kütüphanesi başarıyla yüklendi.")


if __name__ == "__main__":
    install_missing_libraries()
