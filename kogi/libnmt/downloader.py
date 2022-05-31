import os

def download_from_google_drive(file_id, filename='model.zip', model_path = './model', quiet=True):
    os.system('pip install --upgrade gdown')
    import gdown
    url = f'https://drive.google.com/uc?id={file_id}'

    gdown.download(url, file_id, quiet=quiet)
    if file_id.endswith('.zip'):
        os.system(f'rm -rf {model_path}')
        os.system(f'unzip -d {model_path} -j {filename}')

