from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(name='jupyterflame',
      version='0.0.1',
      description='Brings flamegraphs into jupyter notebooks',
      url='http://github.com/H4dr1en/jupyterflame',
      author='H4dr1en',
      author_email='h4dr1en@pm.me',
      long_description=long_description,
      long_description_content_type="text/markdown",
      license='MIT',
      packages=['jupyterflame'],
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
      ],
      zip_safe=False,
      install_requires=['flameprof']
)