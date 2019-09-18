from setuptools import setup

setup(name='jupyterflame',
      version='0.0.1',
      description='Brings flamegraphs into jupyter notebooks',
      url='http://github.com/H4dr1en/jupyterflame',
      author='H4dr1en',
      author_email='h4dr1en@pm.me',
      license='MIT',
      packages=['jupyterflame'],
      zip_safe=False,
      install_requires=['flameprof']
)