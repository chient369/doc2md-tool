from setuptools import setup, find_packages
import os

# Read the long description from README.md
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

# Package configuration
setup(
    name='convert_md',  # Package name
    version='0.1.1',    # Updated version
    author='chientv',
    author_email='chient369@gmail.com',
    description='Tool to convert document files to Markdown for use with Cursor AI',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/chient369/doc2md_tool',
    py_modules=['convert_utils', 'convert_cli'],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'markitdown>=0.3.0',
        'requests>=2.25.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'flake8>=3.8.0',
            'mypy>=0.800',
        ],
    },
    entry_points={
        'console_scripts': [
            'cvmd=convert_cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Text Processing :: Markup',
        'Topic :: Utilities',
    ],
    python_requires='>=3.6',
    keywords='markdown, converter, document, pdf, excel, word, pptx, cursor, ai',
) 