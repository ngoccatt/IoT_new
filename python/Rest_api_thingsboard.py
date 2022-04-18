# pip3 install tb-rest-client
import logging
# importing models and REST client class from Community Edition
from tb_rest_client.rest_client_ce import *
# importing the API exception
from tb_rest_client.rest import ApiException

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# Thingsboard REST API URL
url = "https://demo.thingsboard.io"
# Login information
username = "cat.tran03@hcmut.edu.vn"
password = "KiyoKiyo"

res = ""

# Creating the REST client object with context manager to get auto token refresh
with RestClientCE(base_url=url) as rest_client:
    try:
        # Auth with credentials
        rest_client.login(username=username, password=password)

        res = rest_client.delete_entity_attributes("c77cb040-6d33-11ec-8159-03103585248e",
                                             "CLIENT_SCOPE",
                                             "light,humidity,pump,pump1,temperature")
        rest_client.#ctrl+space de thay cac ham duoc hien thuc trong python thay cho cac REST API

    except ApiException as e:
        logging.exception(e)
