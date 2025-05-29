from setuptools import setup

# Package configuration
setup(
    name='convert_md',  # Package name
    version='0.1.0',  # Initial version
    author='chientv',  # Replace with your name
    author_email='chient369@gmail.com',  # Replace with your email
    description='Tool to convert document files to Markdown use with cursor ai to search data from document',  # Short description
    long_description=open('README.md', encoding='utf-8').read(),  # Read from README
    long_description_content_type='text/markdown',
    py_modules=['convert_utils', 'convert_cli'],  # Modules to include
    install_requires=[  # Dependencies
        'markitdown',
    ],
    entry_points={  # Command-line entry point
        'console_scripts': [
            'cvmd=convert_cli:main',
        ],
    },
    classifiers=[  # Metadata to categorize the package
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Minimum Python version
) 