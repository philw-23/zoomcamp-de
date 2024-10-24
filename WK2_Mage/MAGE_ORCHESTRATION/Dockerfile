FROM mageai/mageai:latest

# NOTE: this is empty for now, if we need additional packages we can install them from here
# The mage container comes preloaded with a number of packages
COPY requirements.txt ${USER_CODE_PATH}requirements.txt 

RUN pip3 install -r ${USER_CODE_PATH}requirements.txt