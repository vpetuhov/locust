from locust import task, SequentialTaskSet, FastHttpUser, HttpUser, constant_pacing, events
from config.config import cfg, logger
import sys, re
from utils.assertion import check_http_response
from utils.non_test_methods import open_csv_field
import random


class PurchaseFlightTicket(SequentialTaskSet): # класс с задачами (содержит основной сценарий)

    test_users_csv_file_path = './test_data/user_data_test.csv'
    def on_start(self) -> None:

        self.test_users_data = open_csv_field(self.test_users_csv_file_path)

        @task
        def uc_01_getHomePage(self) -> None:
            self.client.get(
                '/WebTours',
                name='REQ_01_1_/WebTours/',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'accept-Encoding': 'gzip, deflate, br, zstd'
                },
                # debug_stream = sys.stderr
            )

            self.client.get(
                '/cgi-bin/welcome.pl?signOff=1',
                name='REQ_01_2_/cgi-bin/welcome.pl?signOff=1',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'accept-Encoding': 'gzip, deflate, br, zstd'
                },
                allow_redirects=False,
                #debug_stream = sys.stderr
            )

            with self.client.get(
                '/cgi-bin/nav.pl?in=home',
                name='REQ_01_3_/cgi-bin/nav.pl?in=home',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'accept-Encoding': 'gzip, deflate, br, zstd'
                },
                allow_redirects=False,
                catch_response=True,
                #debug_stream = sys.stderr
            ) as req_01_3_response:
                check_http_response(req_01_3_response, param_to_check="name=\"userSession\"")
            self.userSession = re.search(r'name=\"userSession\" value=\"(.*)\"/>', req_01_3_response.text).group(1)

        @task
        def uc_02_getLlogin(self) -> None:
            self.user_data_row = random.choice(self.test_users_data)
            userName = self.user_data_row['username']
            password = self.user_data_row['password']
            req_body_02_01 = f'userSession={self.userSession}&username={userName}&password={password}&login.x=42&login.y=5&JSFormSubmit=off'

            with self.client.post(
                '/cgi-bin/login.pl',
                name='REQ_02_1_/cgi-bin/login.pl/',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'accept-Encoding': 'gzip, deflate, br, zstd',
                    'content-type': 'application/x-www-form-urlencoded'
                },
                data=req_body_02_01,
                catch_response=True,
                debug_stream = sys.stderr
            ) as req_02_1_response:
                check_http_response(req_02_1_response, param_to_check="User password was correct")

            self.client.get(
                '/cgi-bin/nav.pl?page=menu&in=home',
                name='REQ_02_2_/cgi-bin/nav.pl?page=menu&in=home',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'accept-Encoding': 'gzip, deflate, br, zstd'
                },
                allow_redirects=False,
                # debug_stream = sys.stderr
            )

            with self.client.get(
                    '/cgi-bin/login.pl?intro=true',
                    name='REQ_02_3_/cgi-bin/login.pl?intro=true',
                    headers={
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'accept-Encoding': 'gzip, deflate, br, zstd'
                    },
                    allow_redirects=False,
                    catch_response=True,
                    debug_stream=sys.stderr
            ) as req_02_3_response:
                check_http_response(req_02_3_response, param_to_check=f"Welcome, <b>{userName}</b>, to the Web Tours reservation pages.")

        uc_01_getHomePage(self)
        uc_02_getLlogin(self)

    @task
    def fixTest(self):
        pass

class WebToursBaseUserClass(FastHttpUser): # юзер-класс, принимающий в себя основные параметры теста
    wait_time = constant_pacing(cfg.pacing)
    host = cfg.url

    logger.info(f'WebToursBaseClass started. Host: {host}')
    tasks = [PurchaseFlightTicket]