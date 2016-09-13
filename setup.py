from setuptools import setup

setup(
    name='configurador',
    version='0.1.0',
    author='Yonatan Romero',
    author_email='yromero@openmailbox.org',
    keywords='netcop configurador',
    packages=['netcop', 'netcop.configurador',
              'netcop.configurador.templates'],
    namespace_packages=['netcop'],
    package_data={
        # Incluir templates de Jinja2
        '': ['*.j2'],
    },
    url='https://github.com/grupo106/configurador',
    description='Realiza la configuracion de parametros del sistema operativo',
    long_description=open('README.md').read(),
    install_requires=[
        'configparser>=3.5.0',
        'Jinja2>=2.8',
    ],
    scripts=["scripts/configurador"],
    test_suite="tests",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: Freely Distributable',
    ]
)
