from setuptools import setup, find_packages


def _requires_from_file(filename):
    return open(filename).read().splitlines()


setup(name="corgi",
      version="0.1",
      description="Corgi Programming AI",
      url="https://github.com/kkuramitsu/corgi",
      packages=find_packages("src"),
      package_dir={"": "src"},
      package_data={'corgi': ['data/*.txt']},
      install_requires=_requires_from_file('requirements.txt'),
      )
