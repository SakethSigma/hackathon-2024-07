from setuptools import setup, find_packages

setup(
    name='ai_vision_service',
    version='0.32',
    packages=find_packages(),
    install_requires=[
        'openai==1.13.3',
        'typing_extensions==4.9.0',
        'tenacity',
        'requests',
        'imageio',
        'simplejson',
        'pillow==10.2.0',
        'python-dotenv',
        'networkx',
        'matplotlib==3.9.0',
        'langgraph',
        'langchain-core',
        'langchain-community',
        'langchain',
        'langchain-openai',
        'python-dotenv',
        'flask-cors'
        # Add any other dependencies here
    ]
)