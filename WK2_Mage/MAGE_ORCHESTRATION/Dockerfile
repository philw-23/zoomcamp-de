FROM mageai/mageai:latest

# NOTE: this is empty for now, we will copy packages installed in mage over later
COPY requirements.txt ${USER_CODE_PATH}requirements.txt 

RUN pip3 install -r ${USER_CODE_PATH}requirements.txt