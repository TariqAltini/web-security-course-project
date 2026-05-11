# web security course project

The source code for the website made for the web security course project.

  

## Setup

1. First requirement is having python installed in your system.

You can check if python is installed by running `python --version`, the output should look like this:

```
Python 3.XX.X
```

2. You need git to be installed.

3. If you're using VSCode, you should have the python extension pack installed, especially the python environment extension.

4. Download the repository using your preferred way and open the repository folder in your code editor.

5. In the repository's folder, run the command:

```
python -m venv .venv
```

Then run:

```
./.venv/Scripts/Activate.ps1
```

6. Run:

```
pip install -r requirements.txt
```

7. Build the database
```
python ./manage.py migrate --database default
python ./manage.py migrate --database vulnerable_db
```
8. Fill the database by running these two commands:
```
python ./manage.py loaddata --database default secure-sample.json
python ./manage.py loaddata --database vulnerable_db vulnerable-sample.json
```

9. Check everything is working by running:

```
python manage.py runserver
```

and then visit http://127.0.0.1:8000/secure/ in your browser. You should the see the websites landing page. There shouldn't be any errors.