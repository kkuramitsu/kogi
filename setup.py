from setuptools import setup, find_packages


def _requires_from_file(filename):
    return open(filename).read().splitlines()


setup(name="kogi",
      version="0.1",
      description="Kogi Programming AI",
      url="https://github.com/kkuramitsu/kogi",
      packages=find_packages("src"),
      package_dir={"": "src"},
      package_data={'kogi': ['data/*.txt']},
      install_requires=_requires_from_file('requirements.txt'),
      )
