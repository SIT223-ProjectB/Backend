# SIT223 Asset Tracker
The main flask application for our Asset tracker project for SIT223

## Running it locally on Linux
We are running our application on an Ubuntu 18.04 Image
### Python installation
*Instructions for Ubuntu 18.04*
1. Update packages and install the pre requisites

`sudo apt update && sudo apt install software-properties-common`

2. Add deadsnakes PPA to your sources

`sudo add-apt-repository ppa:deadsnakes/ppa`

3. Install python 3.7 and required header files

`sudo apt install python3.7 python3.7-dev`
4. Installing Python pip

```
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3.7 get-pip.py
```

### Requirements installation 
1. Source the virtual environment

`source env/bin/activate`

2. Install requirements from requirements.txt

`python3.7 -m pip install -r requirements.txt`

If you encounter errors while installing the requirements, make sure you have the appropriate build tools and headers installed for your linux distribution, the error logs should tell you what you're missing.

### Creating the database
In the file `create_db.py` you can modify the default data to be inserted into the DB which also includes the default accounts, Just add a new account or use the two existing active accounts to login. All you have to do to create the database is run this script like `python3.7 create_db.py`

## Running the Asset Tracker
Its as simple as...

`python3.7 run.py`

Now you can vist http://localhost:5000

